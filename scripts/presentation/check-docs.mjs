/** Check local Markdown and HTML links in the public presentation documents. */
import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '../..');
const files = [
  'README.md',
  'docs/HIGH_LEVEL_DESIGN.md', 'docs/LOW_LEVEL_DESIGN.md',
  'docs/SOLID_AND_MAINTAINABILITY.md',
  'docs/LOCAL_DEVELOPMENT.md',
  'docs/REVIEWER_ACCESS.md', 'docs/assets/demo/README.md',
  'docs/ARCHITECTURE.md', 'docs/DEPLOYMENT_ARCHITECTURE.md',
  'docs/LOCAL_DOCKER_CLEANUP.md', 'docs/PROJECT_REPORT.md',
];
const missing = [];
let checked = 0;
for (const file of files) {
  const source = readFileSync(resolve(root, file), 'utf8');
  const stripped = source.replace(/```[\s\S]*?```/g, '');
  const links = [...stripped.matchAll(/!?\[[^\]]*\]\(([^)]+)\)|(?:href|src)="([^"]+)"/g)];
  for (const match of links) {
    let target = (match[1] ?? match[2]).trim().replace(/^<|>$/g, '');
    if (/^(?:https?:|mailto:|data:|#)/i.test(target)) continue;
    target = decodeURIComponent(target.split('#')[0]);
    if (!target) continue;
    checked++;
    if (!existsSync(resolve(root, dirname(file), target))) missing.push(file + ' -> ' + target);
  }
}
if (missing.length) {
  for (const item of missing) console.error(item);
  process.exitCode = 1;
}
console.log(JSON.stringify({ documents: files.length, local_links: checked, missing: missing.length }));
