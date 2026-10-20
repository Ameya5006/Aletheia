/** Parse presentation Mermaid blocks with an optional ignored local Mermaid install. */
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { JSDOM } = require('../../frontend/node_modules/jsdom');
const dom = new JSDOM('<!doctype html>');
globalThis.window = dom.window;
globalThis.document = dom.window.document;
const root = resolve(import.meta.dirname, '../..');
const packagePath = resolve(root, 'artifacts/mermaid-validator/node_modules/mermaid/dist/mermaid.core.mjs');
const mermaid = (await import(pathToFileURL(packagePath).href)).default;
mermaid.initialize({ startOnLoad: false });
let checked = 0;
let invalid = 0;
for (const file of ['README.md', 'docs/HIGH_LEVEL_DESIGN.md', 'docs/LOW_LEVEL_DESIGN.md']) {
  const source = readFileSync(resolve(root, file), 'utf8');
  let inFile = 0;
  for (const match of source.matchAll(/\x60{3}mermaid\s*\n([\s\S]*?)\x60{3}/g)) {
    checked++; inFile++;
    try {
      await mermaid.parse(match[1]);
    } catch (error) {
      invalid++;
      console.error(file + ' diagram ' + inFile + ': ' + error.message);
    }
  }
}
console.log(JSON.stringify({ diagrams: checked, valid: checked - invalid, invalid }));
if (invalid) process.exitCode = 1;
