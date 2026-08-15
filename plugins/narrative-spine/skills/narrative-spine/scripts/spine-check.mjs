#!/usr/bin/env node
/**
 * spine-check.mjs - narrative spine linter
 *
 *   node spine-check.mjs spine.md
 *   node spine-check.mjs "deck/My Deck.dc.html"
 *   node spine-check.mjs spine.md --quiet     (skip the read-through, lint only)
 *
 * Prints the title-only read-through (the governing test), then lints the spine.
 * Dependency-free. Exit 0 clean, 1 errors found, 2 bad usage.
 */

import { readFileSync, existsSync } from 'node:fs';
import { basename, extname } from 'node:path';

// ------------------------------------------------------------ connectives
const CONNECTIVES = [
  // move, matcher
  ['concession',     /^(despite|even (with|though|as)|although|while [a-z]+ (is|are|was|provides|gives))/i],
  ['escalation',     /\b(is|are|was|were) \w*\s?(compounded|magnified|multiplied|worsened|amplified)\b|^simultaneously\b|^at the same time\b|^worse\b/i],
  ['consequence',    /^(as a result|because|consequently|the result|so that|therefore|which means)/i],
  ['resolution',     /^to (break|fix|solve|end|escape|reverse|stop)\b/i],
  ['taxonomy',       /^to .{0,60}\bwe must separate\b|^(there are|we split|we separate)\b/i],
  ['mechanism',      /^(to (make|ensure|maximi[sz]e|achieve|enable|unlock|satisfy|support|keep|allow|preserve|reduce|isolate|guarantee)|we achieve this|we do this)\b/i],
  ['instantiation',  /^(for example|for instance|concretely|take\b|consider\b)/i],
  ['extension',      /^(this .{0,40}\bextends\b|the same (holds|applies|is true)|likewise|equally)/i],
  ['causation',      /^(because|since|as .{0,40}\b(is|are)\b)/i],
  ['evidence',       /^(we already|today,? |in practice|.{0,30}\balready (does|do|shows?|proves?)\b)/i],
  ['implication',    /^(by |with |once |after )/i],
  ['objection',      /^while\b/i],
  ['quantification', /\b(toward|to) zero\b|\bby \d|\d+\s*(%|percent|x)\b/i],
  ['ask',            /^to (unlock|ignite|start|fund|begin|deliver)\b.*\bwe (require|need|ask)\b|\bwe (require|need|are asking for)\b/i],
  ['sequence',       /^(next|then|finally|first|second|third)\b/i],
  // Anaphoric reference: pointing back at what the previous slide established.
  // The most common connective in a tight deck, and easy to miss when reading
  // for explicit conjunctions only.
  ['anaphora',       /^(this|that|these|those|each|every|both|such|inside (this|these)|within (this|these))\b/i],
];

const JARGON = [
  'hexagonal', 'micro-frontend', 'microfrontend', 'federated', 'abac', 'rbac',
  'idempotent', 'choreograph', 'orchestrat', 'kubernetes', 'k8s', 'sidecar',
  'eventual consistency', 'cqrs', 'saga', 'bff', 'service mesh', 'multi-tenan',
  'serverless', 'sovereign cell', 'blast radius', 'iac', 'cdk', 'ci/cd',
];

const HYPE = ['revolutionary', 'game-chang', 'world-class', 'best-in-class',
              'seamless', 'synergy', 'cutting-edge', 'paradigm', 'turnkey',
              'next-generation', 'state-of-the-art'];

const HEDGE = ['could potentially', 'might possibly', 'we may want to',
               'perhaps we should', 'it seems that', 'sort of', 'kind of'];

// ------------------------------------------------------------ extraction
function fromDeck(s) {
  const out = [];
  const sections = s.split(/<section\b/).slice(1);
  for (const p of sections) {
    const num = /data-screen-label="([^"]*)"/.exec(p);
    const lab = /data-label="([^"]*)"/.exec(p);
    const notes = /data-speaker-notes="([^"]*)"/.exec(p);
    const strip = (x) => x.replace(/<[^>]+>/g, ' ')
                          .replace(/&amp;/g, '&').replace(/&#183;/g, '-')
                          .replace(/&[a-z]+;/g, ' ')
                          .replace(/\s+/g, ' ').trim();
    const eb = /\.Eyebrow"[^>]*>([\s\S]*?)<\/x-import>/.exec(p);
    const ti = /\.SlideTitle"[^>]*>([\s\S]*?)<\/x-import>/.exec(p);
    out.push({
      n: num ? num[1] : String(out.length + 1),
      label: lab ? lab[1] : '',
      kicker: eb ? strip(eb[1]) : '',
      title: ti ? strip(ti[1]) : '',
      notes: notes ? notes[1].trim() : '',
    });
  }
  return out;
}

