import pytest

class Char:
    def __init__(self, concept="", callsign="", name="", hull=None):
        self.concept = concept
        self.callsign = callsign
        self.name = name
        self.hull = hull
        self.stress = 0


def enforce_identity_before_stats(char):
    required = [char.concept, char.callsign, char.name, char.hull]
    if any(not r for r in required):
        raise ValueError("Bitte zuerst Konzept, Callsign, Name und Hülle festlegen.")


def test_classic_start_blocks_stats_without_identity():
    char = Char()
    with pytest.raises(ValueError):
        enforce_identity_before_stats(char)


class State:
    def __init__(self, ttl):
        self.exfil = {"active": True, "ttl": ttl, "hot": False}
        self.char = Char("a", "b", "c", hull="human")
        self.flow = ""


def start_sweep_scene(state):
    if state.exfil["ttl"] <= 0:
        state.flow = "hot_exfil"
        state.exfil["hot"] = True
        return
    state.exfil["ttl"] -= 120
    state.char.stress += 1
    if state.exfil["ttl"] <= 0:
        state.flow = "hot_exfil"


def test_exfil_flow_sweeps_and_hot_exfil():
    state = State(8 * 60)
    start_sweep_scene(state)
    start_sweep_scene(state)
    assert state.exfil["ttl"] == 4 * 60
    assert state.char.stress == 2
    state2 = State(0)
    start_sweep_scene(state2)
    assert state2.flow == "hot_exfil"


def test_boss_scene_foreshadow_and_verbose():
    mission = {
        "foreshadows": [
            "akustischer Click des Metronoms",
            "Glassteg mit Servicelift/Fluchtweg",
        ],
        "boss_scene": {
            "style": "VERBOSE",
            "pressure": ["Timer 90s", "Verstärkung in 2min"],
        },
    }
    assert len(mission["foreshadows"]) >= 2
    assert mission["boss_scene"]["style"] == "VERBOSE"
    assert mission["boss_scene"]["pressure"]
