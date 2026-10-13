import { spawnSync } from 'node:child_process';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
const root = resolve(import.meta.dirname, '../..');
mkdirSync(resolve(root, 'artifacts/stage2-verification'), { recursive: true });
const python =
  process.env.ALETHEIA_PYTHON ||
  resolve(root, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
const result = spawnSync(python, [resolve(import.meta.dirname, 'export-contract.py')], {
  cwd: root,
  encoding: 'utf8',
});
if (result.status !== 0) {
  process.stderr.write(result.stderr || String(result.error));
  process.exit(1);
}
const generated = JSON.parse(
  readFileSync(resolve(root, 'artifacts/stage2-verification/openapi.json'), 'utf8'),
);
const baseline = resolve(import.meta.dirname, '../contracts/openapi.json');
const samples = JSON.parse(
  readFileSync(resolve(root, 'artifacts/stage2-verification/public-responses.json'), 'utf8'),
);
for (const response of Object.values(samples))
  response.request_id = '00000000-0000-4000-8000-000000000001';
const responses = resolve(import.meta.dirname, '../tests/real-api-responses.json');
if (process.argv.includes('--write')) {
  mkdirSync(resolve(import.meta.dirname, '../contracts'), { recursive: true });
  writeFileSync(baseline, JSON.stringify(generated, null, 2) + '\n');
  writeFileSync(responses, JSON.stringify(samples, null, 2) + '\n');
} else if (
  JSON.stringify(generated) !== JSON.stringify(JSON.parse(readFileSync(baseline, 'utf8')))
) {
  throw new Error('FastAPI contract drift: review schemas/routes before updating the snapshot.');
}
if (JSON.stringify(samples) !== JSON.stringify(JSON.parse(readFileSync(responses, 'utf8'))))
  throw new Error('Published FastAPI response drift: review mappings before updating fixtures.');
console.log(result.stdout.trim());
console.log('FastAPI OpenAPI contract matches the frontend snapshot.');
