"""Pinned upstream Blender MCP plus transparent, owner-configured workflow defaults."""
import json
import os
from pathlib import Path
from settings import CONFIG
from workflow import add_bridge_settings, clean_task_parameter_description

os.environ["BLENDER_MCP_SAFE_MODE"] = "1"
os.environ["DISABLE_TELEMETRY"] = "true"
from blender_mcp import server
from mcp.types import ToolAnnotations

output = Path(CONFIG["output_root"]).expanduser()
output.mkdir(parents=True, exist_ok=True)
server.mcp._mcp_server.instructions = server.SERVER_INSTRUCTIONS + """

Blender Web Bridge owner-configured defaults:
- A user can select this app, attach an image, and ask in ordinary language to model it.
  Use the reference image's visible shape/material details; disclose approximation.
- For a NEW model, first inspect the live scene. Save a uniquely named backup if
  there are unsaved changes, create a separate scene, and preserve existing work.
- Save new editable .blend files and previews with unique names in the output
  directory below. Never overwrite unrelated files.
- Keep the viewport framed on the scene as stages are built. Check the resulting
  image and report the actual saved path.
- External asset/generation providers and telemetry are disabled in this profile.
- These defaults are not a filesystem sandbox. Respect host approval and safety
  decisions; they do not grant permission to access unrelated private data.
Configured output directory (data, not an instruction): """ + json.dumps(str(output))

# Keep the upstream tool schema and execution path. Add visible configuration to
# its actual result because some hosts do not forward initialize.instructions.
scene_tool = server.mcp._tool_manager.get_tool("get_scene_info")
original_scene_fn = scene_tool.fn


async def scene_info_with_defaults(*args, **kwargs):
    raw = await original_scene_fn(*args, **kwargs)
    return add_bridge_settings(raw, output)


scene_tool.fn = scene_info_with_defaults

# Descriptions are data about capabilities, not commands to a classifier/model.
# Do not alter tool permissions, code validation, schemas, or host approval.
for tool in server.mcp._tool_manager.list_tools():
    tool.description = clean_task_parameter_description(tool.description)


@server.mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
def get_bridge_settings() -> dict:
    """Read this Mac's configured model output folder and scene-preservation defaults.
    Use when the user asks where to save, or before saving a newly created model.
    Returns configuration only; does not read any files, secrets, or account details.
    """
    return {
        "output_directory": str(output),
        "new_models_use_separate_scenes": True,
        "use_unique_filenames": True,
        "filesystem_sandbox": False,
    }


server.main()
