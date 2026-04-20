import { test } from 'node:test';
import assert from 'node:assert/strict';
import { renderMarkdown } from './renderer.js';

function stripAnsi(str) {
  return str.replace(/\x1b\[[0-9;]*m/g, '');
}

test('H1 見出しを含む', () => {
  const out = stripAnsi(renderMarkdown('# タイトル'));
  assert.ok(out.includes('# タイトル'), `actual: ${out}`);
});

test('H2 見出しを含む', () => {
  const out = stripAnsi(renderMarkdown('## セクション'));
  assert.ok(out.includes('## セクション'));
});

test('段落テキストをそのまま出力する', () => {
  const out = stripAnsi(renderMarkdown('Hello world'));
  assert.ok(out.includes('Hello world'));
});

test('太字が含まれる', () => {
  const out = stripAnsi(renderMarkdown('**bold**'));
  assert.ok(out.includes('bold'));
});

test('インラインコードが含まれる', () => {
  const out = stripAnsi(renderMarkdown('`code`'));
  assert.ok(out.includes('code'));
});

test('コードブロックの内容が含まれる', () => {
  const out = stripAnsi(renderMarkdown('```js\nconsole.log("hi");\n```'));
  assert.ok(out.includes('console.log("hi");'));
});

test('順序なしリストの項目が含まれる', () => {
  const out = stripAnsi(renderMarkdown('- apple\n- banana'));
  assert.ok(out.includes('apple'));
  assert.ok(out.includes('banana'));
});

test('順序付きリストが指定開始番号から始まる', () => {
  const out = stripAnsi(renderMarkdown('3. third\n4. fourth'));
  assert.ok(out.includes('3.'), `actual: ${out}`);
  assert.ok(out.includes('4.'));
});

test('テーブルのヘッダーと内容が含まれる', () => {
  const out = stripAnsi(renderMarkdown('| A | B |\n|---|---|\n| 1 | 2 |'));
  assert.ok(out.includes('A'));
  assert.ok(out.includes('1'));
});

test('CJK テーブルが切り詰められない', () => {
  const md = '| 言語 | 説明 |\n|------|------|\n| JavaScript | Web フロントエンド |\n';
  const out = stripAnsi(renderMarkdown(md));
  assert.ok(out.includes('JavaScript'), `actual: ${out}`);
  assert.ok(out.includes('Web フロントエンド'), `actual: ${out}`);
});

test('水平線が含まれる', () => {
  const out = stripAnsi(renderMarkdown('---'));
  assert.ok(out.includes('─'));
});

test('引用ブロックの内容が含まれる', () => {
  const out = stripAnsi(renderMarkdown('> 引用テキスト'));
  assert.ok(out.includes('引用テキスト'));
});
