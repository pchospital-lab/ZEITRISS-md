const assert = require('assert');

function migrate_save(data) {
  if (!data.save_version) data.save_version = 1;
  if (data.save_version === 1) {
    data.campaign ||= {};
    data.save_version = 2;
  }
  if (data.save_version === 2) {
    data.ui ||= { gm_style: 'verbose' };
    data.save_version = 3;
  }
  return data;
}

function load_deep(json) {
  const data = JSON.parse(json);
  return migrate_save(data);
}

// v1 sample (no save_version)
const v1 = JSON.stringify({ foo: 1 });
// v2 sample
const v2 = JSON.stringify({ save_version: 2, campaign: {} });

assert.equal(load_deep(v1).save_version, 3);
assert.equal(load_deep(v2).save_version, 3);
console.log('save-migration-ok');
