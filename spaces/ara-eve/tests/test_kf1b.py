from pathlib import Path
import json
import struct

GLB = Path(__file__).resolve().parents[1] / "assets" / "KF1b_anim.glb"

EXPECTED = {
    "Bow",
    "Hit_Head",
    "Idle_Sword",
    "Jump_2",
    "Jump_Land",
    "Kneeling_Tired",
    "Meditate",
    "Sitting_Enter",
    "Sitting_Exit",
}


def _gltf_json(path: Path) -> dict:
    data = path.read_bytes()
    assert data[:4] == b"glTF"
    offset = 12
    clen, ctype = struct.unpack_from("<I4s", data, offset)
    assert ctype == b"JSON"
    return json.loads(data[offset + 8 : offset + 8 + clen])


def test_kf1b_is_rigged_with_nine_clips():
    assert GLB.exists()
    js = _gltf_json(GLB)
    names = {a.get("name") for a in js.get("animations", [])}
    assert names == EXPECTED
    joints = [js["nodes"][i].get("name") for i in js["skins"][0]["joints"]]
    assert "pelvis" in joints and "head" in joints and "thigh_l" in joints


def test_default_session_loads_kf1b():
    from ara_eve.session import new_session

    session = new_session()
    assert session.glb_url.endswith("KF1b_anim.glb")
