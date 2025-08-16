const rt = require('../runtime');
try {
  rt.radio_rx({ device: null, range: 50 });
} catch (e) {
  console.log(e.message);
}
