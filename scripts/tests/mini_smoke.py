#!/usr/bin/env python3
"""Lightweight smoke tests for dice, transfer and shop."""

import random


def roll_w6(*_, **__):
    raise RuntimeError("Deprecated: route via roll_check()")


def roll_w10(*_, **__):
    raise RuntimeError("Deprecated: route via roll_check()")


def engine_roll(*_, **__):
    raise RuntimeError("Deprecated RNG: use rng_roll() → roll_check()")


def label_for(count: int, sides: int, exploding: bool) -> str:
    star = "*" if exploding else ""
    return f"{count}W{sides}{star}" if count > 1 else f"W{sides}{star}"


def format_raw_list(raw, max_show: int = 6) -> str:
    if len(raw) <= max_show:
        return "[" + ",".join(map(str, raw)) + "]"
    head = ",".join(map(str, raw[:max_show]))
    return f"[{head},…]"


def rng_roll(num, sides, exploding=False):
    rolls = []
    for _ in range(num):
        r = random.randrange(1, sides + 1)
        rolls.append(r)
        if exploding and r == sides:
            rolls.append(random.randrange(1, sides + 1))
    die_text = label_for(num, sides, exploding)
    if num > 1:
        die_text += " " + format_raw_list(rolls)
    return rolls, die_text


def roll_check(die_text, sg, total, parts, success, raw_rolls, local_debug=False):
    overlay = f"{die_text} {' '.join(parts)} → {total} ≥ SG {sg} ({'Erfolg' if success else 'Fail'})"
    print(overlay)
    if not success and sg is not None and total == sg - 1:
        print('knapp daneben')
    if local_debug:
        print({
            'roll': die_text,
            'raw': raw_rolls,
            'mods': parts,
            'SG': sg,
            'total': total,
            'success': success,
        })


def die_for_attribute(attr_val: int) -> str:
    return "W10*" if attr_val >= 11 else "W6*"


def skill_check(attr, gear, sg, *, local_debug=False):
    die = die_for_attribute(attr)
    rolls, die_text = rng_roll(1, 10, True) if die == "W10*" else rng_roll(1, 6, True)
    total = sum(rolls) + attr + gear
    parts = [f"+{attr} ATTR", f"+{gear} Gear"]
    success = total >= sg
    roll_check(die_text, sg, total, parts, success, rolls, local_debug)
    return success


def deep_merge(base, override):
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


DEFAULT_OUT = (
    "Nullzeit‑Puffer · Transfer 3…2…1 · Redirect: +{hours}h (Self-Collision Guard)"
)
DEFAULT_IN_CORE = "Fenster stabil · {ttl} · Return 3…2…1"
DEFAULT_IN_RIFT = "Resonanzfenster stabil · {ttl} · Return 3…2…1"


def get_transfer_cfg(ctx):
    base = ctx['cfg']['fx']['transfer']
    override = ctx.get('mission', {}).get('fx', {}).get('transfer', {})
    tcfg = deep_merge(base, override)
    tcfg.setdefault("hud_out_template", DEFAULT_OUT)
    tcfg.setdefault("hud_in_template_core", DEFAULT_IN_CORE)
    tcfg.setdefault("hud_in_template_rift", DEFAULT_IN_RIFT)
    return tcfg


def should_show_transfer_enter(ctx, tcfg):
    mode = tcfg.get('on_mission_enter', 'always')
    return (
        mode == 'always'
        or (mode == 'first_session' and ctx.get('session', {}).get('first_mission'))
        or (mode == 'first_episode' and ctx.get('episode', {}).get('first_mission'))
    )


def transfer_out_from_hq(ctx, tcfg):
    hours = tcfg.get('redirect_hours', tcfg.get('redirect_hours_default', 6))
    tpl = tcfg.get("hud_out_template", DEFAULT_OUT)
    if tcfg.get('show_redirect', True):
        print(tpl.format(hours=hours))
    print('...transfer senses...')


