const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root,
  scopeLabel: 'Upload-Snapshot-Watchguard'
});

const { file, text, source } = readMarkdown(
  'uploads/hard-final-review.md',
  [/Hard Final Review/i],
  'Upload-Snapshot-Watchguard'
);

assert.ok(
  /historischer Snapshot/i.test(text),
  'Upload-Kontext-Drift: hard-final-review.md muss explizit als historischer Snapshot gekennzeichnet sein.'
);
assert.ok(
  /internal\/qa\/process\/known-issues\.md/i.test(text),
  'Upload-Kontext-Drift: hard-final-review.md muss auf internal/qa/process/known-issues.md verweisen.'
);
assert.ok(
  /internal\/qa\/process\/hard-final-review-next-steps\.md/i.test(text),
  'Upload-Kontext-Drift: hard-final-review.md muss auf internal/qa/process/hard-final-review-next-steps.md verweisen.'
);

console.log(`Upload-Snapshot-Watchguard Zielpfad: ${path.relative(root, file)} (${source})`);
console.log('upload-snapshot-watchguard-ok');
