import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
const root = resolve(import.meta.dirname, '..');
const pkg = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'));
for (const [name, version] of Object.entries({ ...pkg.dependencies, ...pkg.devDependencies })) {
  const installed = JSON.parse(
    readFileSync(resolve(root, 'node_modules', name, 'package.json'), 'utf8'),
  );
  if (installed.version !== version) throw new Error(`Dependency drift: ${name}`);
  if (!installed.license) throw new Error(`Missing licence metadata: ${name}`);
  console.log(`${name}@${version}: ${installed.license}`);
}
