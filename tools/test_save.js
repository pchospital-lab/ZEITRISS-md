const rt = require('../runtime');
const assert = require('assert');

const json = rt.save_deep();
const data = JSON.parse(json);
assert.equal(data.save_version, 3);
try {
  rt.save_deep({ ...rt.state, location: 'FIELD' });
} catch (e) {
  console.log(e.message);
}
assert.equal(rt.migrate_save({}).save_version, 3);
console.log('save-ok');
