// Usage: node scripts/tokenize.mjs <file> <lang> <firstLine> <lastLine> <out.json>
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {basename, dirname} from 'node:path';
import {codeToTokens} from 'shiki';

const [file, lang, first, last, out] = process.argv.slice(2);
if (!out) {
  console.error('usage: node scripts/tokenize.mjs <file> <lang> <firstLine> <lastLine> <out.json>');
  process.exit(2);
}
const all = readFileSync(file, 'utf8').split('\n');
const code = all.slice(Number(first) - 1, Number(last)).join('\n');
const {tokens} = await codeToTokens(code, {lang, theme: 'github-dark'});
mkdirSync(dirname(out), {recursive: true});
writeFileSync(out, JSON.stringify({
  file: basename(file),
  firstLine: Number(first),
  lines: tokens.map((line) => line.map((t) => ({content: t.content, color: t.color}))),
}));
console.log(`${out}: ${tokens.length} lines`);
