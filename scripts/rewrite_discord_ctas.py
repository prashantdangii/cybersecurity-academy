#!/usr/bin/env python3
"""Rewrite Discord unlock CTAs → Academy Discord updates/ops home.

Run from repo root:
  python3 scripts/rewrite_discord_ctas.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Whop already grants Discord on subscribe/trial. Deep-link into the server.
# Swap for a permanent discord.gg invite anytime (one constant below).
DISCORD = "https://discord.com/channels/1449813215788797954"
OLD_CHECKOUT = "https://whop.com/checkout/3Ugn8Q3jNpHU2kPeEN-0Xm3-uqfq-nck6-mRWOKnNAVQNB/"

BLURB_MAP = [
    (
        "Clear missions here — then unlock job alerts, reviews, and gated content on Discord.",
        "Missions live on this page. Open Discord for chapter drops, daily drills, and job channels.",
    ),
    (
        "Tap join to unlock the full academy community.",
        "You’re already in — open Discord for updates, feeds, and community check-ins.",
    ),
    (
        "Live coaching, job alerts, and gated drops unlock inside Discord.",
        "Daily drills, job alerts, and chapter updates land in Discord.",
    ),
    (
        "Unlock job channels, intro reviews, and hiring threads on Discord.",
        "Post intros, get reviews, and track jobs in Discord.",
    ),
    (
        "Unlock mock interview channels and mentor feedback on Discord.",
        "Practice interviews and get feedback in Discord.",
    ),
    (
        "Unlock study groups and accountability threads on Discord.",
        "Study groups and accountability streaks live in Discord.",
    ),
    (
        "Unlock private program tips and live hunts on Discord.",
        "Share hunts (in-scope) and tips in Discord bounty channels.",
    ),
    (
        "Unlock recon playbooks and live target reviews on Discord.",
        "Recon playbooks and peer reviews live in Discord.",
    ),
    (
        "Get report reviews from mentors on Discord before you submit.",
        "Get report reviews in Discord before you submit.",
    ),
    (
        "Unlock advanced hunt sessions and private tips on Discord.",
        "Advanced hunt sessions and tips land in Discord.",
    ),
    (
        "Unlock client leads and intro threads on Discord.",
        "Freelance intros and lead threads live in Discord.",
    ),
    (
        "Unlock contract templates discussion on Discord.",
        "Contract / SOW discussions happen in Discord.",
    ),
    (
        "Get portfolio reviews on Discord.",
        "Get portfolio reviews in Discord.",
    ),
    (
        "Disclosure mentoring unlocks on Discord.",
        "Disclosure mentoring and peer review happen in Discord.",
    ),
]


def rewrite_text(s: str) -> str:
    s = s.replace(OLD_CHECKOUT, DISCORD)
    s = s.replace("Unlock on Discord", "Open Discord")
    s = s.replace("Join &amp; unlock →", "Open Discord →")
    s = s.replace("Join & unlock →", "Open Discord →")
    s = s.replace(
        '<span class="t">Join the academy</span>',
        '<span class="t">Academy HQ</span>',
    )
    s = s.replace(
        '<span class="t">Jobs & mentors</span>',
        '<span class="t">Updates & jobs</span>',
    )
    s = s.replace("Jobs · mentor help · gated labs", "Chapter drops · Q&A · check-ins")
    s = s.replace("Jobs · mentors · gated labs", "Updates · drills · jobs lounge")
    s = s.replace("Apply · reviews · gated drops.", "Feeds · reviews · job lounge.")
    s = s.replace("Open checkout · unlock now", "New chapters · daily drills")
    s = s.replace(
        "Jobs · mentors · gated labs — join to unlock",
        "Updates · drills · jobs lounge",
    )

    for old, new in BLURB_MAP:
        s = s.replace(old, new)

    s = s.replace("gated labs", "daily drills")
    s = s.replace("gated content", "chapter updates")
    s = s.replace("gated drops", "chapter drops")
    s = s.replace("member-only drops", "chapter drops")
    s = s.replace(
        "Join via the unlock button and post.",
        "Open Discord and post your intro.",
    )
    s = s.replace(
        "Unlock the next drops + community on Discord.",
        "Continue in Discord for updates, drills, and the next chapter drops.",
    )
    s = s.replace(
        "Save proof in <code class=\"inl\">lab-notes.md</code>. Unlock the next drops + community on Discord.",
        "Save proof in <code class=\"inl\">lab-notes.md</code>. Open Discord for updates and the next chapter drops.",
    )
    return s


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "discord-feeds" in path.parts or "node_modules" in path.parts:
            continue
        raw = path.read_text(encoding="utf-8")
        new = rewrite_text(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    for rel in ("README.md", "_gen_full_course.py"):
        path = ROOT / rel
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        new = rewrite_text(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(rel)

    print(f"Updated {len(changed)} files")
    for c in changed:
        print(" ", c)


if __name__ == "__main__":
    main()
