const path = require('path');
const assert = require('assert');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

const root = path.resolve(__dirname, '..');

const { file, text, source } = resolveUniqueMarkdownTarget({
  root,
  preferredRelPaths: ['uploads/hard-final-review.md'],
  candidatePathRegex: /uploads[\\/].*hard-final-review.*\.md$/i,
  contentPredicates: [/Hard Final Review/i],
  label: 'Upload-Snapshot-Watchguard'
});

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
