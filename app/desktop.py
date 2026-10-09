#!/usr/bin/env python3
# Author / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
"""Four-layer macOS controller. Tk widgets are touched only on the UI thread."""
from __future__ import annotations

import json
import queue
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import webbrowser

import bootstrap
import bridge
import keychain_store
import settings
from safeio import FileLock, atomic_json, checked_path

VERSION = '2.0.2-rc3'
DISPLAY_NAME = 'Blender Web Bridge / Blender 網頁橋接器'


def public_status(snapshot):
    """An explicit export allowlist: no account names, IDs, scenes, PIDs or logs."""
    return {
        'schema': 1, 'version': VERSION, 'ready': snapshot.get('ready', False),
        'blender_state': snapshot.get('blender', {}).get('state', 'unknown'),
        'process_ready': snapshot.get('tunnel', {}).get('ok', False),
        'cloud': {key: snapshot.get('cloud', {}).get(key) for key in
                  ('state', 'reason', 'metrics_state', 'diagnostic', 'restart_recommended')},
        'web': {key: snapshot.get('web', {}).get(key) for key in ('state', 'source', 'age_seconds')},
    }


def status_rows(snapshot):
    if not snapshot:
        return [(label, 'Unknown / 未知：沒有新鮮檢查結果') for label in
                ('1 · Blender', '2 · Tunnel process / 程序', '3 · Cloud / 雲端', '4 · ChatGPT web / 網頁')]
    cloud = snapshot['cloud']
    cloud_text = {'ok': 'Polling confirmed / 已確認輪詢', 'blocked': 'Rejected / 雲端拒絕',
                  'degraded': 'New failure; recovery unconfirmed / 出現新失敗，恢復未確認',
                  'unknown': 'Unknown / 未知'}.get(cloud['state'], 'Unknown / 未知')
    if cloud.get('diagnostic') == 'region_403':
        cloud_text += ' · HTTP 403 unsupported_country_region_territory; restart will not grant eligibility / 重啟不會取得地區資格'
    elif cloud.get('diagnostic') == 'authorization_rejected':
        cloud_text += ' · Authorization rejected / 授權被拒'
    cloud_text += ' · metrics: ' + cloud.get('metrics_state', 'unknown')
    return [('1 · Blender', snapshot['blender']['detail']),
            ('2 · Tunnel process / 程序', snapshot['tunnel']['detail']),
            ('3 · Cloud / 雲端', cloud_text), ('4 · ChatGPT web / 網頁', snapshot['web']['detail'])]