def transfer_back_to_hq(state, tcfg, hot=False):
    if hot:
        print('HOT-Exfil · Fenster instabil')
    else:
        tpl_core = tcfg.get("hud_in_template_core", DEFAULT_IN_CORE)
        tpl_rift = tcfg.get("hud_in_template_rift", DEFAULT_IN_RIFT)
        tpl = tpl_rift if state['mission']['mode'] == 'RIFT' else tpl_core
        print(tpl.format(ttl='08s'))
    print('...return senses...')


def reset_exfil_state(state):
    state.setdefault('exfil', {})
    state['exfil']['active'] = False
    state['exfil']['ttl'] = 0
    state['exfil']['hot'] = False
    state.setdefault('flags', {})
    state['flags']['hot_exfil'] = False


def rank_index(rank, order):
    if rank not in order:
        allowed = ", ".join(order)
        raise ValueError(f"Unbekannter Rank '{rank}'. Erlaubt: {allowed}")
    return order.index(rank)


def validate_catalog_ranks(catalog, order):
    for it in catalog:
        mr = it.get('min_rank')
        if mr and mr not in order:
            allowed = ", ".join(order)
            raise ValueError(
                f"Item {it['id']} ('{it['name']}') → min_rank '{mr}' unbekannt. Erlaubt: {allowed}"
            )


def can_purchase(char_rank, item, order):
    mr = item.get('min_rank')
    return True if not mr else rank_index(char_rank, order) >= rank_index(mr, order)


def list_shop_items(char, catalog, order):
    for it in catalog:
        if can_purchase(char['rank'], it, order):
            print(f"{it['name']} · {it['price']} CU")
        else:
            print(
                f"🔒 {it['name']} · {it['price']} CU (erfordert Rank: {it['min_rank']})"
            )


def next_unlocked_rank(char_rank, item_min_rank, order):
    return (
        item_min_rank
        if rank_index(char_rank, order) < rank_index(item_min_rank, order)
        else None
    )


def deny_purchase(char, item, order):
    print('Kauf gesperrt')
    print(f"{item['name']} erfordert Rank: {item['min_rank']}.")
    print(f"Dein Rank: {char['rank']}.")
    nxt = next_unlocked_rank(char['rank'], item['min_rank'], order)
    if nxt:
        print(f"Freigabe bei: {nxt}.")
    print('SFX: ui/deny')


def shop_buy(char, item_id, catalog, order):
    it = next((i for i in catalog if i['id'] == item_id), None)
    if not it:
        print('Unbekannter Artikel.')
        return
    if not can_purchase(char['rank'], it, order):
        deny_purchase(char, it, order)
        return
    print(f"Gekauft: {it['name']} ({it['price']} CU)")


if __name__ == '__main__':
    print('Dice:')
    skill_check(5, 2, 8)
    skill_check(11, 0, 12, local_debug=True)
    raw, die_text = rng_roll(3, 6, True)
    roll_check(die_text, 0, sum(raw), [], True, raw)
    roll_check('W6', 5, 4, [], False, [4])

    print('\nTransfer:')
    ctx = {
        'cfg': {
            'fx': {
                'transfer': {
                    'redirect_hours_default': 6,
                    'hud_out_template': 'Redirect {hours}h',
                    'hud_in_template_core': 'Fenster stabil · {ttl}',
                    'hud_in_template_rift': 'Resonanzfenster stabil · {ttl}',
                }
            }
        },
        'mission': {'fx': {'transfer': {'show_redirect': False}}},
        'session': {'first_mission': True},
        'episode': {'first_mission': True},
    }
    tcfg = get_transfer_cfg(ctx)
    if should_show_transfer_enter(ctx, tcfg):
        transfer_out_from_hq(ctx, tcfg)
    state = {'mission': {'mode': 'RIFT'}, 'exfil': {'active': True, 'ttl': 5, 'hot': False}, 'flags': {}}
    transfer_back_to_hq(state, tcfg, hot=False)
    reset_exfil_state(state)

    print('\nShop:')
    order = ['Operator I', 'Operator II', 'Agent']
    catalog = [{'id': 'lead', 'name': 'Lead Kit', 'price': 100, 'min_rank': 'Operator II'}]
    validate_catalog_ranks(catalog, order)
    char = {'rank': 'Operator I'}
    list_shop_items(char, catalog, order)
    shop_buy(char, 'lead', catalog, order)

