"""Pose Engine for Humanoid 3D Character Armature and Facial Animation.

This module provides humanoid armature posing (converting from T-pose to natural
xianxia / martial arts poses) and procedural facial blinking animation.
Designed to be testable outside Blender via pure functions and mockable objects.
"""

from __future__ import annotations

import math
from typing import Any

try:
    import bpy
    import mathutils
except ImportError:
    bpy = None
    mathutils = None

# Core supported poses
SUPPORTED_POSES = [
    "idle_stand",
    "hands_clasped_back",
    "cast_spell",
    "swordsman_ready",
    "talking",
]

# Mapping between VRoid humanoid bone names and common generic aliases
BONE_ALIASES: dict[str, list[str]] = {
    "J_Bip_C_Hips": ["hips", "hip", "pelvis", "root"],
    "J_Bip_C_Spine": ["spine", "spine_01", "spine.001"],
    "J_Bip_C_Chest": ["chest", "spine_02", "spine.002"],
    "J_Bip_C_UpperChest": ["upperchest", "upper_chest", "spine_03"],
    "J_Bip_C_Neck": ["neck"],
    "J_Bip_C_Head": ["head", "head 1"],
    "J_Bip_L_UpperArm": ["upperarm_l", "upper_arm.l", "arm_l", "leftupperarm"],
    "J_Bip_R_UpperArm": ["upperarm_r", "upper_arm.r", "arm_r", "rightupperarm"],
    "J_Bip_L_LowerArm": ["lowerarm_l", "lower_arm.l", "forearm_l", "forearm.l", "leftlowerarm"],
    "J_Bip_R_LowerArm": ["lowerarm_r", "lower_arm.r", "forearm_r", "forearm.r", "rightlowerarm"],
    "J_Bip_L_Hand": ["hand_l", "hand.l", "wrist_l", "lefthand"],
    "J_Bip_R_Hand": ["hand_r", "hand.r", "wrist_r", "righthand"],
}

ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical_bone, aliases_list in BONE_ALIASES.items():
    ALIAS_TO_CANONICAL[canonical_bone.lower()] = canonical_bone
    ALIAS_TO_CANONICAL[canonical_bone.lower().replace("-", "_").replace(" ", "_")] = canonical_bone
    for alias_name in aliases_list:
        ALIAS_TO_CANONICAL[alias_name.lower()] = canonical_bone
        ALIAS_TO_CANONICAL[alias_name.lower().replace("-", "_").replace(" ", "_")] = canonical_bone


