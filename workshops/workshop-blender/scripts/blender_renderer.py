#!/usr/bin/env python3
"""
Blender Headless Renderer (blender_renderer.py)

Renders a 3D Xianxia scene with automated camera animation based on
a timeline spec JSON generated from the unified job specification.

Usage inside Blender headless:
  blender.exe -b -P workshops/workshop-blender/scripts/blender_renderer.py -- --spec <path_to_spec.json> --output <path_to_raw.mp4> [--dry-run]
"""
import argparse
import json
import math
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import bpy
    import mathutils
except ImportError:
    print("[ERROR] Script must be executed inside Blender's embedded Python environment.", file=sys.stderr)
    sys.exit(1)

# Preset camera positions for dynamic shot choreography
CAMERA_POSITIONS = {
    "dolly_in": {
        "start": (0.0, -9.8, 3.4),
        "end": (0.0, -5.8, 2.2),
    },
    "orbit": {
        "start": (-3.5, -8.0, 3.0),
        "end": (3.5, -8.0, 3.0),
    },
    "dolly_out": {
        "start": (0.0, -5.8, 2.2),
        "end": (0.0, -9.8, 3.4),
    },
    "static": {
        "start": (0.0, -8.5, 2.8),
        "end": (0.0, -8.5, 2.8),
    },
}

# Focal target for camera view (centered between character and divine sword)
SCENE_TARGET = mathutils.Vector((0.0, -0.6, 2.0))


def parse_args():
    """
    Parse command line arguments passed after '--'.
    Supports --spec, --output, --dry-run, and --help.
    """
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(
        prog="blender_renderer.py",
        description="Headless Blender 3D Scene and Camera Animation Renderer",
        add_help=True
    )
    parser.add_argument("--spec", type=str, required=True, help="Path to timeline spec JSON file")
    parser.add_argument("--output", type=str, required=True, help="Path to output video file (.mp4)")
    parser.add_argument("--dry-run", action="store_true", help="Setup scene and camera without rendering animation")

    if "-h" in argv or "--help" in argv:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args(argv)


def create_material(name, base_color, metallic=0.0, roughness=0.5, emission_color=(0.0, 0.0, 0.0, 1.0), emission_strength=0.0):
    """
    Creates or reconfigures a Principled BSDF material.
    """
    mat = bpy.data.materials.new(name=name)
    if not getattr(mat, "node_tree", None) and hasattr(mat, "use_nodes"):
        mat.use_nodes = True
    nodes = mat.node_tree.nodes if mat.node_tree else None
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission_color
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = emission_color
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    return mat


def assign_material(obj, mat):
    """Assigns a material to an object's first material slot."""
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def add_cylinder(name, radius, depth, location, rotation=(0.0, 0.0, 0.0), vertices=32, material=None):
    """Helper to create a cylinder primitive."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        assign_material(obj, material)
    return obj


def add_sphere(name, radius, location, segments=32, ring_count=16, material=None):
    """Helper to create a UV sphere primitive."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=ring_count,
        radius=radius,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        assign_material(obj, material)
    return obj


def add_cube(name, scale, location, rotation=(0.0, 0.0, 0.0), material=None):
    """Helper to create a cube primitive."""
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if material:
        assign_material(obj, material)
    return obj


