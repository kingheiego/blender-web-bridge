# Author / 作者水印: @kinghei.ego/@ai.alter
"""Expose user-selected defaults as runtime data, not only optional server guidance."""
import json
import re


def clean_task_parameter_description(description):
    """Remove upstream verbatim-prompt instructions; preserve capability warnings."""
    return re.sub(
        r"(?m)^(\s*-\s*user_prompt:).*$",
        r"\1 Task context for this operation. Do not include credentials.",
        description or "",
    )


def add_bridge_settings(raw, output_directory):
    try:
        scene = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return raw
    if not isinstance(scene, dict):
        return raw
    scene["bridge_settings"] = {
        "output_directory": str(output_directory),
        "new_models_use_separate_scenes": True,
        "use_unique_filenames": True,
        "filesystem_sandbox": False,
    }
    return json.dumps(scene, ensure_ascii=False, indent=2)
