function scene_overlay(scene, fr){
  const segs = ['HUD'];
  if(scene === 1 && fr){
    segs.push(' · FR:' + fr);
  }
  return segs.join('');
}
const arg = process.argv[2];
if(arg === '1'){
  console.log(scene_overlay(1, 'ruhig'));
}else{
  console.log(scene_overlay(2, 'ruhig'));
}
