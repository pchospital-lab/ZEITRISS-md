const rt = require('../runtime');
rt.StartMission();
console.log(rt.scene_overlay({ index: 0 }));
rt.state.exfil.sweeps = 1;
rt.state.exfil.stress = 2;
console.log(rt.scene_overlay({ index: 0 }));