class App:
    def __init__(self, root):
        self.root, self.events = root, queue.Queue()
        self.busy = self.polling = False
        self.last, self.observed = None, 0.0
        root.title(DISPLAY_NAME + ' · ' + VERSION)
        root.geometry('1080x800')
        root.minsize(960, 720)
        style = ttk.Style()
        if 'aqua' in style.theme_names():
            style.theme_use('aqua')
        heading = ttk.Frame(root, padding=20)
        heading.pack(fill='x')
        ttk.Label(heading, text=DISPLAY_NAME, font=('', 22, 'bold')).pack(anchor='w')
        ttk.Label(heading, text='One private connection · 四層狀態獨立驗證 · No network-setting changes / 不更改網絡設定').pack(anchor='w', pady=6)
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill='both', expand=True, padx=20, pady=6)
        self.status_page = ttk.Frame(self.tabs, padding=16)
        self.setup_page = ttk.Frame(self.tabs, padding=16)
        self.web_page = ttk.Frame(self.tabs, padding=16)
        for page, title in ((self.status_page, 'Status / 狀態'), (self.setup_page, 'Setup / 設定'),
                            (self.web_page, 'Web acceptance / 網頁驗收')):
            self.tabs.add(page, text=title)
        self.headline = ttk.Label(self.status_page, text='Unknown / 正在取得新鮮資料', font=('', 17, 'bold'))
        self.headline.pack(anchor='w', pady=(0, 14))
        self.rows = []
        for label, detail in status_rows(None):
            box = ttk.LabelFrame(self.status_page, text=label, padding=10)
            box.pack(fill='x', pady=5)
            var = tk.StringVar(value=detail)
            ttk.Label(box, textvariable=var, wraplength=920, justify='left').pack(anchor='w')
            self.rows.append(var)
        controls = ttk.Frame(self.status_page)
        controls.pack(fill='x', pady=16)
        self.buttons = []
        for text, action in [('Connect / 一鍵連接', bridge.connect), ('Stop / 停止通道', bridge.disconnect)]:
            button = ttk.Button(controls, text=text, command=lambda fn=action: self.action(fn))
            button.pack(side='left', padx=(0, 12))
            self.buttons.append(button)
        ttk.Button(controls, text='Check / 檢查', command=self.poll).pack(side='left', padx=8)
        ttk.Button(controls, text='Guide / 圖解', command=self.help).pack(side='left', padx=8)
        ttk.Button(controls, text='Export status / 匯出狀態', command=self.export).pack(side='left', padx=8)
        ttk.Label(self.status_page, text='Open Blender yourself before Connect. Closing Blender keeps it closed; Stop disconnects only the tunnel.\n先自行開啟 Blender 再按連接。關閉 Blender 後不會自動重開；停止只會中斷通道。', wraplength=920).pack(anchor='w')
        self.setup()
        self.acceptance()
        self.message = tk.StringVar(value='Open Blender yourself, then check each connection layer / 自行開啟 Blender 後逐層檢查連線 · @kinghei.ego/@ai.alter (GitHub: kingheiego)')
        ttk.Label(root, textvariable=self.message, wraplength=1020, padding=18).pack(fill='x')
        root.after(50, self.poll)
        root.after(100, self.drain)
        root.after(500, self.watchdog)

    def setup(self):
        page = self.setup_page
        ttk.Label(page, text='Existing Tunnel ID and credential bindings are preserved.\n既有 Tunnel ID 與憑證綁定不會被重建或更換。', wraplength=920).grid(row=0, column=0, columnspan=2, sticky='w', pady=12)
        self.values = {}
        for row, (key, text) in enumerate((('blender_app', 'Blender.app'), ('tunnel_id', 'Tunnel ID / 通道 ID'),
                                           ('app_name', 'Tool display name / 工具顯示名稱'),
                                           ('output_root', 'Output folder / 輸出資料夾')), 1):
            ttk.Label(page, text=text).grid(row=row, column=0, sticky='w', pady=9)
            var = tk.StringVar(value=bridge.CONFIG[key])
            self.values[key] = var
            entry = ttk.Entry(page, textvariable=var, width=68)
            entry.grid(row=row, column=1, sticky='ew', padx=16)
            if key == 'tunnel_id' and bridge.CONFIG.get('tunnel_id'):
                entry.configure(state='disabled')
        self.secret = tk.StringVar()
        ttk.Label(page, text='Existing runtime key / 已有通道金鑰').grid(row=5, column=0, sticky='w', pady=9)
        key_entry = ttk.Entry(page, textvariable=self.secret, show='•', width=68)
        key_entry.grid(row=5, column=1, sticky='ew', padx=16)
        if bridge.CONFIG.get('credential_configured'):
            key_entry.configure(state='disabled')
        page.columnconfigure(1, weight=1)
        ttk.Label(page, text='First setup only: paste your own existing key. Nothing creates a key or tunnel.\n首次設定才可輸入你已有的金鑰；本程式不建立金鑰或通道。', wraplength=920).grid(row=6, column=0, columnspan=2, sticky='w', pady=12)
        for row, label, fn in ((7, 'Save setup / 儲存設定', self.save_setup),
                                (8, 'Prepare components / 準備元件', lambda: self.action(self.prepare_components)),
                                (9, 'Disable old Blender auto-restart / 停用舊版 Blender 自動重開', self.retire_legacy)):
            button = ttk.Button(page, text=label, command=fn)
            button.grid(row=row, column=0, columnspan=2, sticky='w', pady=8)
            self.buttons.append(button)
        ttk.Label(page, text='Save and close Blender, then stop the tunnel before Prepare components. If an older install keeps reopening Blender, save your scene, Stop the tunnel, and use the legacy button once.\n準備元件前先儲存並關閉 Blender，再停止通道；若舊版仍會自動重開 Blender，先儲存場景、停止通道，再按上方舊版按鈕一次。', wraplength=920).grid(row=10, column=0, columnspan=2, sticky='w', pady=12)

    def retire_legacy(self):
        if messagebox.askyesno(
                'Old Blender auto-restart / 舊版 Blender 自動重開',
                'Save your Blender scene first. This will close only the old managed Blender instance and archive its auto-restart service. Continue?\n請先儲存 Blender 場景。此操作會關閉舊版受管理的 Blender，並備份及停用它的自動重開服務。是否繼續？'):
            self.action(bridge.retire_legacy_blender_service)

    def prepare_components(self):
        if (bridge.require_service_known(bridge.CONFIG['blender_label'])['loaded']
                or bridge.LEGACY_BLENDER_PLIST.exists()):
            return {'ok': False,
                    'message': 'Save Blender, Stop the tunnel, then use the old auto-restart button first / 先儲存 Blender、停止通道，再按停用舊版自動重開'}
        return bootstrap.prepare_runtime()

    def acceptance(self):
        page = self.web_page
        text = ('In ChatGPT, select your existing Blender app and request get_scene_info twice.\n'
                'Check the real returned scene name and object count. Do not request any edits or saves.\n'
                '在 ChatGPT 選既有 Blender 工具，要求實際呼叫 get_scene_info 兩次。\n'
                '核對真實回覆的場景名稱與物件數，不建立、修改或存檔。\n\n'
                'Recording below is your explicit observation, not an automatic web verification.\n'
                'A pass expires after 5 minutes or on a process-generation change or local/cloud failure.\n'
                '下方只記錄你的明確觀察，並非自動網頁驗證。通過紀錄五分鐘後、程序更替或本機／雲端失敗時失效。')
        ttk.Label(page, text=text, wraplength=940, justify='left').pack(anchor='w', pady=12)
        ttk.Label(page, text='Evidence reference / 證據參照（只保存雜湊，不保存原文）').pack(anchor='w', pady=8)
        self.evidence = tk.StringVar()
        ttk.Entry(page, textvariable=self.evidence, width=90).pack(fill='x', pady=8)
        row = ttk.Frame(page)
        row.pack(fill='x', pady=12)
        for passed, text in ((True, 'Record actual pass / 記錄實際通過'), (False, 'Record actual failure / 記錄實際失敗')):
            button = ttk.Button(row, text=text, command=lambda value=passed: self.attest(value))
            button.pack(side='left', padx=(0, 12))
            self.buttons.append(button)

    def save_setup(self):
        value = dict(bridge.CONFIG)
        for key, var in self.values.items():
            value[key] = var.get().strip()
        secret = self.secret.get().strip()
        self.secret.set('')
        def save():
            with FileLock(bridge.STATE / 'control.lock'):
                bridge.assert_install_complete()
                if bridge.require_service_known(bridge.LABEL)['loaded']:
                    raise RuntimeError('Tunnel must be stopped')
                settings.validate(value, require_ready=True)
                if not (Path(value['blender_app']) / 'Contents/MacOS/Blender').is_file():
                    raise ValueError('Blender.app not found')
                if secret and bridge.CONFIG.get('credential_configured'):
                    raise ValueError('Existing key replacement is disabled')
                if secret:
                    keychain_store.put(secret, account=value['credential'].get('account', 'default'))
                    value['credential_configured'] = True
                settings.save(value)
                return {'ok': True, 'message': 'Saved locally / 已在本機儲存設定'}
        self.action(save)

    def attest(self, passed):
        evidence = self.evidence.get().strip()
        if not evidence:
            self.message.set('Enter a reference to a real tool result / 請輸入真實工具回覆的證據參照')
            return
        if passed and not messagebox.askyesno('Actual web test / 真實網頁測試',
                'Did you observe successful read-only replies in ChatGPT?\n你是否已在 ChatGPT 親自核對成功的唯讀工具回覆？'):
            return
        self.action(lambda: bridge.record_web_acceptance(passed, evidence))

    def action(self, fn):
        if self.busy:
            return
        self.busy = True
        for button in self.buttons:
            button.configure(state='disabled')
        self.message.set('Working on the requested local action / 正在執行所要求的本機操作')
        def worker():
            try:
                outcome = fn()
            except Exception as exc:
                outcome = {'ok': False, 'message': 'Action refused or failed / 操作已拒絕或失敗：' + type(exc).__name__}
            self.events.put(('action', outcome))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        if not self.polling:
            self.polling = True
            def worker():
                try:
                    value = bridge.snapshot()
                except Exception:
                    value = None
                self.events.put(('snapshot', value))
            threading.Thread(target=worker, daemon=True).start()

    def apply(self, value):
        self.last = value
        self.observed = time.monotonic() if value else 0.0
        for var, (_, text) in zip(self.rows, status_rows(value)):
            var.set(text)
        if not value:
            bridge.invalidate_web_acceptance()
            title = 'Unknown / 檢查失敗或資料已過期'
        elif value['ready']:
            title = 'Local + cloud + recent owner-confirmed web test / 三項條件已確認'
        elif value['cloud_ready']:
            title = 'Local/cloud confirmed; web unverified / 本機及雲端已確認，網頁未驗收'
        else:
            title = 'Not verified end-to-end / 未確認端到端可用'
        self.headline.configure(text=title)

    def drain(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'snapshot':
                    self.polling = False
                    self.apply(value)
                else:
                    self.busy = False
                    for button in self.buttons:
                        button.configure(state='normal')
                    self.message.set(value.get('message', 'Action finished / 操作完成'))
                    self.poll()
        except queue.Empty:
            pass
        self.root.after(100, self.drain)

    def watchdog(self):
        if self.last and time.monotonic() - self.observed > 15:
            self.apply(None)
        if not self.polling and (not self.last or time.monotonic() - self.observed >= 5):
            self.poll()
        self.root.after(500, self.watchdog)

    def export(self):
        if not self.last or time.monotonic() - self.observed > 15:
            self.message.set('No fresh status to export / 沒有可匯出的新鮮狀態')
            return
        target = filedialog.asksaveasfilename(defaultextension='.json', initialfile='bridge-status.json')
        if target:
            try:
                atomic_json(checked_path(target), public_status(self.last))
            except (OSError, ValueError):
                self.message.set('Export failed / 匯出失敗')

    def help(self):
        path = Path(__file__).resolve().parent / 'docs' / 'SETUP_RC2.html'
        if not path.exists():
            path = Path(__file__).resolve().parent.parent / 'docs' / 'SETUP_RC2.html'
        if path.is_file():
            webbrowser.open(path.as_uri())
        else:
            self.message.set('Guide file is missing / 缺少圖解檔案')


def main():
    if sys.platform != 'darwin':
        print('Desktop launch is macOS-only / 桌面工具只在 macOS 啟動', file=sys.stderr)
        return 1
    try:
        with FileLock(bridge.STATE / 'ui.lock'):
            bridge.assert_install_complete()
            root = tk.Tk()
            App(root)
            root.mainloop()
    except Exception as exc:
        print('Desktop refused or failed / 面板未啟動：' + type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
