#!/usr/bin/env python3
"""Lightweight smoke tests for dice, transfer and shop."""

import random


def rng_roll(num, sides, exploding=False):
    rolls = []
    for _ in range(num):
        r = random.randrange(1, sides + 1)
        rolls.append(r)
        if exploding and r == sides:
            rolls.append(random.randrange(1, sides + 1))
    die_text = f"{num}W{sides}{'*' if exploding else ''}"
    return rolls, die_text


def roll_check(die_text, sg, total, parts, success, raw_rolls, local_debug=False):
    overlay = f"{die_text} {' '.join(parts)} → {total} ≥ SG {sg} ({'Erfolg' if success else 'Fail'})"
    print(overlay)
    if local_debug:
        print({
            'roll': die_text,
            'raw': raw_rolls,
            'mods': parts,
            'SG': sg,
            'total': total,
            'success': success,
        })


def skill_check(attr, gear, sg, use_w10=False, local_debug=False):
    rolls, die_text = rng_roll(1, 10, True) if use_w10 else rng_roll(1, 6, True)
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


def get_transfer_cfg(ctx):
    base = ctx['cfg']['fx']['transfer']
    override = ctx.get('mission', {}).get('fx', {}).get('transfer', {})
    return deep_merge(base, override)


def should_show_transfer_enter(ctx, tcfg):
    mode = tcfg.get('on_mission_enter', 'always')
    return (
        mode == 'always'
        or (mode == 'first_session' and ctx.get('session', {}).get('first_mission'))
        or (mode == 'first_episode' and ctx.get('episode', {}).get('first_mission'))
    )


def transfer_out_from_hq(ctx, tcfg):
    hours = tcfg.get('redirect_hours', tcfg.get('redirect_hours_default', 6))
    if tcfg.get('show_redirect', True):
        print(tcfg['hud_out_template'].format(hours=hours))
    print('...transfer senses...')


def transfer_back_to_hq(state, tcfg, hot=False):
    if hot:
        print('HOT-Exfil · Fenster instabil')
    else:
        tpl = (
            tcfg['hud_in_template_rift']
            if state['mission']['mode'] == 'RIFT'
            else tcfg['hud_in_template_core']
        )
        print(tpl.format(ttl='08s'))
    print('...return senses...')


def rank_index(rank, order):
    if rank not in order:
        raise ValueError(f'Unbekannter Rank: {rank}')
    return order.index(rank)


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


def deny_purchase(item):
    print(f"Kauf gesperrt: {item['name']} erfordert Rank {item['min_rank']}.")
    print('SFX: ui/deny')


def shop_buy(char, item_id, catalog, order):
    it = next((i for i in catalog if i['id'] == item_id), None)
    if not it:
        print('Unbekannter Artikel.')
        return
    if not can_purchase(char['rank'], it, order):
        deny_purchase(it)
        return
    print(f"Gekauft: {it['name']} ({it['price']} CU)")


if __name__ == '__main__':
    print('Dice:')
    skill_check(5, 2, 8)
    skill_check(11, 0, 12, use_w10=True, local_debug=True)

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
    state = {'mission': {'mode': 'RIFT'}}
    transfer_back_to_hq(state, tcfg, hot=False)

    print('\nShop:')
    order = ['Operator I', 'Operator II', 'Agent']
    catalog = [{'id': 'lead', 'name': 'Lead Kit', 'price': 100, 'min_rank': 'Operator II'}]
    char = {'rank': 'Operator I'}
    list_shop_items(char, catalog, order)
    shop_buy(char, 'lead', catalog, order)

