const assert = require('assert');
const rt = require('../runtime');

let thrownError;
assert.throws(
  () => rt.radio_rx({ device: null, range_m: 50 }),
  (error) => {
    thrownError = error;
    return error instanceof Error && error.message.includes('CommsCheck failed');
  },
  'radio_rx sollte bei fehlendem Comms-Setup eine CommsCheck-Fehlermeldung werfen.'
);

assert.ok(thrownError, 'radio_rx muss im Fehlerpfad eine Exception liefern.');
assert.ok(
  thrownError.message.startsWith('CommsCheck failed: require valid device/range or relay/jammer override.'),
  'Fehlertext muss auf die Comms-Validierung hinweisen.'
);

console.log(thrownError.message);

assert.doesNotThrow(() => {
  const result = rt.radio_rx({ device: 'comlink', range_m: 2000 });
  assert.strictEqual(result, 'rx');
});

console.log('comms-rx-ok');