# Base Euler rotations (XYZ order in radians) for VRoid bones
_RAW_POSE_ROTATIONS: dict[str, dict[str, tuple[float, float, float]]] = {
    # 1. idle_stand: Relaxed natural standing posture, arms lowered from T-pose
    "idle_stand": {
        "J_Bip_L_UpperArm": (0.10, 0.05, -1.25),
        "J_Bip_R_UpperArm": (0.10, -0.05, 1.25),
        "J_Bip_L_LowerArm": (0.00, 0.00, -0.25),
        "J_Bip_R_LowerArm": (0.00, 0.00, 0.25),
        "J_Bip_L_Hand": (0.05, 0.00, -0.05),
        "J_Bip_R_Hand": (0.05, 0.00, 0.05),
        "J_Bip_C_Spine": (0.02, 0.00, 0.00),
        "J_Bip_C_Chest": (0.02, 0.00, 0.00),
        "J_Bip_C_Head": (-0.05, 0.00, 0.00),
    },
    # 2. hands_clasped_back: Cultivator / master stance with hands clasped behind back
    "hands_clasped_back": {
        "J_Bip_L_UpperArm": (-0.35, 0.20, -1.30),
        "J_Bip_R_UpperArm": (-0.35, -0.20, 1.30),
        "J_Bip_L_LowerArm": (-0.45, 0.50, -1.15),
        "J_Bip_R_LowerArm": (-0.45, -0.50, 1.15),
        "J_Bip_L_Hand": (0.15, 0.00, -0.25),
        "J_Bip_R_Hand": (0.15, 0.00, 0.25),
        "J_Bip_C_Spine": (-0.05, 0.00, 0.00),
        "J_Bip_C_Chest": (-0.03, 0.00, 0.00),
        "J_Bip_C_Head": (-0.08, 0.00, 0.00),
    },
    # 3. cast_spell: Left hand sword seal at chest, right hand directing spiritual qi forward
    "cast_spell": {
        "J_Bip_L_UpperArm": (0.65, 0.30, -0.85),
        "J_Bip_L_LowerArm": (0.85, 0.40, -0.75),
        "J_Bip_L_Hand": (0.20, 0.10, 0.30),
        "J_Bip_R_UpperArm": (0.95, -0.25, 0.65),
        "J_Bip_R_LowerArm": (0.35, -0.15, 0.20),
        "J_Bip_R_Hand": (-0.20, 0.00, 0.15),
        "J_Bip_C_Spine": (0.05, 0.00, -0.15),
        "J_Bip_C_Chest": (0.05, 0.00, -0.10),
        "J_Bip_C_Head": (0.05, 0.00, 0.15),
    },
    # 4. swordsman_ready: Low martial stance, dominant hand near waist ready to draw blade
    "swordsman_ready": {
        "J_Bip_L_UpperArm": (0.55, 0.20, -0.75),
        "J_Bip_L_LowerArm": (0.65, 0.25, -0.65),
        "J_Bip_L_Hand": (0.10, 0.00, 0.15),
        "J_Bip_R_UpperArm": (-0.35, -0.30, 1.15),
        "J_Bip_R_LowerArm": (0.85, -0.20, 0.55),
        "J_Bip_R_Hand": (0.20, 0.10, -0.10),
        "J_Bip_C_Spine": (0.10, 0.00, 0.20),
        "J_Bip_C_Chest": (0.08, 0.00, 0.15),
        "J_Bip_C_Head": (-0.05, 0.00, -0.15),
    },
    # 5. talking: Relaxed conversational posture with expressive right hand gesture
    "talking": {
        "J_Bip_L_UpperArm": (0.05, 0.00, -1.20),
        "J_Bip_L_LowerArm": (0.10, -0.10, -0.15),
        "J_Bip_L_Hand": (0.00, 0.00, 0.00),
        "J_Bip_R_UpperArm": (0.45, -0.20, 0.85),
        "J_Bip_R_LowerArm": (0.75, -0.30, 0.45),
        "J_Bip_R_Hand": (0.20, 0.20, 0.10),
        "J_Bip_C_Spine": (0.02, 0.00, 0.05),
        "J_Bip_C_Chest": (0.02, 0.00, 0.03),
        "J_Bip_C_Head": (0.05, 0.03, -0.05),
    },
}


def get_supported_poses() -> list[str]:
    """Return a list of all supported humanoid pose names."""
    return list(SUPPORTED_POSES)


def map_beat_to_pose(role: str, speaker: str) -> str:
    """Map a video beat's role and speaker to an appropriate humanoid pose.

    Args:
        role: Shot or beat role (e.g. 'hook_teaser', 'dialogue', 'hook_intro', 'climax').
        speaker: Name or role of the speaker (e.g. 'Lâm Mặc', 'Người Kể Chuyện').

    Returns:
        One of SUPPORTED_POSES.
    """
    role_str = (role or "").strip().lower()
    spk_str = (speaker or "").strip().lower()

    # 1. Narrator / story teller -> hands_clasped_back (dignified cultivator)
    if "người kể chuyện" in spk_str or "narrator" in spk_str or "narrator" in role_str:
        return "hands_clasped_back"

    # 2. Intro / exposition -> hands_clasped_back
    if role_str in ("hook_intro", "intro", "exposition"):
        return "hands_clasped_back"

    # 3. Dialogue / conversation -> talking
    if role_str in ("dialogue", "talking", "explainer", "conversation"):
        return "talking"

    # 4. Action / teaser / climax
    if role_str in ("hook_teaser", "climax", "action", "combat", "fight"):
        # Swordsman or warrior gets swordsman_ready, others cast_spell
        if "kiếm" in spk_str or "lâm mặc" in spk_str or "warrior" in spk_str or "swordsman" in spk_str:
            return "swordsman_ready"
        return "cast_spell"

    return "idle_stand"


