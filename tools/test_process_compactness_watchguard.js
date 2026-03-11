const path = require('path');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root,
  scopeLabel: 'Process-Compactness-Watchguard',
});

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

function lineCount(text) {
  return text.split(/\r?\n/).length;
}

const knownIssues = readMarkdown(
  'internal/qa/process/known-issues.md',
  [
    /Known Issues/i,
  ],
  'known-issues Prozesskompaktheit',
);

const nextSteps = readMarkdown(
  'internal/qa/process/hard-final-review-next-steps.md',
  [
    /Hard-Final-Review/i,
  ],
  'hard-final-review Prozesskompaktheit',
);

const knownIssuesLines = lineCount(knownIssues.text);
const nextStepsLines = lineCount(nextSteps.text);

assert(
  knownIssuesLines <= 50,
  `known-issues.md ist zu lang (${knownIssuesLines} Zeilen, Limit: 50). Datei: ${knownIssues.file}`,
);
assert(
  nextStepsLines <= 30,
  `hard-final-review-next-steps.md ist zu lang (${nextStepsLines} Zeilen, Limit: 30). Datei: ${nextSteps.file}`,
);

assert(
  /issue-pack-complete-summary\.md/.test(knownIssues.text),
  `Archiv-Verweis auf Kompaktzusammenfassung fehlt in ${knownIssues.file}`,
);

assert(
  /issue-pack-complete-summary\.md/.test(nextSteps.text),
  `Archiv-Verweis auf Kompaktzusammenfassung fehlt in ${nextSteps.file}`,
);

console.log('process-compactness-watchguard-ok');
