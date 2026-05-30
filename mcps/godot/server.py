import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("godot")

GODOT_BIN = os.environ.get("GODOT_BIN", "godot-4")

PROJECT_GODOT_TEMPLATE = """; Engine configuration file.
config_version=5

[application]

config/name="{name}"
config/features=PackedStringArray("4.3", "Forward Plus")
run/main_scene="res://scenes/Main.tscn"

[display]

window/size/viewport_width=320
window/size/viewport_height=240
window/stretch/mode="canvas_items"
window/stretch/aspect="keep"
"""

EXPORT_PRESETS_TEMPLATE = """[preset.0]

name="Web"
platform="Web"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/index.html"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
"""


def scaffold_project(name: str, path: str) -> str:
    """Scaffold a new Godot 4 project with Web export preset.

    Creates {path}/{name}/ with project.godot, export_presets.cfg,
    and standard subdirectories (scenes, scripts, rooms, sprites, audio, build).
    Returns the absolute path to the created project directory.
    """
    project_dir = os.path.join(os.path.abspath(path), name)
    os.makedirs(project_dir, exist_ok=True)

    for subdir in ("scenes", "scripts", "rooms", "sprites", "audio", "build"):
        os.makedirs(os.path.join(project_dir, subdir), exist_ok=True)

    with open(os.path.join(project_dir, "project.godot"), "w") as f:
        f.write(PROJECT_GODOT_TEMPLATE.format(name=name))

    with open(os.path.join(project_dir, "export_presets.cfg"), "w") as f:
        f.write(EXPORT_PRESETS_TEMPLATE)

    return project_dir


def export_html5(project_path: str, output_path: str) -> str:
    """Export a Godot 4 project to HTML5.

    Runs godot-4 --headless --export-release Web <output_path> from within
    the project directory. output_path must be inside project_path.
    Returns output_path on success. Raises RuntimeError on non-zero exit.
    Raises ValueError if output_path escapes the project directory.
    """
    project_path = os.path.abspath(project_path)
    output_path = os.path.abspath(output_path)

    if not output_path.startswith(project_path + os.sep):
        raise ValueError(
            f"output_path '{output_path}' is outside project '{project_path}'. "
            "Use a path inside the project directory."
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result = subprocess.run(
        [GODOT_BIN, "--headless", "--export-release", "Web", output_path],
        cwd=project_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Godot export failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    return output_path


@mcp.tool()
def scaffold_project_tool(name: str, path: str) -> str:
    """Scaffold a new Godot 4 project at path/name/ with Web export preset.
    Returns the absolute path to the project directory.
    """
    return scaffold_project(name=name, path=path)


@mcp.tool()
def export_html5_tool(project_path: str, output_path: str) -> str:
    """Export a Godot 4 project to HTML5. output_path must be inside project_path.
    Returns output_path on success.
    """
    return export_html5(project_path=project_path, output_path=output_path)


if __name__ == "__main__":
    mcp.run()
