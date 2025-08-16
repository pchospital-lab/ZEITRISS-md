const rt = require('../runtime');
try {
  rt.radio_tx({ device: null, range: 50 });
} catch (e) {
  console.log(e.message);
}
