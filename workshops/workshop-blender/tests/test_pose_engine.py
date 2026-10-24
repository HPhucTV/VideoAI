import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add workshop-blender to sys.path
wb_dir = Path(__file__).resolve().parent.parent
if str(wb_dir) not in sys.path:
    sys.path.insert(0, str(wb_dir))

from pose_engine import (
    SUPPORTED_POSES,
    get_supported_poses,
    map_beat_to_pose,
    get_pose_bone_rotations,
    calculate_blink_keyframes,
    apply_pose_to_armature,
    apply_blink_keyframes_to_mesh,
    apply_blink_keyframes,
)


def test_get_supported_poses():
    poses = get_supported_poses()
    expected = {"idle_stand", "hands_clasped_back", "cast_spell", "swordsman_ready", "talking"}
    assert expected.issubset(set(poses))
    assert poses == SUPPORTED_POSES


def test_map_beat_to_pose():
    # Hook teaser -> tư thế xuất chiêu hoặc thủ kiếm
    assert map_beat_to_pose("hook_teaser", "Lâm Mặc") in ["cast_spell", "swordsman_ready"]
    assert map_beat_to_pose("hook_teaser", "Vân Hy") in ["cast_spell", "swordsman_ready"]

    # Dialogue / đàm đạo -> talking
    assert map_beat_to_pose("dialogue", "Lâm Mặc") == "talking"
    assert map_beat_to_pose("talking", "Nhân Vật A") == "talking"
    assert map_beat_to_pose("explainer", "Nhân Vật B") == "talking"

    # Người dẫn truyện / intro / cao nhân -> hands_clasped_back
    assert map_beat_to_pose("hook_intro", "Người Kể Chuyện") == "hands_clasped_back"
    assert map_beat_to_pose("intro", "Lâm Mặc") == "hands_clasped_back"
    assert map_beat_to_pose("dialogue", "Narrator") == "hands_clasped_back"
    assert map_beat_to_pose("narrator_shot", "Ai Đó") == "hands_clasped_back"

    # Climax / action
    assert map_beat_to_pose("climax", "Lâm Mặc") in ["cast_spell", "swordsman_ready"]
    assert map_beat_to_pose("action", "Vân Hy") in ["cast_spell", "swordsman_ready"]

    # Unknown role & speaker fallback
    assert map_beat_to_pose("unknown", "unknown") == "idle_stand"
    assert map_beat_to_pose("", "") == "idle_stand"


def test_get_pose_bone_rotations():
    # All 5 core poses must return valid rotation dicts
    for pose in ["idle_stand", "hands_clasped_back", "cast_spell", "swordsman_ready", "talking"]:
        rotations = get_pose_bone_rotations(pose)
        assert isinstance(rotations, dict)
        assert len(rotations) > 0

        # Must support VRoid and/or generic humanoid bone names
        assert "J_Bip_L_UpperArm" in rotations or "upperarm_l" in rotations
        assert "J_Bip_R_UpperArm" in rotations or "upperarm_r" in rotations

        # Each rotation must be a tuple of 3 floats (radians)
        arm_rot = rotations.get("J_Bip_L_UpperArm") or rotations.get("upperarm_l")
        assert isinstance(arm_rot, (tuple, list))
        assert len(arm_rot) == 3
        assert all(isinstance(v, (int, float)) for v in arm_rot)

        # Upper arm downward rotation should be significant from T-pose (abs > 0.5 rad)
        assert max(abs(v) for v in arm_rot) > 0.5, f"Pose {pose} arm rotation too subtle from T-pose"

    # Invalid pose should raise ValueError
    with pytest.raises(ValueError):
        get_pose_bone_rotations("non_existent_pose")


def test_calculate_blink_keyframes():
    start_frame = 1
    end_frame = 300
    fps = 30

    keyframes = calculate_blink_keyframes(start_frame, end_frame, fps=fps)
    assert len(keyframes) > 0

    # Verify tuple structure and value range
    for frame, value in keyframes:
        assert isinstance(frame, int)
        assert isinstance(value, float)
        assert 0.0 <= value <= 1.0
        assert start_frame <= frame <= end_frame

    # Find blink peak frames (value == 1.0)
    peaks = [frame for frame, val in keyframes if val == 1.0]
    assert len(peaks) >= 2, "Expected multiple blinks in 300 frames (10s)"

    # Verify intervals between consecutive blinks (~2.5 to 4.0 seconds)
    for i in range(len(peaks) - 1):
        interval_frames = peaks[i + 1] - peaks[i]
        interval_sec = interval_frames / fps
        assert 2.5 <= interval_sec <= 4.0, f"Blink interval {interval_sec}s outside realistic range"

    # Verify blink cycle: 0.0 -> 1.0 -> 0.0
    for peak in peaks:
        before = [v for f, v in keyframes if f == peak - 2]
        after = [v for f, v in keyframes if f == peak + 2]
        assert before == [0.0], f"Expected eye open 2 frames before peak {peak}"
        assert after == [0.0], f"Expected eye open 2 frames after peak {peak}"

    # Edge cases
    assert calculate_blink_keyframes(100, 100) == []
    assert calculate_blink_keyframes(100, 50) == []


