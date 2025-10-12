const assert = require('assert');

function freshRuntime(){
  delete require.cache[require.resolve('../runtime')];
  return require('../runtime');
}

function setupHighTierAgent(rt){
  rt.startSolo('klassisch');
  rt.state.character.id = 'qa-high-tier';
  rt.state.character.name = 'QA High-Tier';
  rt.state.character.rank = 'Chief';
  rt.state.character.lvl = 18;
  rt.state.character.research_level = 4;
  rt.state.campaign.research_level = 4;
  rt.state.campaign.faction_rep = 4;
  rt.state.campaign.rift_blueprints = ['rift-core', 'arena-scout'];
  rt.state.economy = { credits: 20000 };
  rt.on_command('!chrono reset');
}

function verifyChronopolisStock(){
  const rt = freshRuntime();
  setupHighTierAgent(rt);
  const report = rt.chronopolisStockReport();
  const lines = report.split('\n');
  assert.ok(lines[0].startsWith('Chronopolis · Tagesangebot'), 'Chronopolis-Header fehlt');
  const categories = new Set();
  lines.forEach((line) => {
    if (line.startsWith('— ') && line.endsWith(' —')){
      categories.add(line.slice(2, -2));
    }
  });
  assert.ok(categories.has('Temporal Ships'), 'Temporal Ships fehlen im Report');
  assert.ok(categories.has('Never-Was Gadgets'), 'Never-Was Gadgets fehlen im Report');
  assert.ok(categories.has('Era-Skins'), 'Era-Skins fehlen im Report');
  const locked = lines.filter((line) => line.startsWith('🔒'));
  assert.strictEqual(locked.length, 0, 'High-Tier-Agent: Angebot enthält noch gesperrte Items');
  return { report };
}

function verifyMarketLog(){
  const rt = freshRuntime();
  setupHighTierAgent(rt);
  const purchase = rt.log_market_purchase('Quantum-Flashbang', 500, {
    timestamp: '2025-06-28T12:00:00Z',
    px_delta: -2,
    source: 'QA-Protokoll',
    note: 'Hochstufen-Stichprobe'
  });
  assert.strictEqual(purchase.item, 'Quantum-Flashbang');
  assert.strictEqual(purchase.cost_cu, 500);
  assert.strictEqual(purchase.px_clause, 'Px -2');
  assert.strictEqual(rt.state.logs.market.length, 1, 'Markt-Log sollte genau einen Eintrag führen');
  const [entry] = rt.state.logs.market.slice(-1);
  assert.ok(entry.timestamp && entry.timestamp.includes('2025-06-28'), 'Timestamp fehlt im Markt-Log');
  assert.strictEqual(entry.note, 'Hochstufen-Stichprobe');
  assert.strictEqual(entry.source, 'QA-Protokoll');
  const formatted = [`${entry.timestamp}`, `${entry.item}`, `${entry.cost_cu} CU`, entry.px_clause, entry.note, `Quelle ${entry.source}`]
    .filter(Boolean)
    .join(' · ');
  return { purchase, formatted };
}

function main(){
  const stock = verifyChronopolisStock();
  const market = verifyMarketLog();
  console.log('Chronopolis-Report:\n', stock.report);
  console.log('Letzter Markt-Eintrag:', market.purchase);
  console.log('Chronopolis-Trace (formatiert):', market.formatted);
}

if (require.main === module){
  main();
}

module.exports = {
  verifyChronopolisStock,
  verifyMarketLog
};