def get_pose_bone_rotations(pose_name: str) -> dict[str, tuple[float, float, float]]:
    """Get bone rotation mapping in radians (XYZ Euler) for a given pose.

    Includes both VRoid naming ('J_Bip_L_UpperArm') and generic humanoid aliases
    ('upperarm_l', etc.).

    Args:
        pose_name: Pose identifier.

    Returns:
        Dict mapping bone names and aliases to (x, y, z) rotation tuples in radians.

    Raises:
        ValueError: If pose_name is not supported.
    """
    if pose_name not in _RAW_POSE_ROTATIONS:
        raise ValueError(f"Unsupported pose '{pose_name}'. Supported poses: {SUPPORTED_POSES}")

    base_dict = _RAW_POSE_ROTATIONS[pose_name]
    full_dict = dict(base_dict)

    # Populate generic aliases so both conventions work seamlessly
    for vroid_name, rot in base_dict.items():
        aliases = BONE_ALIASES.get(vroid_name, [])
        for alias in aliases:
            full_dict[alias] = rot

    return full_dict


def calculate_blink_keyframes(
    start_frame: int,
    end_frame: int,
    fps: int = 30,
    interval_sec: float = 3.2,
) -> list[tuple[int, float]]:
    """Generate facial blink keyframe tuples (frame, shape_key_value).

    Creates natural closed-open blink impulses every `interval_sec` seconds:
    - frame: 0.0 (open)
    - frame + 2: 1.0 (closed)
    - frame + 4: 0.0 (open)

    Args:
        start_frame: Start frame index.
        end_frame: End frame index.
        fps: Frames per second.
        interval_sec: Approximate interval between blinks in seconds (default ~3.2s).

    Returns:
        List of (frame, value) tuples where value is 0.0 or 1.0.
    """
    if end_frame <= start_frame:
        return []

    interval_frames = max(1, int(round(interval_sec * fps)))
    keyframes: list[tuple[int, float]] = []

    curr = start_frame + interval_frames
    while curr + 4 <= end_frame:
        keyframes.append((curr, 0.0))
        keyframes.append((curr + 2, 1.0))
        keyframes.append((curr + 4, 0.0))
        curr += interval_frames

    return keyframes


def euler_to_quaternion(x: float, y: float, z: float) -> tuple[float, float, float, float]:
    """Convert Euler angles (XYZ order in radians) to Quaternion (w, x, y, z)."""
    cx = math.cos(x * 0.5)
    sx = math.sin(x * 0.5)
    cy = math.cos(y * 0.5)
    sy = math.sin(y * 0.5)
    cz = math.cos(z * 0.5)
    sz = math.sin(z * 0.5)

    w = cx * cy * cz + sx * sy * sz
    qx = sx * cy * cz - cx * sy * sz
    qy = cx * sy * cz + sx * cy * sz
    qz = cx * cy * sz - sx * sy * cz
    return (w, qx, qy, qz)


