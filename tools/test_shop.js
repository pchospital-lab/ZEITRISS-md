const rt = require('../runtime');

function resetState(){
  rt.state.character = { lvl: 1 };
  rt.state.campaign = {
    faction_rep: 0,
    rift_seeds: [],
    rift_blueprints: []
  };
}

function scenario(name, cfg){
  resetState();
  if (typeof cfg.level === 'number'){
    rt.state.character.lvl = cfg.level;
  }
  if (typeof cfg.faction_rep === 'number'){
    rt.state.campaign.faction_rep = cfg.faction_rep;
  }
  if (Array.isArray(cfg.rift_blueprints)){
    rt.state.campaign.rift_blueprints = cfg.rift_blueprints.slice();
  }
  const lvl = rt.state.character.lvl;
  const rep = rt.state.campaign.faction_rep;
  const bps = rt.state.campaign.rift_blueprints;
  const tiers = rt.render_shop_tiers(lvl, rep, bps);
  console.log(`${name}: ${tiers}`);
  console.log(`${name}-cmd: ${rt.on_command('!gear shop')}`);
}

scenario('baseline', { level: 5, faction_rep: 1, rift_blueprints: [] });
scenario('tier3-no-blueprint', { level: 12, faction_rep: 3, rift_blueprints: [] });
scenario('tier3-with-blueprint', { level: 12, faction_rep: 3, rift_blueprints: ['BP-01'] });