function fromSpine(s) {
  const out = [];
  const blocks = s.split(/^###\s+/m).slice(1);
  for (const b of blocks) {
    const head = b.split('\n')[0].trim();
    const g = (k) => {
      const m = new RegExp(`^-\\s*\\*\\*${k}:\\*\\*\\s*([\\s\\S]*?)(?=\\n-\\s*\\*\\*|\\n###|$)`, 'mi').exec(b);
      return m ? m[1].replace(/\s+/g, ' ').trim() : '';
    };
    const n = (/^(\d+)/.exec(head) || [, String(out.length + 1)])[1];
    out.push({ n, label: head, kicker: g('Kicker'), title: g('Title'),
               link: g('Link'), brief: g('Brief'), notes: g('Notes'),
               diagram: g('Diagram') });
  }
  return out;
}

// ------------------------------------------------------------ cohesion
const STOP = new Set(['this','that','these','those','with','from','into','their','there',
  'which','while','where','when','what','have','been','were','will','must','they','them',
  'than','then','also','only','every','each','more','most','same','such','over','under',
  'across','because','before','after','about','through','without','using','make','makes',
  'made','does','done','both','our','ours','your','the','and','for','are','was','not']);
const stem = (w) => w.toLowerCase().replace(/(ing|ed|es|s)$/, '');
const terms = (t) => new Set(
  (t.toLowerCase().match(/[a-z][a-z-]{3,}/g) || [])
    .filter((w) => !STOP.has(w)).map(stem).filter((w) => w.length >= 4));
function cohesion(prev, cur) {
  const a = terms(prev), b = terms(cur);
  return [...b].filter((w) => a.has(w));
}

// ------------------------------------------------------------ reporting
let ERRORS = 0, WARNINGS = 0;
const err  = (m) => { ERRORS++;   console.log(`  ERROR  ${m}`); };
const warn = (m) => { WARNINGS++; console.log(`  warn   ${m}`); };

// ------------------------------------------------------------ main
const argv = process.argv.slice(2);
const quiet = argv.includes('--quiet');
const file = argv.find((a) => !a.startsWith('--'));
if (!file) { console.error('usage: spine-check.mjs <spine.md | deck.dc.html> [--quiet]'); process.exit(2); }
if (!existsSync(file)) { console.error(`not found: ${file}`); process.exit(2); }

const src = readFileSync(file, 'utf8');
const isDeck = extname(file) === '.html' || src.includes('<x-dc>');
const slides = isDeck ? fromDeck(src) : fromSpine(src);

if (!slides.length) {
  console.error('no slides found. For a spine, use "### NN - Name" blocks with **Kicker:** and **Title:** lines.');
  process.exit(2);
}

const content = slides.filter((s) => s.title && !/^(cover|title|vision|closing|contact|thank)/i.test(s.label + ' ' + s.kicker));

// ---- the governing test ----------------------------------------------
console.log(`\n${basename(file)}  ${slides.length} slides, ${content.length} content slides`);

if (!quiet) {
  console.log('\n' + '='.repeat(76));
  console.log('TITLE-ONLY READ-THROUGH  (must read as one persuasive paragraph)');
  console.log('='.repeat(76) + '\n');
  const para = content.map((s) => s.title.replace(/\s+/g, ' ').trim())
                      .map((t) => (/[.!?]$/.test(t) ? t : t + '.')).join(' ');
  // wrap at 76
  let line = '';
  for (const w of para.split(' ')) {
    if ((line + ' ' + w).trim().length > 76) { console.log(line.trim()); line = w; }
    else line += ' ' + w;
  }
  if (line.trim()) console.log(line.trim());
  console.log('\n' + '='.repeat(76));
}

console.log('\nLINT\n');

// ---- house style (whole document) -------------------------------------
if (src.includes('—')) {
  const n = (src.match(/—/g) || []).length;
  err(`${n} em dash(es). House style: comma, colon, semicolon, parentheses, or a new sentence.`);
}
const emoji = src.match(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu);
if (emoji) warn(`${emoji.length} emoji found. The system is matte and serious.`);

// ---- per slide ---------------------------------------------------------
const kickers = new Map();
const unfilled = [];
let mapAt = -1;
content.forEach((s, i) => {
  const tag = `[${s.n}${s.label ? ' ' + s.label.replace(/^\d+\s*-\s*/, '') : ''}]`;
  const t = s.title.trim();

  if (!s.kicker) warn(`${tag} no kicker. The reader loses their place in the argument.`);
  if (!t) { err(`${tag} no title.`); return; }

  // Unfilled template placeholders: report once, then skip prose checks that
  // would only be measuring the placeholder.
  if (/<[^>]+>/.test(t)) { unfilled.push(s.n); return; }

  // A title is a sentence, not a label. The two reliable tells of a label are
  // brevity and Title Case; a verb whitelist is too brittle to lead with.
  const wordsArr = t.split(/\s+/);
  const words = wordsArr.length;
  const capRatio = wordsArr.slice(1).filter((w) => /^[A-Z]/.test(w)).length / Math.max(1, words - 1);
  if (words < 6) {
    err(`${tag} title is ${words} words: "${t}". A title is a full sentence carrying a claim, not a label.`);
  } else if (capRatio > 0.6) {
    err(`${tag} title is Title Case: "${t}". Titles are sentence case; Title Case turns a claim back into a label.`);
  }
  if (words > 38) warn(`${tag} title is ${words} words. Target 20 to 32, two lines at presentation size.`);
  if (/\band also\b/i.test(t) || (t.match(/\band\b/gi) || []).length >= 3) {
    warn(`${tag} title may carry more than one idea. If it needs "and also", it is two slides.`);
  }

  // Connective. An explicit opener is best; failing that, lexical cohesion with
  // the previous title (a shared, meaningful noun) still binds the two slides.
  // Only a title with neither is a true orphan.
  if (i > 0) {
    const move = CONNECTIVES.find(([, re]) => re.test(t));
    if (!move) {
      const shared = cohesion(content[i - 1].title, t);
      if (!shared.length) {
        warn(`${tag} orphan: no connective and no shared term with the previous slide. "${t.slice(0, 54)}..."`);
      }
    }
  }

  // kicker hygiene
  if (s.kicker) {
    const k = s.kicker.trim();
    const isSignpost = /[-·]|dimension|part\s+(one|two)/i.test(k);
    if (k.split(/\s+/).length > (isSignpost ? 7 : 5)) {
      warn(`${tag} kicker "${k}" is long. One to four words, or up to seven for a branch signpost.`);
    }
    if (/[.!?]$/.test(k)) warn(`${tag} kicker ends with punctuation. It is a label, not a sentence.`);
    const kl = k.toLowerCase();
    const tl = t.toLowerCase();
    if (kl.length > 6 && tl.includes(kl)) {
      warn(`${tag} kicker "${k}" repeats inside the title. The kicker should add position, not content.`);
    }
    const seen = kickers.get(kl);
    if (seen && !/dimension|part|section/i.test(kl)) {
      warn(`${tag} kicker "${k}" already used at slide ${seen}. Kickers are unique unless signposting a branch.`);
    }
    kickers.set(kl, s.n);
    if (/dimension|two dimensions|the map/i.test(kl) && mapAt < 0) mapAt = i;
  }

  // jargon in titles
  const jl = JARGON.filter((j) => t.toLowerCase().includes(j));
  if (jl.length) {
    warn(`${tag} jargon in the title (${jl.join(', ')}). Keep it only if the audience already uses the word.`);
  }

  // hype and hedging
  for (const h of HYPE) if (t.toLowerCase().includes(h)) warn(`${tag} hype word "${h}".`);
  for (const h of HEDGE) if (t.toLowerCase().includes(h)) err(`${tag} hedged claim "${h}". Commit, or state the uncertainty as a fact.`);

  // passive with no actor
  if (/\b(it was decided|will be (reduced|improved|delivered)|are (built|created) )\b/i.test(t) && !/\bwe\b/i.test(t)) {
    warn(`${tag} passive with no actor. Name who does it.`);
  }

  // notes
  if (isDeck && !s.notes) warn(`${tag} no speaker notes.`);
  // diagram claim must equal the title
  if (s.diagram && s.diagram.replace(/[.\s]+$/, '') !== t.replace(/[.\s]+$/, '')
      && !/^<.*>$/.test(s.diagram)) {
    err(`${tag} diagram claim differs from the title. They must match verbatim, or the picture wins.`);
  }
});

// ---- map signposting ---------------------------------------------------
if (mapAt >= 0) {
  const after = content.slice(mapAt + 1);
  const signposted = after.filter((s) => /dimension|part\s+(one|two|1|2)/i.test(s.kicker || '')).length;
  if (signposted === 0) {
    err(`a map was declared at slide ${content[mapAt].n} but no later slide signposts its branch. A declared and abandoned map is worse than none.`);
  } else if (signposted < 2) {
    warn(`only ${signposted} slide signposts a branch after the map. Both branches need announcing.`);
  }
}

// ---- template placeholders ---------------------------------------------
if (unfilled.length) {
  console.log(`  info   ${unfilled.length} slide(s) still hold <placeholders> (${unfilled.join(', ')}); prose checks skipped for those.`);
}

// ---- ask ---------------------------------------------------------------
const hasAsk = content.some((s) => /\b(we (require|need|are asking)|the ask|the investment)\b/i.test(s.title + ' ' + s.kicker));
if (!hasAsk) warn('no Ask beat detected. A deck with no specific ask leaves the room undecided.');

// ---- summary -----------------------------------------------------------
console.log(`\n${ERRORS} error(s), ${WARNINGS} warning(s)`);
if (!ERRORS && !WARNINGS) console.log('clean');
process.exit(ERRORS > 0 ? 1 : 0);
