# Author / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
"""Conservative, read-only cloud observations; never starts or restarts services.

Contract: local readyz is not a cloud or web acceptance test. Error counters are
partitioned by error_kind in tunnel-client. A counter pair cannot order
success and failure within one scrape; that case remains unknown until a later
unambiguous success. No raw logs, URLs, account IDs or error messages escape here.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

FRESH_WINDOW_SECONDS = 90
MAX_METRICS_BYTES = 2_000_000
MAX_LOG_BYTES = 262_144
LAST = "commands_poll_last_successful_timestamp_seconds"
ERRORS = "commands_poll_errors_total"
_SCOPE = {"otel_scope_name", "otel_scope_version", "otel_scope_schema_url"}
_LINE = re.compile(r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{(.*)\})?\s+(\S+)\s*$')
_LABEL = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:[^"\\]|\\[\\"n])*)"(?:,|$)')


class MetricsError(ValueError):
    """Contains only a fixed, non-secret reason code."""


def _labels(text: str | None) -> tuple:
    if not text:
        return ()
    result, pos = {}, 0
    while pos < len(text):
        match = _LABEL.match(text, pos)
        if not match or match[1] in result:
            raise MetricsError("invalid_labels")
        # Decode only the escaping permitted by Prometheus, not arbitrary JSON.
        raw = match[2]
        result[match[1]] = re.sub(r'\\([\\"n])', lambda m: '\n' if m[1] == 'n' else m[1], raw)
        pos = match.end()
    return tuple(sorted(result.items()))


@dataclass(frozen=True)
class Sample:
    last_success: float
    errors: tuple[tuple[tuple, int], ...]

    @property
    def total_errors(self) -> int:
        return sum(value for _, value in self.errors)


def parse_metrics(text: str) -> Sample:
    """Require both metric families, finite nonnegative values and unique series.

    Unknown dimensions fail closed rather than accidentally merging two clients.
    Absence of an error counter is NOT interpreted as zero.
    """
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_METRICS_BYTES:
        raise MetricsError("metrics_oversized")
    successes, errors, seen, scopes = [], [], set(), set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Ignore unrelated metrics but never silently ignore a malformed required one.
        prefix = re.split(r'[\s{]', line, maxsplit=1)[0]
        if prefix not in (LAST, ERRORS):
            continue
        match = _LINE.fullmatch(line)
        if not match:
            raise MetricsError("invalid_metric_line")
        name, raw_labels, raw_value = match.groups()
        labels = _labels(raw_labels)
        if (name, labels) in seen:
            raise MetricsError("duplicate_metric_series")
        seen.add((name, labels))
        allowed = _SCOPE | ({"error_kind"} if name == ERRORS else set())
        if set(dict(labels)) - allowed:
            raise MetricsError("unsupported_metric_dimensions")
        scopes.add(tuple((key, value) for key, value in labels if key in _SCOPE))
        try:
            value = float(raw_value)
        except ValueError as exc:
            raise MetricsError("invalid_metric_value") from exc
        if not math.isfinite(value) or value < 0 or not value.is_integer() or value > 2**53:
            raise MetricsError("invalid_metric_value")
        if name == LAST:
            successes.append(value)
        else:
            errors.append((labels, int(value)))
    if len(successes) != 1 or not errors:
        raise MetricsError("required_counters_missing_or_ambiguous")
    if len(scopes) != 1:
        raise MetricsError("inconsistent_metric_scope")
    if len(errors) > 1 and any("error_kind" not in dict(labels) for labels, _ in errors):
        raise MetricsError("ambiguous_error_aggregation")
    return Sample(successes[0], tuple(sorted(errors)))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise MetricsError("local_redirect_refused")


def local_url(url: str) -> str:
    if not isinstance(url, str) or not re.fullmatch(r"http://127\.0\.0\.1:[0-9]{1,5}", url):
        raise MetricsError("invalid_local_health_url")
    if not 1 <= int(url.rsplit(':', 1)[1]) <= 65535:
        raise MetricsError("invalid_local_health_port")
    return url


def local_get(url: str, endpoint: str, limit: int, timeout: float = 2.0) -> bytes:
    if endpoint not in ('/metrics', '/readyz'):
        raise MetricsError("endpoint_not_allowed")
    # This bypass affects this loopback-only opener, never system proxy settings.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(local_url(url) + endpoint,
                                     headers={"Cache-Control": "no-cache, no-store"})
    with opener.open(request, timeout=timeout) as response:
        if response.status != 200:
            raise MetricsError("local_http_error")
        age = response.headers.get('Age', '0')
        if not age.isdigit() or int(age) > 0:
            raise MetricsError("cached_metrics_refused")
        body = response.read(limit + 1)
        if len(body) > limit:
            raise MetricsError("metrics_oversized")
        return body


def _timestamp(value) -> float:
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    result = parsed.timestamp()
    if not math.isfinite(result):
        raise ValueError("finite timestamp required")
    return result


def recent_log_event(path: Path, started_at: float, now: float) -> dict | None:
    """Read a bounded tail of structured poll events for this process generation.

    The returned dict is an allowlist. A mention of '403' in arbitrary text is
    never a region diagnosis. Unreadable, old or truncated data proves nothing.
    """
    try:
        if path.is_symlink():
            return None
        with path.open('rb') as stream:
            stream.seek(0, 2)
            length = stream.tell()
            stream.seek(max(0, length - MAX_LOG_BYTES))
            if length > MAX_LOG_BYTES:
                stream.readline()
            raw = stream.read(MAX_LOG_BYTES)
    except OSError:
        return None
    events = []
    for line in raw.splitlines():
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                continue
            stamp = _timestamp(record.get('time'))
            if not started_at <= stamp <= now or now - stamp > FRESH_WINDOW_SECONDS:
                continue
            message = record.get('msg')
            if message == 'poller recovered; polling operational':
                events.append({'kind': 'recovered', 'at': stamp})
            elif message in ('poll failed; backing off', 'poll timed out; backing off'):
                status = record.get('status_code')
                code = record.get('error_code')
                if type(status) is int and status == 403 and code == 'unsupported_country_region_territory':
                    kind = 'region_403'
                elif type(status) is int and status in (401, 403):
                    kind = 'authorization_rejected'
                else:
                    kind = 'poll_failed'
                events.append({'kind': kind, 'at': stamp})
        except (ValueError, TypeError, UnicodeError, OverflowError):
            continue
    return max(events, key=lambda event: event['at']) if events else None


def result(state: str, reason: str, metrics_state: str = 'unknown', event=None) -> dict:
    diagnosis = event.get('kind') if event else None
    return {'state': state, 'reason': reason, 'metrics_state': metrics_state,
            'diagnostic': diagnosis, 'restart_recommended': False}


class CloudObserver:
    """One observer, not a supervisor. Restarting the UI loses evidence safely."""
    def __init__(self):
        self.lock = threading.Lock()
        self.generation = None
        self.previous = None
        self.failure_latched = False
        self.previous_observed = None
        self.last_state = 'unknown'

    def reset(self, generation=None):
        self.generation = generation
        self.previous = None
        self.failure_latched = False
        self.previous_observed = None
        self.last_state = 'unknown'

    def observe(self, text: str | None, generation: str, now: float | None = None,
                event: dict | None = None, freshness: float = FRESH_WINDOW_SECONDS) -> dict:
        now = time.time() if now is None else now
        with self.lock:
            if generation != self.generation:
                self.reset(generation)
            if not math.isfinite(now) or not math.isfinite(freshness) or freshness <= 0:
                self.reset(generation)
                return result('unknown', 'invalid_clock')
            # Evidence becomes invalid across a sleep/long observation gap or clock rollback.
            if self.previous_observed is not None and not 0 <= now - self.previous_observed <= freshness:
                # Keep monotonic counter history: a missing scrape or sleep must
                # not erase a known failure and make a reset counter look healthy.
                self.failure_latched = True
                self.last_state = 'unknown'
            try:
                sample = parse_metrics(text) if text is not None else None
                if sample is None:
                    raise MetricsError('metrics_unavailable')
            except MetricsError as exc:
                self.failure_latched = True
                self.last_state = 'unknown'
                self.previous_observed = now
                return result('unknown', str(exc), event=event)
            old = self.previous
            previous_state = self.last_state
            self.previous, self.previous_observed = sample, now
            if sample.last_success > now:
                self.failure_latched = True
                outcome = result('unknown', 'future_timestamp', event=event)
            elif sample.last_success == 0 or now - sample.last_success > freshness:
                self.failure_latched = sample.total_errors > 0
                reason = 'no_successful_poll' if sample.last_success == 0 else 'stale_success'
                outcome = result('unknown', reason, event=event)
            else:
                old_errors = dict(old.errors) if old else {}
                new_errors = dict(sample.errors)
                regressed = old is not None and (
                    sample.last_success < old.last_success or
                    any(key not in new_errors or new_errors[key] < value for key, value in old_errors.items()))
                increased = old is not None and any(value > old_errors.get(key, 0)
                                                    for key, value in new_errors.items())
                advanced = old is not None and sample.last_success > old.last_success
                fresh_failure = bool(event and event['kind'] != 'recovered' and
                                     0 <= now - event['at'] <= freshness and
                                     event['at'] >= sample.last_success)
                if regressed:
                    self.failure_latched = True
                    outcome = result('unknown', 'counter_reset_or_series_disappeared', 'unknown', event)
                elif fresh_failure:
                    self.failure_latched = True
                    state = 'blocked' if event['kind'] in ('region_403', 'authorization_rejected') else 'degraded'
                    outcome = result(state, 'failure_after_success', 'fresh', event)
                elif increased:
                    self.failure_latched = True
                    outcome = result('unknown' if advanced else 'degraded',
                                     'success_failure_order_unknown' if advanced else 'new_poll_errors', 'fresh', event)
                elif advanced:
                    self.failure_latched = False
                    outcome = result('ok', 'observed_recovery' if previous_state != 'ok' else 'polling', 'fresh', event)
                elif self.failure_latched:
                    outcome = result('degraded', 'awaiting_new_success', 'fresh', event)
                elif old is None and sample.total_errors:
                    self.failure_latched = True
                    outcome = result('unknown', 'history_requires_observed_recovery', 'fresh', event)
                else:
                    outcome = result('ok', 'polling', 'fresh', event)
            self.last_state = outcome['state']
            return outcome


OBSERVER = CloudObserver()


def inspect_cloud(url: str, generation: str, started_at: float, log_path: Path,
                  now: float | None = None, observer: CloudObserver = OBSERVER) -> dict:
    now = time.time() if now is None else now
    event = recent_log_event(log_path, started_at, now)
    try:
        text = local_get(url, '/metrics', MAX_METRICS_BYTES).decode('utf-8', 'strict')
    except (OSError, ValueError, UnicodeError):
        text = None
    return observer.observe(text, generation, now, event)