def setup_scene_and_character():
    """
    Cleans up old scene data and creates:
    - Dark mystical world background
    - Specialized Xianxia materials
    - 3-tier octagonal stone altar
    - 4 warding stone pillars with glowing spirit orbs
    - Divine Sword embedded at altar center
    - Taoist Monk character standing before the altar with hands clasped behind back
    - 3-point cinematic lighting (MoonKey, WarmFill, AuraLight)
    """
    # 1. Clear old meshes, lights, cameras, materials
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam, do_unlink=True)

    # 2. Setup mystical dark World background
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    if not getattr(world, "node_tree", None) and hasattr(world, "use_nodes"):
        world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background") if world.node_tree else None
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.008, 0.012, 0.025, 1.0)
        bg_node.inputs["Strength"].default_value = 1.0

    # 3. Create materials
    dark_stone = create_material(
        "DarkStone",
        base_color=(0.04, 0.04, 0.05, 1.0),
        metallic=0.1,
        roughness=0.85
    )
    ancient_gold = create_material(
        "AncientGold",
        base_color=(0.85, 0.65, 0.18, 1.0),
        metallic=0.95,
        roughness=0.35
    )
    sword_blade = create_material(
        "SwordBlade",
        base_color=(0.75, 0.88, 0.98, 1.0),
        metallic=0.98,
        roughness=0.12,
        emission_color=(0.12, 0.45, 0.85, 1.0),
        emission_strength=1.5
    )
    spirit_aura = create_material(
        "SpiritAura",
        base_color=(0.05, 0.85, 0.95, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission_color=(0.0, 0.9, 1.0, 1.0),
        emission_strength=8.0
    )
    char_skin = create_material(
        "CharSkin",
        base_color=(0.85, 0.70, 0.58, 1.0),
        metallic=0.0,
        roughness=0.55
    )
    char_robe = create_material(
        "CharRobe",
        base_color=(0.03, 0.08, 0.22, 1.0),
        metallic=0.05,
        roughness=0.75
    )
    char_hair = create_material(
        "CharHair",
        base_color=(0.02, 0.02, 0.025, 1.0),
        metallic=0.1,
        roughness=0.6
    )

    # 4. Octagonal Altar Base (r=4.0), Mid (r=3.2), Core (r=1.6)
    add_cylinder("Altar_Base", radius=4.0, depth=0.5, location=(0.0, 0.0, 0.25), vertices=8, material=dark_stone)
    add_cylinder("Altar_Mid", radius=3.2, depth=0.5, location=(0.0, 0.0, 0.75), vertices=8, material=dark_stone)
    add_cylinder("Altar_Core", radius=1.6, depth=0.5, location=(0.0, 0.0, 1.25), vertices=8, material=dark_stone)

    # 5. Four Warding Pillars with Spirit Aura orbs
    pillar_coords = [(-2.2, -2.2), (2.2, -2.2), (-2.2, 2.2), (2.2, 2.2)]
    for i, (px, py) in enumerate(pillar_coords, start=1):
        add_cylinder(f"Pillar_{i}", radius=0.25, depth=2.2, location=(px, py, 2.1), vertices=8, material=dark_stone)
        add_cylinder(f"PillarCap_{i}", radius=0.28, depth=0.1, location=(px, py, 3.25), vertices=8, material=ancient_gold)
        add_sphere(f"PillarOrb_{i}", radius=0.2, location=(px, py, 3.45), material=spirit_aura)

    # 6. Divine Sword embedded in Altar Core center
    # - Blade
    add_cube("DivineSword_Blade", scale=(0.14, 0.03, 1.9), location=(0.0, 0.0, 2.45), material=sword_blade)
    # - Crossguard
    add_cube("DivineSword_Guard", scale=(0.7, 0.12, 0.08), location=(0.0, 0.0, 3.45), material=ancient_gold)
    # - Grip / Handle
    add_cylinder("DivineSword_Grip", radius=0.035, depth=0.55, location=(0.0, 0.0, 3.75), material=ancient_gold)
    # - Pommel
    add_sphere("DivineSword_Pommel", radius=0.09, location=(0.0, 0.0, 4.08), material=spirit_aura)

    # 7. Character: Taoist Monk standing before altar with hands clasped behind back
    # Ground at character position on Mid tier is z = 1.0
    char_y = -2.3
    add_cylinder("Char_RobeLower", radius=0.32, depth=0.9, location=(0.0, char_y, 1.45), material=char_robe)
    add_cube("Char_Chest", scale=(0.52, 0.32, 0.65), location=(0.0, char_y, 2.15), material=char_robe)
    add_cylinder("Char_Neck", radius=0.08, depth=0.15, location=(0.0, char_y, 2.52), material=char_skin)
    add_sphere("Char_Head", radius=0.18, location=(0.0, char_y, 2.72), material=char_skin)
    add_cylinder("Char_HairBun", radius=0.09, depth=0.15, location=(0.0, char_y, 2.92), material=char_hair)
    add_cylinder("Char_HairPin", radius=0.015, depth=0.35, location=(0.0, char_y, 2.92), rotation=(0.0, math.radians(90), 0.0), material=ancient_gold)
    # Arms and hands clasped behind back
    add_cylinder("Char_LeftArm", radius=0.07, depth=0.45, location=(-0.20, char_y + 0.12, 1.95), rotation=(math.radians(30), math.radians(20), 0.0), material=char_robe)
    add_cylinder("Char_RightArm", radius=0.07, depth=0.45, location=(0.20, char_y + 0.12, 1.95), rotation=(math.radians(30), math.radians(-20), 0.0), material=char_robe)
    add_sphere("Char_HandsClasped", radius=0.09, location=(0.0, char_y + 0.16, 1.82), material=char_skin)

    # 8. 3-Point Cinematic Lighting
    # MoonKey (cool blue moonlight angled downwards)
    moon_light = bpy.data.lights.new(name="MoonKey", type="SUN")
    moon_light.energy = 4.5
    moon_light.color = (0.4, 0.65, 1.0)
    moon_obj = bpy.data.objects.new("MoonKey", moon_light)
    moon_obj.location = (4.0, -5.0, 10.0)
    sun_dir = SCENE_TARGET - mathutils.Vector((4.0, -5.0, 10.0))
    moon_obj.rotation_euler = sun_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(moon_obj)

    # WarmFill (warm ambient fill light from opposite angle)
    fill_light = bpy.data.lights.new(name="WarmFill", type="POINT")
    fill_light.energy = 400.0
    fill_light.color = (1.0, 0.75, 0.45)
    fill_obj = bpy.data.objects.new("WarmFill", fill_light)
    fill_obj.location = (-5.0, -3.0, 4.0)
    bpy.context.scene.collection.objects.link(fill_obj)

    # AuraLight (radiant cyan light emanating from divine sword)
    aura_light = bpy.data.lights.new(name="AuraLight", type="POINT")
    aura_light.energy = 350.0
    aura_light.color = (0.1, 0.85, 1.0)
    aura_obj = bpy.data.objects.new("AuraLight", aura_light)
    aura_obj.location = (0.0, 0.0, 2.5)
    bpy.context.scene.collection.objects.link(aura_obj)


def set_camera_interpolation(cam_obj, interpolation="BEZIER"):
    """
    Configures keyframe interpolation across all fcurves for legacy and layered actions.
    """
    if not cam_obj.animation_data or not cam_obj.animation_data.action:
        return
    action = cam_obj.animation_data.action

    # Legacy fcurves (Blender < 4.4)
    if hasattr(action, "fcurves"):
        for fc in action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = interpolation

    # Layered action strips / channelbags (Blender 4.4 / 5.x)
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in getattr(layer, "strips", []):
                for slot in getattr(action, "slots", []):
                    try:
                        cb = strip.channelbag(slot)
                        if cb and hasattr(cb, "fcurves"):
                            for fc in cb.fcurves:
                                for kp in fc.keyframe_points:
                                    kp.interpolation = interpolation
                    except Exception:
                        pass


def keyframe_camera_pose(cam_obj, frame: int, pos: tuple[float, float, float], target: mathutils.Vector):
    """
    Inserts location and rotation keyframes at specified frame pointing directly at target.
    """
    cam_obj.location = pos
    cam_obj.keyframe_insert(data_path="location", frame=frame)

    dir_vec = target - mathutils.Vector(pos)
    cam_obj.rotation_euler = dir_vec.to_track_quat("-Z", "Y").to_euler()
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def setup_camera_and_animate(spec: dict):
    """
    Creates a 40mm cinematic camera and sets keyframe animation for each shot.
    """
    cam_data = bpy.data.cameras.new(name="MainCamera")
    cam_data.lens = 40.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    shots = spec.get("shots", [])

    if not shots:
        # Default static camera pose if no shots defined
        keyframe_camera_pose(cam_obj, 1, CAMERA_POSITIONS["static"]["start"], SCENE_TARGET)
        set_camera_interpolation(cam_obj, "BEZIER")
        return cam_obj

    for shot in shots:
        start_frame = int(shot.get("start_frame", 1))
        end_frame = int(shot.get("end_frame", start_frame))
        action_name = str(shot.get("camera_action", "static")).strip().lower()

        cam_config = CAMERA_POSITIONS.get(action_name, CAMERA_POSITIONS["static"])
        pos_start = cam_config["start"]
        pos_end = cam_config["end"]

        if start_frame == end_frame:
            keyframe_camera_pose(cam_obj, start_frame, pos_start, SCENE_TARGET)
        else:
            keyframe_camera_pose(cam_obj, start_frame, pos_start, SCENE_TARGET)
            keyframe_camera_pose(cam_obj, end_frame, pos_end, SCENE_TARGET)

    set_camera_interpolation(cam_obj, "BEZIER")
    return cam_obj


def configure_render_settings(spec: dict, output_path: str):
    """
    Configures render engine, resolution, fps, frame range, and FFMPEG video output.
    """
    scene = bpy.context.scene

    # 1. Render Engine: try BLENDER_EEVEE_NEXT, fallback to BLENDER_EEVEE
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"

    # 2. Resolution & FPS
    res = spec.get("resolution", [1280, 720])
    scene.render.resolution_x = int(res[0])
    scene.render.resolution_y = int(res[1])
    scene.render.resolution_percentage = 100
    scene.render.fps = int(spec.get("fps", 30))

    # 3. Frame Range
    scene.frame_start = 1
    total_frames = int(spec.get("total_frames", 30))
    scene.frame_end = max(1, total_frames)

    # 4. Output filepath & FFMPEG H.264 MP4 settings
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out_file)

    # In Blender 5.0+, media_type must be set to 'VIDEO' to enable video container formats
    if hasattr(scene.render.image_settings, "media_type"):
        scene.render.image_settings.media_type = "VIDEO"

    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"


def main():
    args = parse_args()
    spec_path = Path(args.spec).resolve()

    if not spec_path.is_file():
        print(f"[ERROR] Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    print(f"[INFO] Initializing scene and character...")
    setup_scene_and_character()

    print(f"[INFO] Setting up camera animation for {len(spec.get('shots', []))} shots...")
    setup_camera_and_animate(spec)

    print(f"[INFO] Configuring render settings (resolution={spec.get('resolution')}, total_frames={spec.get('total_frames')})...")
    configure_render_settings(spec, args.output)

    if args.dry_run:
        print(f"[OK] Dry-run completed successfully. Scene configured, rendering skipped.")
        return

    print(f"[INFO] Starting Blender animation rendering to: {args.output}")
    bpy.ops.render.render(animation=True)
    print(f"[OK] Animation render completed: {args.output}")


if __name__ == "__main__":
    main()
