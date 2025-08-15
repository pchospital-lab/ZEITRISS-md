function px_bar(px){
  return '▓'.repeat(px) + '░'.repeat(5 - px);
}
function px_tracker(temp){
  const paradox = 0;
  const remaining = 5 - paradox;
  return `Paradox: ${px_bar(paradox)} · TEMP ${temp} · +1 nach ${remaining} Missionen`;
}
function render_rewards(){
  return 'Rewards rendered';
}
function render_shop_tiers(level=1, faction_rep=0, rift_blueprints=[]){
  const t1 = level >= 1;
  const t2 = level >= 6;
  const t3 = level >= 11 && faction_rep >= 3;
  const bp = rift_blueprints.length;
  return `Shop-Tiers: T1:${t1?'true':'false'} T2:${t2?'true':'false'} T3:${t3?'true':'false'} · BP:${bp}`;
}
function debrief(state){
  return `${render_rewards()}\n${px_tracker(state.temp || 0)}`;
}
function on_command(cmd){
  if(cmd === '!gear shop'){
    return render_shop_tiers(1,0,[]);
  }
  if(cmd === '!px'){
    return px_tracker(0);
  }
  return '';
}
module.exports = { on_command, debrief, render_shop_tiers, px_tracker };
