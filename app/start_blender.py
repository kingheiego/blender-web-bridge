# Author / 作者水印: @kinghei.ego/@ai.alter
"""Run inside an isolated Blender instance, retaining its normal UI event loop."""
import json
import os
from pathlib import Path
import bpy
import addon_utils

cfg = json.loads(Path(os.environ["BWB_CONFIG_PATH"]).read_text())
os.environ["BLENDER_MCP_SAFE_MODE"] = "1"
os.environ["DISABLE_TELEMETRY"] = "true"
addon_utils.enable("blender_mcp", default_set=True, persistent=True)
for scene in bpy.data.scenes:
    for prop in ("blendermcp_use_polyhaven", "blendermcp_use_hyper3d",
                 "blendermcp_use_sketchfab", "blendermcp_use_polypizza",
                 "blendermcp_use_hunyuan3d", "blendermcp_use_tripo",
                 "blendermcp_telemetry_consent"):
        if hasattr(scene, prop):
            setattr(scene, prop, False)
    scene.blendermcp_port = cfg["port"]
    if hasattr(scene, "blendermcp_auto_start_server"):
        scene.blendermcp_auto_start_server = True
bpy.ops.blendermcp.start_server()
print("Blender Web Bridge add-on started", flush=True)
# Returning is essential: socket commands are dispatched through bpy.app.timers.
