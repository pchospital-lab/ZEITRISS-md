const gmStyle = process.env.GM_STYLE || 'verbose';
function assert_foreshadow(countNeeded=2, foreshadows=[]){
  if(gmStyle === 'precision'){
    const c = foreshadows.length;
    if(c < countNeeded){
      console.log(`Foreshadow low: ${c}/${countNeeded}`);
    }
  }
}
assert_foreshadow(2, []);
