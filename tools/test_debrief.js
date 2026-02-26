const rt = require('../runtime');

rt.state.character = {
  lvl: 4,
  rank: 'Operator I',
  cooldowns: {},
  attributes: { TEMP: 2 }
};
rt.state.campaign = {
  paradoxon_index: 2,
  missions_since_px: 1,
  rift_seeds: [],
  rift_blueprints: [],
  research_level: 0,
  chronopolis_missions_since_reset: 0,
  chronopolis_tick_modulo: 3
};
rt.state.economy = { credits: 1800 };

const out = rt.debrief({
  temp: 2,
  cu_reward: 450,
  level_before: 3,
  level_after: 4,
  stabilized: true
});

console.log(out);

if (!/Chrono Units \+450 CU/.test(out)){
  throw new Error('Chrono-Units-Zeile fehlt.');
}
if (!/Level-Up 3→4/.test(out)){
  throw new Error('Level-Up fehlt.');
}
if (!/Resonanz Px 3\/5 \(\+1 pro Mission\)/.test(out)){
  throw new Error('Resonanz-Zeile fehlt.');
}
