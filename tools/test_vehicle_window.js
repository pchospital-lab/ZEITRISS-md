const rt = require('../runtime');

function assertMatch(haystack, needle, msg){
  if (!haystack.includes(needle)){
    throw new Error(`${msg}\nErwartet: ${needle}\nIst: ${haystack}`);
  }
}

rt.state.character = {
  lvl: 4,
  rank: 'Operator I',
  cooldowns: {},
  attributes: { TEMP: 2 }
};
rt.state.campaign = {
  paradoxon_index: 2,
  missions_since_px: 1,
  mission: 2,
  rift_seeds: [],
  rift_blueprints: [],
  research_level: 0,
  chronopolis_missions_since_reset: 0,
  chronopolis_tick_modulo: 3
};

const normal = rt.debrief({ temp: 2, cu_reward: 0, stabilized: true });
assertMatch(normal, 'Fahrzeugfenster · TEMP 2 · Rhythmus 4',
  'Standard-Debrief muss normale Fensterlogik anzeigen.');

const byClass = rt.debrief({
  temp: 2,
  cu_reward: 0,
  stabilized: true,
  vehicle_class: 'TECH_IV_TEMPORAL',
  source: 'chronopolis_legendary'
});
assertMatch(byClass, 'Fahrzeugfenster · Ausnahme aktiv',
  'Tech-IV-Kontext via vehicle_class/source muss Ausnahme aktivieren.');

const nestedVehicle = rt.debrief({
  temp: 2,
  cu_reward: 0,
  stabilized: true,
  vehicle: { class: 'temporal_ship' }
});
assertMatch(nestedVehicle, 'Fahrzeugfenster · Ausnahme aktiv',
  'Verschachtelter vehicle-Kontext muss Ausnahme aktivieren.');

const nestedContext = rt.debrief({
  temp: 2,
  cu_reward: 0,
  stabilized: true,
  vehicle_context: { vehicle_type: 'temporal_ship' }
});
assertMatch(nestedContext, 'Fahrzeugfenster · Ausnahme aktiv',
  'vehicle_context.vehicle_type muss Ausnahme aktivieren.');

console.log('test_vehicle_window: ok');
