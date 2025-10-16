const rt = require('../runtime');
try {
  rt.radio_tx({ device: null, range_m: 50 });
} catch (e) {
  console.log(e.message);
}
