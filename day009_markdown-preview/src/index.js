#!/usr/bin/env node
import { readFileSync } from 'fs';
import { resolve, extname } from 'path';
import { renderMarkdown } from './renderer.js';

const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  console.log(`
Usage: mdp <file.md> [options]

Options:
  -h, --help    Show this help message

Examples:
  mdp README.md
  mdp ./docs/guide.md
`);
  process.exit(args.length === 0 ? 1 : 0);
}

const filePath = resolve(args[0]);

if (extname(filePath) !== '.md' && extname(filePath) !== '.markdown') {
  console.error(`Error: "${args[0]}" is not a Markdown file (.md or .markdown)`);
  process.exit(1);
}

let source;
try {
  source = readFileSync(filePath, 'utf-8');
} catch (err) {
  if (err.code === 'ENOENT') {
    console.error(`Error: File not found — "${filePath}"`);
  } else {
    console.error(`Error: Could not read file — ${err.message}`);
  }
  process.exit(1);
}

if (source.trim() === '') {
  console.error('Error: File is empty');
  process.exit(1);
}

const output = renderMarkdown(source);
process.stdout.write(output + '\n');
