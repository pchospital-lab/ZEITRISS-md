const rt = require('../runtime');
const assert = require('assert');
const dispatcherFixture = require('../internal/qa/fixtures/dispatcher_strings.json');

const dispatcherStrings = rt.DISPATCHER_STRINGS;
assert.deepStrictEqual(dispatcherStrings, dispatcherFixture.strings);

let response = rt.on_command('spiel starten solo');
assert.strictEqual(
  response,
  dispatcherStrings[dispatcherFixture.negativpfade.spiel_starten_solo]
);
const traceLength = rt.state.logs.trace.length;
const lastTrace = rt.state.logs.trace[traceLength - 1];
assert.strictEqual(lastTrace.event, 'dispatch_hint');
assert.strictEqual(lastTrace.channel, dispatcherFixture.trace.channel);
assert.strictEqual(lastTrace.reason, 'start_syntax');
assert.strictEqual(rt.state.logs.flags.dispatch_syntax_hint_seen, true);

response = rt.on_command('spiel starten solo');
assert.strictEqual(response, dispatcherStrings.start_hint);
assert.strictEqual(rt.state.logs.trace.length, traceLength);

response = rt.on_command('spiel starten (solo trigger schnell)');
assert(response.startsWith('Startsyntax aktualisiert'));

response = rt.on_command('!kampagnenmodus trigger');
assert(response.startsWith('Kampagnenmodus gesetzt: TRIGGER'));

response = rt.on_command('spiel starten (solo schnell)');
assert.strictEqual(response, 'solo-trigger-schnell');
assert.strictEqual(rt.state.start.type, 'solo');
assert.strictEqual(rt.state.start.mode, 'schnell');
assert.strictEqual(rt.state.start.seed_mode, 'trigger');
assert.strictEqual(rt.state.campaign.mode, 'trigger');
assert.strictEqual(rt.state.campaign.seed_source, 'trigger');
assert.strictEqual(rt.state.flags.runtime.skip_entry_choice, false);
assert.strictEqual(rt.state.logs.flags.chronopolis_warn_seen, false);

response = rt.on_command('!kampagnenmodus preserve');
assert(response.startsWith('Kampagnenmodus gesetzt: PRESERVE'));

response = rt.on_command('Spiel starten (npc-team 3 classic)');
assert.strictEqual(response, 'npc-team-klassisch');
assert.strictEqual(rt.state.start.type, 'npc-team');
assert.strictEqual(rt.state.start.mode, 'klassisch');
assert.strictEqual(rt.state.start.seed_mode, 'preserve');
assert.strictEqual(rt.state.campaign.mode, 'preserve');
assert.strictEqual(rt.state.campaign.seed_source, 'preserve');
assert.strictEqual(rt.state.team.size, 4);
assert.strictEqual(rt.state.campaign.team_size, 4);
assert.strictEqual(rt.state.team.members.length, 3);

let error = rt.on_command('spiel starten (npc-team 5)');
assert.strictEqual(error, dispatcherStrings.npc_team_size_error);
assert.strictEqual(rt.state.start.type, 'npc-team');
assert.strictEqual(rt.state.team.size, 4);

error = rt.on_command('spiel starten (gruppe 3)');
assert.strictEqual(error, dispatcherStrings.group_number_error);
assert.strictEqual(rt.state.start.type, 'npc-team');

response = rt.on_command('spiel starten (gruppe trigger fast)');
assert(response.startsWith('Kampagnenmodus separat setzen'));

response = rt.on_command('!kampagnenmodus trigger');
assert(response.startsWith('Kampagnenmodus gesetzt: TRIGGER'));

response = rt.on_command('spiel starten (gruppe fast)');
assert.strictEqual(response, 'gruppe-trigger-schnell');
assert.strictEqual(rt.state.start.type, 'gruppe');
assert.strictEqual(rt.state.start.mode, 'schnell');
assert.strictEqual(rt.state.start.seed_mode, 'trigger');
assert.strictEqual(rt.state.campaign.mode, 'trigger');
assert.strictEqual(rt.state.campaign.seed_source, 'trigger');

const help = rt.on_command('!help start');
assert(help.includes('!kampagnenmodus mixed|preserve|trigger'));

rt.on_command('begin mission');
assert.notEqual(rt.state.exfil, null);

console.log('start-ok');
