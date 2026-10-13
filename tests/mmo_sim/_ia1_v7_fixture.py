"""Canonical SYNTHETIC IA-1 test data only; never migrate actual game saves.
No product mocks, validator bypass, actual-output conversion or network access.
"""
from __future__ import annotations
import copy
from functools import lru_cache
import json
from pathlib import Path
from jsonschema.validators import validator_for

_ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = _ROOT / 'internal/qa/fixtures/savegame_v7_5er_hq_highlevel.json'

@lru_cache(maxsize=1)
def _validators():
    result = []
    for name in ('saveGame.v7.schema.json', 'saveGame.v7.export.schema.json'):
        schema = json.loads((_ROOT / 'systems/gameflow' / name).read_text(encoding='utf-8'))
        # The pinned schemas have only local fragment references; disallow remote retrieval.
        def check_refs(value):
            if isinstance(value, dict):
                if '$ref' in value and not value['$ref'].startswith('#'):
                    raise AssertionError('Nonlocal test-schema reference')
                for nested in value.values():
                    check_refs(nested)
            elif isinstance(value, list):
                for nested in value:
                    check_refs(nested)
        check_refs(schema)
        cls = validator_for(schema)
        cls.check_schema(schema)
        result.append(cls(schema))
    return tuple(result)

def _assert_valid(save: dict) -> None:
    for validator in _validators():
        validator.validate(save)
    assert len(save['characters']) == 1
    char = save['characters'][0]
    assert save['economy']['wallets'][char['id']]['balance'] == char['wallet']

def make_v7_fixture(char_id: str, name: str, *, lvl: int = 1,
                    save_id: str | None = None, **extra) -> dict:
    """Full v7 fixture with the same synthetic ID/name/level as the old test."""
    if extra:
        raise AssertionError('IA-1 reference has no extra fixture fields')
    save = json.loads(_TEMPLATE.read_text(encoding='utf-8'))
    char = copy.deepcopy(save['characters'][0])
    char.update(id=char_id, name=name, callsign=name.upper(), lvl=lvl, xp=0,
                rank='Test', origin={'role': 'Synthetische IA-1-Testfigur'},
                wallet=0, equipment=[], talents=[], implants=[], history={},
                carry=[], quarters_stash=[], reputation={}, sys_installed=0,
                has_psi=False, level_history={})
    for key in ('psi_heat', 'pp', 'psi_abilities'):
        char.pop(key, None)
    save['characters'] = [char]
    save['economy']['wallets'] = {char_id: {'balance': 0}}
    save['save_id'] = save_id if save_id is not None else f'fixture-{char_id}'
    _assert_valid(save)
    return save

def advance_v7_fixture(save: dict, *, lvl: int, wallet: int, equipment: list) -> None:
    """Replace only the former in-memory .update fixture step, not a product call.
    Same level, monetary amount and marker list; both canonical wallet locations
    stay consistent. Caller still publishes using the original real store API.
    """
    _assert_valid(save)
    char = save['characters'][0]
    char.update(lvl=lvl, wallet=wallet, equipment=copy.deepcopy(equipment))
    save['economy']['wallets'][char['id']]['balance'] = wallet
    _assert_valid(save)
