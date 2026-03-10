const fs = require('fs');
const path = require('path');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

function createDocTextLoader({ root, scopeLabel }) {
  const markdownDocCache = new Map();

  function readText(relPath) {
    return fs.readFileSync(path.join(root, relPath), 'utf8');
  }

  function readMarkdown(relPath, anchors = [/./s], label = `${scopeLabel} (${relPath})`) {
    return resolveUniqueMarkdownTarget({
      root,
      preferredRelPaths: [relPath],
      candidatePathRegex: new RegExp(`${path.basename(relPath).replace('.', '\\.')}$`, 'i'),
      contentPredicates: anchors,
      label
    });
  }

  function getDocText(relPath, anchors = [/./s], label = `${scopeLabel} (${relPath})`) {
    if (!relPath.endsWith('.md')) return readText(relPath);
    if (!markdownDocCache.has(relPath)) {
      const { text } = readMarkdown(relPath, anchors, label);
      markdownDocCache.set(relPath, text);
    }
    return markdownDocCache.get(relPath);
  }

  return {
    readText,
    readMarkdown,
    getDocText
  };
}

module.exports = {
  createDocTextLoader
};
