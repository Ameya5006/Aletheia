/** Check local Markdown and HTML links in the public presentation documents. */
import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '../..');
const files = [
  'README.md',
  'docs/HIGH_LEVEL_DESIGN.md', 'docs/LOW_LEVEL_DESIGN.md',
  'docs/SOLID_AND_MAINTAINABILITY.md', 'docs/REPOSITORY_CLEANUP.md',
  'docs/LOCAL_DEVELOPMENT.md', 'docs/GITHUB_PRESENTATION.md',
  'docs/REVIEWER_ACCESS.md', 'docs/assets/demo/README.md',
  'docs/ARCHITECTURE.md', 'docs/DEPLOYMENT_ARCHITECTURE.md',
  'docs/EXECUTION_PLAN.md', 'docs/PROJECT_REPORT.md',
  'docs/SUPERVISOR_HANDOFF.md',
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
