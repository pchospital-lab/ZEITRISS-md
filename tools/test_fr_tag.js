const rt = require('../runtime');
rt.StartMission();
const idx = parseInt(process.argv[2] || '1', 10) - 1;
console.log(rt.scene_overlay({ index: idx }));