def apply_pose_to_armature(
    armature_obj: Any,
    pose_name: str,
    keyframe: int | None = None,
) -> list[str]:
    """Apply bone rotations for a given pose to a Blender armature object.

    Args:
        armature_obj: Blender Object of type ARMATURE (or mock with pose.bones).
        pose_name: One of SUPPORTED_POSES.
        keyframe: If provided, inserts a keyframe at this frame number.

    Returns:
        List of bone names that were modified.
    """
    rotations = get_pose_bone_rotations(pose_name)
    if not hasattr(armature_obj, "pose") or not hasattr(armature_obj.pose, "bones"):
        return []

    modified_bones: list[str] = []
    pose_bones = armature_obj.pose.bones

    for bone in pose_bones:
        rot = None
        # 1. Exact match
        if bone.name in rotations:
            rot = rotations[bone.name]
        else:
            # 2. Match via alias dictionary
            b_low = bone.name.lower()
            b_clean = b_low.replace("-", "_").replace(" ", "_")
            canonical = ALIAS_TO_CANONICAL.get(b_low) or ALIAS_TO_CANONICAL.get(b_clean)
            if canonical and canonical in rotations:
                rot = rotations[canonical]
            else:
                # 3. Fallback scan
                for k, v in rotations.items():
                    if k.lower().replace("-", "_").replace(" ", "_") == b_clean:
                        rot = v
                        break

        if rot is None:
            continue

        rx, ry, rz = rot
        rot_mode = getattr(bone, "rotation_mode", "QUATERNION")

        if rot_mode == "QUATERNION":
            if mathutils is not None:
                quat = mathutils.Euler((rx, ry, rz), "XYZ").to_quaternion()
            else:
                quat = euler_to_quaternion(rx, ry, rz)
            bone.rotation_quaternion = quat
            if keyframe is not None and hasattr(bone, "keyframe_insert"):
                bone.keyframe_insert(data_path="rotation_quaternion", frame=keyframe)
        else:
            bone.rotation_euler = (rx, ry, rz)
            if keyframe is not None and hasattr(bone, "keyframe_insert"):
                bone.keyframe_insert(data_path="rotation_euler", frame=keyframe)

        modified_bones.append(bone.name)

    return modified_bones


def apply_blink_keyframes_to_mesh(
    face_obj: Any,
    start_frame: int,
    end_frame: int,
    fps: int = 30,
) -> list[str]:
    """Insert procedural blinking keyframes onto mesh shape keys.

    Matches common blink shape key names such as 'Fcl_EYE_Close', 'blink',
    'target_0', 'eye_close', 'Blink_L', 'Blink_R'.

    Args:
        face_obj: Mesh Object (or root object with children) containing shape keys.
        start_frame: Starting frame number.
        end_frame: Ending frame number.
        fps: Animation frames per second.

    Returns:
        List of shape key names that received keyframes.
    """
    keyframes = calculate_blink_keyframes(start_frame, end_frame, fps=fps)
    if not keyframes:
        return []

    # Find candidate mesh objects that have shape_keys
    candidate_objects = []
    if hasattr(face_obj, "data") and hasattr(face_obj.data, "shape_keys"):
        candidate_objects.append(face_obj)

    # If face_obj has children (e.g. root Armature), search children as well
    if hasattr(face_obj, "children"):
        for child in face_obj.children:
            if hasattr(child, "data") and hasattr(child.data, "shape_keys"):
                candidate_objects.append(child)

    modified_keys: list[str] = []

    for obj in candidate_objects:
        shape_keys = getattr(obj.data, "shape_keys", None)
        if not shape_keys:
            continue
        key_blocks = getattr(shape_keys, "key_blocks", [])

        bilateral_candidates = []
        unilateral_candidates = []

        for kb in key_blocks:
            name_lower = kb.name.lower()
            is_unilateral = any(
                tag in name_lower
                for tag in ("_l", "_r", ".l", ".r", "-l", "-r", "left", "right")
            )
            is_blink = (
                "fcl_eye_close" in name_lower
                or "eye_close" in name_lower
                or name_lower == "target_0"
                or "blink" in name_lower
            )
            if is_blink:
                if is_unilateral:
                    unilateral_candidates.append(kb)
                else:
                    bilateral_candidates.append(kb)

        # Prioritize bilateral shape keys to avoid double eyelid deformation
        target_kbs = bilateral_candidates if bilateral_candidates else unilateral_candidates

        for kb in target_kbs:
            for frame, val in keyframes:
                kb.value = val
                if hasattr(kb, "keyframe_insert"):
                    kb.keyframe_insert(data_path="value", frame=frame)
            modified_keys.append(kb.name)

    return modified_keys


# Alias for compatibility with different calling conventions
apply_blink_keyframes = apply_blink_keyframes_to_mesh
