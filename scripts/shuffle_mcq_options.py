#!/usr/bin/env python3
"""Shuffle MCQ option order so the correct answer is not always B.

Idempotent: canonicalizes (correct first, wrongs by label) then seeded-shuffles.
Run from repo root:
  python3 scripts/shuffle_mcq_options.py
"""
from __future__ import annotations

import hashlib
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BTN_RE = re.compile(r'<button class="qopt"[^>]*>.*?</button>', re.S)
QOPTS_RE = re.compile(r'(<div class="qopts">)(.*?)(</div>)', re.S)


def seed_for(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def shuffle_file(html: str) -> tuple[str, int]:
    changed = 0

    def repl(m: re.Match) -> str:
        nonlocal changed
        open_tag, inner, close = m.group(1), m.group(2), m.group(3)
        buttons = BTN_RE.findall(inner)
        if len(buttons) < 2:
            return m.group(0)
        before = html[max(0, m.start() - 500) : m.start()]
        qm = re.search(r'<p class="qq">(.*?)</p>\s*$', before, re.S)
        qq = re.sub(r"<[^>]+>", "", qm.group(1)).strip() if qm else buttons[0][:60]

        def label(b: str) -> str:
            lm = re.search(r"<span>(.*?)</span>\s*</button>", b, re.S)
            return lm.group(1) if lm else b

        correct = [b for b in buttons if 'data-ok="1"' in b]
        wrongs = sorted([b for b in buttons if 'data-ok="1"' not in b], key=label)
        order = correct + wrongs
        random.Random(seed_for("mcq-v2:" + qq)).shuffle(order)

        bs = list(BTN_RE.finditer(inner))
        lead = inner[: bs[0].start()]
        trail = inner[bs[-1].end() :]
        sep = inner[bs[0].end() : bs[1].start()] if len(bs) >= 2 else ""
        new_inner = lead + sep.join(order) + trail
        if new_inner != inner:
            changed += 1
        return open_tag + new_inner + close

    return QOPTS_RE.sub(repl, html), changed


def main() -> None:
    total = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "discord-feeds" in path.parts:
            continue
        raw = path.read_text(encoding="utf-8")
        if 'class="qopt"' not in raw:
            continue
        new, n = shuffle_file(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            total += n
            print(f"{path.relative_to(ROOT)}: {n}")
    print(f"Shuffled {total} quizzes")


if __name__ == "__main__":
    main()