def test_apply_pose_to_armature_mock():
    # Create mock bone
    bone_l_arm = MagicMock()
    bone_l_arm.name = "J_Bip_L_UpperArm"
    bone_l_arm.rotation_mode = "QUATERNION"
    bone_l_arm.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)

    bone_spine = MagicMock()
    bone_spine.name = "J_Bip_C_Spine"
    bone_spine.rotation_mode = "XYZ"
    bone_spine.rotation_euler = (0.0, 0.0, 0.0)

    mock_armature = MagicMock()
    mock_armature.type = "ARMATURE"
    mock_armature.pose.bones = [bone_l_arm, bone_spine]

    # Test apply pose without keyframe
    modified_bones = apply_pose_to_armature(mock_armature, "hands_clasped_back")
    assert "J_Bip_L_UpperArm" in modified_bones
    assert bone_l_arm.rotation_quaternion != (1.0, 0.0, 0.0, 0.0)
    assert not bone_l_arm.keyframe_insert.called

    # Test apply pose with keyframe
    modified_bones_kf = apply_pose_to_armature(mock_armature, "cast_spell", keyframe=45)
    assert "J_Bip_L_UpperArm" in modified_bones_kf
    bone_l_arm.keyframe_insert.assert_called_with(data_path="rotation_quaternion", frame=45)
    bone_spine.keyframe_insert.assert_called_with(data_path="rotation_euler", frame=45)


def test_apply_blink_keyframes_mock():
    # Mock face mesh with shape keys
    shape_key_block = MagicMock()
    shape_key_block.name = "Fcl_EYE_Close"
    shape_key_block.value = 0.0

    mock_mesh = MagicMock()
    mock_mesh.data.shape_keys.key_blocks = [shape_key_block]

    result = apply_blink_keyframes_to_mesh(mock_mesh, start_frame=1, end_frame=150, fps=30)
    assert "Fcl_EYE_Close" in result
    assert shape_key_block.keyframe_insert.called

    # Test alias apply_blink_keyframes
    assert apply_blink_keyframes == apply_blink_keyframes_to_mesh


def test_apply_blink_keyframes_bilateral_priority():
    # When both bilateral and unilateral shape keys exist, only bilateral should be keyed
    kb_bilateral = MagicMock()
    kb_bilateral.name = "Fcl_EYE_Close"
    kb_bilateral.value = 0.0

    kb_left = MagicMock()
    kb_left.name = "Blink_L"
    kb_left.value = 0.0

    kb_right = MagicMock()
    kb_right.name = "Blink_R"
    kb_right.value = 0.0

    mock_mesh = MagicMock()
    mock_mesh.data.shape_keys.key_blocks = [kb_bilateral, kb_left, kb_right]

    result = apply_blink_keyframes_to_mesh(mock_mesh, start_frame=1, end_frame=150, fps=30)
    assert result == ["Fcl_EYE_Close"]
    assert kb_bilateral.keyframe_insert.called
    assert not kb_left.keyframe_insert.called
    assert not kb_right.keyframe_insert.called


def test_apply_blink_keyframes_unilateral_fallback():
    # When only unilateral shape keys exist, both left and right should be keyed
    kb_left = MagicMock()
    kb_left.name = "Blink_L"
    kb_left.value = 0.0

    kb_right = MagicMock()
    kb_right.name = "Blink_R"
    kb_right.value = 0.0

    mock_mesh = MagicMock()
    mock_mesh.data.shape_keys.key_blocks = [kb_left, kb_right]

    result = apply_blink_keyframes_to_mesh(mock_mesh, start_frame=1, end_frame=150, fps=30)
    assert set(result) == {"Blink_L", "Blink_R"}
    assert kb_left.keyframe_insert.called
    assert kb_right.keyframe_insert.called

