const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOOLS_DIR = path.join(ROOT, 'tools');

function listWatchguardTests() {
  return fs
    .readdirSync(TOOLS_DIR)
    .filter((file) => /^test_.*watchguard\.js$/.test(file))
    .filter((file) => file !== 'test_watchguard_loader_consistency.js')
    .sort();
}

function readFile(relPath) {
  return fs.readFileSync(path.join(TOOLS_DIR, relPath), 'utf8');
}

function hasDirectMarkdownReadFileSync(text) {
  return /readFileSync\s*\([\s\S]{0,220}\.md(?:["'`]|\s*[,)])/m.test(text);
}

function hasScopeLabelOnLoader(text) {
  return /createDocTextLoader\s*\(\s*\{[\s\S]{0,260}scopeLabel\s*:\s*['"`][^'"`]+['"`]/m.test(text);
}

function getScopeLabelValue(text) {
  const match = text.match(/createDocTextLoader\s*\(\s*\{[\s\S]{0,260}scopeLabel\s*:\s*['"`]([^'"`]+)['"`]/m);
  return match ? match[1].trim() : '';
}

function stripJsComments(text) {
  return text
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/(^|[^:])\/\/.*$/gm, '$1');
}

function normalizeLabelToken(text) {
  return (text || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

function expectedScopeLabelTokenFromFilename(file) {
  return normalizeLabelToken(file.replace(/^test_/, '').replace(/\.js$/, ''));
}

function hasLoaderApiBinding(text) {
  return /const\s*\{[^}]*\b(readMarkdown|getDocText|readText)\b[^}]*\}\s*=\s*createDocTextLoader\s*\(/m.test(text);
}

function hasLoaderApiUsage(text) {
  return /\b(readMarkdown|getDocText|readText)\s*\(/.test(text);
}

function expectedOkTokenFromFilename(file) {
  return file.replace(/^test_/, '').replace(/\.js$/, '').replace(/_/g, '-') + '-ok';
}

function hasExpectedOkToken(text, expectedToken) {
  const matches = [...text.matchAll(/console\.log\(\s*['"`]([^'"`]+)['"`]\s*\)/g)];
  return matches.some((m) => m[1] === expectedToken);
}

const violations = [];

for (const file of listWatchguardTests()) {
  const text = readFile(file);
  const codeText = stripJsComments(text);

  if (/watchguard_file_resolver/.test(codeText)) {
    violations.push(`${file}: nutzt weiterhin watchguard_file_resolver direkt.`);
  }

  if (/resolveUniqueMarkdownTarget\s*\(/.test(codeText)) {
    violations.push(`${file}: ruft resolveUniqueMarkdownTarget(...) direkt auf.`);
  }

  if (/createDocTextLoader/.test(codeText) === false) {
    violations.push(`${file}: bindet createDocTextLoader nicht ein.`);
  }

  if (hasLoaderApiBinding(codeText) === false) {
    violations.push(`${file}: bindet keine Loader-Lese-API (readMarkdown/getDocText/readText) direkt aus createDocTextLoader(...) ein.`);
  }

  if (hasLoaderApiUsage(codeText) === false) {
    violations.push(`${file}: nutzt keine Loader-Lese-API (readMarkdown/getDocText/readText) im Guard-Code.`);
  }

  if (hasScopeLabelOnLoader(codeText) === false) {
    violations.push(`${file}: setzt keinen scopeLabel beim createDocTextLoader(...) (Pflicht für nachvollziehbare Fehlermeldungen).`);
  }

  const scopeLabel = getScopeLabelValue(codeText);
  if (scopeLabel) {
    if (/Watchguard$/i.test(scopeLabel) === false) {
      violations.push(`${file}: scopeLabel muss mit "Watchguard" enden (einheitliche Guard-Diagnostik).`);
    }
    if (/[/\\]/.test(scopeLabel)) {
      violations.push(`${file}: scopeLabel darf keine Slash-Zeichen enthalten (nur Klartext-Label für Logs).`);
    }

    const expectedToken = expectedScopeLabelTokenFromFilename(file);
    const scopeToken = normalizeLabelToken(scopeLabel);
    if (scopeToken !== expectedToken) {
      violations.push(`${file}: scopeLabel muss semantisch zum Dateinamen passen (erwartet Token: ${expectedToken}, gefunden: ${scopeToken}).`);
    }
  }

  if (hasDirectMarkdownReadFileSync(codeText)) {
    violations.push(`${file}: liest .md-Dateien direkt per readFileSync statt Loader.`);
  }

  const expectedOkToken = expectedOkTokenFromFilename(file);
  if (hasExpectedOkToken(codeText, expectedOkToken) === false) {
    violations.push(`${file}: muss das erwartete Ergebnis-Token "${expectedOkToken}" per console.log(...) ausgeben (Smoke-Grep-Kohärenz).`);
  }

}

if (violations.length > 0) {
  console.error('watchguard-loader-consistency-fail');
  for (const line of violations) {
    console.error(`- ${line}`);
  }
  process.exit(1);
}

console.log('watchguard-loader-consistency-ok');
