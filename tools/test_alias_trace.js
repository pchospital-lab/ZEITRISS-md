const rt = require('../runtime');

console.log(rt.on_command('!alias clear'));
console.log(rt.on_command('!alias log Vega|Dr. Lang|aktiv|Kontakt gehalten'));
console.log(rt.on_command('!alias log persona=Rook|cover=Archivarin|status=exposed|note=Backup aktiviert|mission=M5|scene=3'));
console.log(rt.on_command('!alias status'));
console.log(rt.on_command('!radio clear'));
console.log(rt.on_command('!radio log Echo|ops|Feindkontakt gesichtet|warnung'));
console.log(rt.on_command('!radio log speaker=Nova|channel=med|message=Verletzte sichern|status=ok|scene=4|note=Medbay inbound'));
console.log(rt.on_command('!radio status'));
