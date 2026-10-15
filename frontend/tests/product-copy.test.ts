import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import ts from 'typescript';
import { expect, it } from 'vitest';
import { displayText } from '../src/components/ui';

const forbidden = /synthetic|demonstration|dismissed_demo|\bdemo\b/i;
it('has no forbidden static product copy in JSX text or accessible labels', () => {
  const hits: string[] = [];
  function inspect(folder: string) {
    for (const item of readdirSync(folder, { withFileTypes: true })) {
      const path = resolve(folder, item.name);
      if (item.isDirectory()) inspect(path);
      else if (path.endsWith('.tsx')) {
        const source = ts.createSourceFile(
          path,
          readFileSync(path, 'utf8'),
          ts.ScriptTarget.Latest,
          true,
          ts.ScriptKind.TSX,
        );
        function visit(node: ts.Node) {
          if (ts.isJsxText(node) && forbidden.test(node.text)) hits.push(path + ': ' + node.text);
          if (
            ts.isJsxAttribute(node) &&
            /^(title|description|aria-label|placeholder|alt)$/.test(node.name.getText(source)) &&
            node.initializer &&
            ts.isStringLiteral(node.initializer) &&
            forbidden.test(node.initializer.text)
          )
            hits.push(path + ': ' + node.initializer.text);
          ts.forEachChild(node, visit);
        }
        visit(source);
      }
    }
  }
  inspect(resolve(import.meta.dirname, '../src'));
  expect(hits).toEqual([]);
});
it('translates historical presentation labels without altering source data or numbers', () => {
  const original = {
    case_id: 'synthetic-discharge-v1',
    decision: 'dismissed_demo',
    probability: 0.1278216918809014,
  };
  const before = JSON.stringify(original);
  const shown = displayText(before);
  expect(shown).not.toMatch(forbidden);
  expect(shown).toContain('0.1278216918809014');
  expect(JSON.stringify(original)).toBe(before);
});
