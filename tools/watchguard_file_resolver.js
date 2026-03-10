const fs = require('fs');
const path = require('path');
const assert = require('assert');

function walk(dir, ignoreDirPattern = /^\.git$/) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory() && ignoreDirPattern.test(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full, ignoreDirPattern));
    else out.push(full);
  }
  return out;
}

function resolveUniqueMarkdownTarget({
  root,
  preferredRelPaths = [],
  candidatePathRegex = /.*/i,
  contentPredicates = [],
  label = 'Watchguard'
}) {
  const normalize = (p) => path.normalize(path.isAbsolute(p) ? p : path.join(root, p));

  for (const relPath of preferredRelPaths) {
    const fullPath = normalize(relPath);
    if (!fs.existsSync(fullPath)) continue;
    const text = fs.readFileSync(fullPath, 'utf8');
    if (contentPredicates.every((predicate) => predicate.test(text))) {
      return { file: fullPath, text, source: 'preferred' };
    }
  }

  const candidates = walk(root)
    .filter((p) => p.endsWith('.md'))
    .filter((p) => candidatePathRegex.test(path.relative(root, p)));

  const hits = candidates
    .map((file) => ({ file, text: fs.readFileSync(file, 'utf8') }))
    .filter(({ text }) => contentPredicates.every((predicate) => predicate.test(text)));

  assert.ok(hits.length > 0, `${label}: Kein passendes Markdown-Ziel gefunden.`);
  assert.ok(
    hits.length === 1,
    `${label}: Mehrdeutige Zielpfade gefunden (${hits.map((h) => path.relative(root, h.file)).join(', ')}).`
  );

  return { ...hits[0], source: 'fallback-scan' };
}

module.exports = {
  resolveUniqueMarkdownTarget
};
