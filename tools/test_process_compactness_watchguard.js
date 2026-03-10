const path = require('path');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

const root = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

function lineCount(text) {
  return text.split(/\r?\n/).length;
}

const knownIssues = resolveUniqueMarkdownTarget({
  root,
  preferredRelPaths: ['internal/qa/process/known-issues.md'],
  candidatePathRegex: /known-issues\.md$/i,
  contentPredicates: [
    /Known Issues & Triage-Prozess/i,
    /internal\/qa\/process\/archive\/known-issues-durchlaufhistorie-73-156\.md/i,
  ],
});

const nextSteps = resolveUniqueMarkdownTarget({
  root,
  preferredRelPaths: ['internal/qa/process/hard-final-review-next-steps.md'],
  candidatePathRegex: /hard-final-review-next-steps\.md$/i,
  contentPredicates: [
    /Hard-Final-Review\s*–\s*Anschlussübersicht/i,
    /Offene Anschluss-Tasks/i,
  ],
});

const knownIssuesLines = lineCount(knownIssues.text);
const nextStepsLines = lineCount(nextSteps.text);

assert(
  knownIssuesLines <= 220,
  `known-issues.md ist zu lang für den Triage-Einstieg (${knownIssuesLines} Zeilen, Limit: 220). Datei: ${knownIssues.file}`,
);
assert(
  nextStepsLines <= 260,
  `hard-final-review-next-steps.md ist zu lang für die Anschlussübersicht (${nextStepsLines} Zeilen, Limit: 260). Datei: ${nextSteps.file}`,
);

assert(
  /internal\/qa\/process\/archive\/known-issues-durchlaufhistorie-73-156\.md/.test(knownIssues.text),
  `Archiv-Verweis fehlt in ${knownIssues.file}`,
);
assert(
  /internal\/qa\/process\/hard-final-review-next-steps\.md/.test(knownIssues.text),
  `Prozess-Verweis auf hard-final-review-next-steps.md fehlt in ${knownIssues.file}`,
);
assert(
  /Pflicht-Smoke/i.test(nextSteps.text),
  `Pflicht-Smoke-Hinweis fehlt in ${nextSteps.file}`,
);

console.log('process-compactness-watchguard-ok');
