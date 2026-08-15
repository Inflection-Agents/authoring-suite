#!/usr/bin/env python3
"""Flag candidate voice-rule violations in a prose draft (`references/voice-rules.md`).

This checks the mechanical half of the rule list only: the half that's a grep, a count, or a
stdev, not a judgment call. Every finding is a candidate, not a verdict — sentence-length
variance and paragraph length are heuristics with false positives (a genuinely short paragraph
used as a deliberate beat will get flagged), so read the findings rather than auto-fixing them.
Banned words and em dashes are the two checks with no legitimate false positive: if either
fires, the fix is to remove it, not to argue with the flag.

Fenced code blocks and inline code spans are masked before scanning (same length, same line
count, content blanked) so that quoting a banned phrase as an example — the way
`references/voice-rules.md` itself does — never triggers a false positive on itself.

Sentence splitting is a plain regex on `.`/`!`/`?` plus whitespace. It will misfire on
abbreviations ("e.g.", "Dr.") and decimal numbers inside prose; this is a known limitation of
a dependency-free script, not a bug to chase down with a full NLP sentence tokenizer.
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")

EM_DASH_RE = re.compile(r"—")

# Phrases banned wherever they appear in prose.
BANNED_ANYWHERE = [
    "delve into", "leverage", "utilize", "facilitate", "comprehensive", "crucial",
    "essential", "pivotal", "seamless", "powerful", "game-changing", "robust", "empowers",
    "ultimately", "arguably", "in many ways", "to some extent", "it's worth noting",
    "to be clear", "in other words", "simply put", "that said", "with that in mind",
    "needless to say", "in conclusion", "overall", "both approaches have merit",
    "landscape", "tapestry", "realm", "in the realm of", "unlock", "elevate",
    "groundbreaking", "cutting-edge", "transformative", "innovative", "intricate",
    "intricate interplay", "vibrant", "holistic", "bolster", "foster", "harness", "unpack",
    "shed light on", "pave the way", "underscore", "multifaceted", "it cannot be overstated",
    "it is worth mentioning", "it should be considered", "when it comes to", "at its core",
    "at the end of the day", "this is where", "not only",
]

# Phrases banned only as a sentence/paragraph opener.
BANNED_OPENER = [
    "worth noting", "worth crediting", "worth flagging", "so,",
]

# Phrases banned only as a sentence/paragraph closer (a bare hedge, not the phrase itself,
# which is legitimate mid-sentence: "the timeout depends on latency" is fine).
BANNED_CLOSER = ["it depends"]

INTENSIFIER_RE = re.compile(r"\b(very|really|truly|extremely)\b", re.IGNORECASE)
NOT_X_ITS_Y_RE = re.compile(
    r"\b(not|isn'?t|wasn'?t|aren'?t|weren'?t)\b[^.!?\n]{1,60}?[,:—]\s*"
    r"(it'?s|it is|but|instead|that'?s)\b",
    re.IGNORECASE,
)
NEGATION_ASSERTION_RE = re.compile(
    r"\b(is not|isn'?t|was never|wasn'?t)\b[^.!?\n]{1,60}?[.:]\s*"
    r"(it is|it'?s|that was)\b",
    re.IGNORECASE,
)
THAT_IS_X_RE = re.compile(r"(?m)^That is\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
BULLET_LINE_RE = re.compile(r"^\s*([-*]|\d+\.)\s+")
HEADING_RE = re.compile(r"(?m)^#{1,6}\s")


def blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group())


def mask_code(text: str) -> str:
    text = CODE_FENCE_RE.sub(blank, text)
    text = INLINE_CODE_RE.sub(blank, text)
    return text


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def split_sections(text: str) -> list[tuple[int, str]]:
    """(start_line, section_text) pairs, split on markdown headings."""
    starts = [m.start() for m in HEADING_RE.finditer(text)]
    if not starts or starts[0] != 0:
        starts = [0] + starts
    bounds = starts + [len(text)]
    return [
        (line_of(text, bounds[i]), text[bounds[i] : bounds[i + 1]])
        for i in range(len(bounds) - 1)
    ]


def _phrase_re(phrase: str) -> re.Pattern:
    # \s+ between words, not a literal space, so a phrase that happens to wrap across a
    # line break in hand-wrapped markdown still matches.
    return re.compile(r"\s+".join(re.escape(w) for w in phrase.split()), re.IGNORECASE)


def check_banned_words(text: str) -> list[str]:
    findings = []
    for phrase in BANNED_ANYWHERE:
        for m in _phrase_re(phrase).finditer(text):
            findings.append(f"{line_of(text, m.start())}: banned phrase {phrase!r}")
    for para_start, para in split_sections(text):
        offset = 0
        for sentence in SENTENCE_SPLIT_RE.split(para):
            stripped = sentence.strip().lower()
            pos = para_start - 1 + para.count("\n", 0, offset) + 1
            for phrase in BANNED_OPENER:
                if stripped.startswith(phrase):
                    findings.append(f"~{pos}: banned opener {phrase!r}")
            trailing = stripped.rstrip(".!? ")
            for phrase in BANNED_CLOSER:
                if trailing.endswith(phrase):
                    findings.append(f"~{pos}: banned closer {phrase!r}")
            offset = para.find(sentence, offset) + len(sentence)
    return findings


def check_em_dash(text: str) -> list[str]:
    return [f"{line_of(text, m.start())}: em dash" for m in EM_DASH_RE.finditer(text)]


def check_not_x_its_y(text: str) -> list[str]:
    return [
        f"{line_of(text, m.start())}: \"not X, it's Y\" construction: {m.group(0)!r}"
        for m in NOT_X_ITS_Y_RE.finditer(text)
    ]


def check_negation_assertion(text: str) -> list[str]:
    matches = list(NEGATION_ASSERTION_RE.finditer(text))
    if len(matches) > 1:
        return [
            f"{line_of(text, m.start())}: negation-then-assertion "
            f"(#{i + 1} of {len(matches)}, max 1 per document): {m.group(0)!r}"
            for i, m in enumerate(matches)
        ]
    return []


def check_that_is_x(text: str) -> list[str]:
    findings = []
    for _, section in split_sections(text):
        matches = list(THAT_IS_X_RE.finditer(section))
        if len(matches) > 1:
            findings.append(
                f"{line_of(text, section.find(matches[0].group()))}: "
                f'"That is X" used {len(matches)}x in one section, max 1'
            )
    return findings


def check_intensifiers(text: str) -> list[str]:
    words = re.findall(r"\w+", text)
    hits = INTENSIFIER_RE.findall(text)
    if len(words) < 50:
        return []
    density = len(hits) / len(words)
    if density > 0.006:  # roughly 1 per 165 words
        return [f"intensifier density {density:.3%} ({len(hits)} in {len(words)} words)"]
    return []


def check_sentence_variance(text: str) -> list[str]:
    prose_lines = [
        line
        for line in text.splitlines()
        if line.strip() and not BULLET_LINE_RE.match(line) and not HEADING_RE.match(line)
    ]
    prose = " ".join(prose_lines)
    sentences = [s for s in SENTENCE_SPLIT_RE.split(prose) if s.strip()]
    lengths = [len(re.findall(r"\w+", s)) for s in sentences if re.findall(r"\w+", s)]
    if len(lengths) < 6:
        return []
    mean = statistics.mean(lengths)
    stdev = statistics.pstdev(lengths)
    if mean > 0 and stdev / mean < 0.35:
        return [
            f"flat sentence-length rhythm: mean {mean:.1f} words, stdev {stdev:.1f} "
            f"across {len(lengths)} sentences"
        ]
    return []


def check_paragraph_length(text: str) -> list[str]:
    findings = []
    paragraphs = re.split(r"\n\s*\n", text)
    pos = 0
    for para in paragraphs:
        start = text.find(para, pos)
        pos = start + len(para) if start >= 0 else pos
        if BULLET_LINE_RE.match(para.strip()) or HEADING_RE.match(para.strip()):
            continue
        sentence_count = len([s for s in SENTENCE_SPLIT_RE.split(para) if s.strip()])
        if sentence_count > 8:
            findings.append(
                f"{line_of(text, max(start, 0))}: paragraph runs {sentence_count} "
                f"sentences, consider splitting"
            )
    return findings


def check_bullet_ratio(text: str) -> list[str]:
    lines = [
        line
        for line in text.splitlines()
        if line.strip() and not HEADING_RE.match(line) and not line.strip().startswith("```")
    ]
    if len(lines) < 8:
        return []
    bullet_lines = [line for line in lines if BULLET_LINE_RE.match(line)]
    ratio = len(bullet_lines) / len(lines)
    if ratio > 0.6:
        return [f"bullet-heavy: {ratio:.0%} of non-heading lines are list items"]
    return []


CHECKS = [
    check_banned_words,
    check_em_dash,
    check_not_x_its_y,
    check_negation_assertion,
    check_that_is_x,
    check_intensifiers,
    check_sentence_variance,
    check_paragraph_length,
    check_bullet_ratio,
]


def check(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    masked = mask_code(raw)
    findings = []
    for fn in CHECKS:
        for finding in fn(masked):
            findings.append(f"{path}:{finding}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="prose files to check (markdown or text)")
    args = parser.parse_args()

    all_findings: list[str] = []
    for file in args.files:
        path = Path(file)
        if not path.exists():
            all_findings.append(f"{path}: file not found")
            continue
        all_findings.extend(check(path))

    for finding in all_findings:
        print(finding)
    print(f"Summary: {len(args.files)} file(s) checked, {len(all_findings)} finding(s).")
    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
