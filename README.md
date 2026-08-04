# Cybersecurity Academy — Whop pages

Standalone HTML learning pages embedded in a Whop community as **Web app** / **Content** apps.

## Rules for this repo

- **One self-contained file per page.** Inline `<style>` and `<script>`. No external CSS, JS, fonts, or images — pages must render inside a Whop iframe with nothing else fetched.
- **No build step.** What's in the repo is what ships.
- **Mobile first.** Whop is used heavily on phones. Every page must be readable at 360px wide.
- **Never link to a page that doesn't exist.** Use the `.ncard.soon` / `.soon` badge markup instead.
- **Visual over verbal.** No block of body copy longer than ~4 lines. If you're writing a paragraph, check whether a `.flow`, `.layers`, `.tiles`, `.vs` or `.chips` component says it better. Prose that genuinely can't be cut goes inside a collapsed `<details class="more">`.

## How a page behaves

Both `start-here.html` and every lesson are **step players**, not scrolling documents:

- One screen at a time, driven by a sticky **Back / Next** bar at the bottom. Arrow keys work.
- A dot rail at the top shows every step; tap any dot to jump. The 3px bar at the very top is overall progress.
- State persists in `localStorage` (step position, lab checkboxes, quiz answers), wrapped in `try/catch` because Whop iframes can block storage.
- Deep links work: `#s3` opens step 3, `#plan` / `#map` on Start Here.
- Finishing the last step reveals a completion screen with counts and the next lesson.

`start-here.html` specifically is a funnel: hero → 5 visual questions → a **generated** roadmap (track, ordered lesson list with hours, phase weeks, milestone dates) → copyable Discord intro. The track scoring lives in `decide()`; the curriculum lives in the `CORE` / `TRACKS` / `GOALS` objects at the top of its script — **that's the single source of truth, update it when a page ships.**

## Structure

```
index.html                      redirect → start-here.html (so the repo root works as a landing page)
start-here.html                 the roadmap + track selector; entry point for everything
_template.html                  master template — copy this to make a new page
cybercore/                      foundations (mandatory for all tracks)
web-application-security/       offense
penetration-testing/            offense
exploit-development/            offense
vulnerability-research/         offense — advanced, after everything else
defensive-security/             defense
grc/                            governance, risk, compliance
ai-security/                    AI/LLM security
bug-bounty/                     outcome track — any base track
freelancing/                    outcome track — any base track
career/                         resume, interviews, certs
community/                      wins wall
```

## Making a new page

1. Copy `_template.html` into the right folder.
2. Set `data-track` on `<html>` — this picks the accent colour: `core` `offense` `defense` `grc` `ai` `bounty` `freelance` `career`.
3. Fill every `<!-- FILL: ... -->` marker.
4. Each step is one `<section class="lesson" data-title="…" data-desc="…" hidden>`. IDs (`s1`…`sN`) and the intro path list are generated from these — don't hand-write them. Keep the step count equal to the content outline.
5. Per step, use: `Concept` (short + a visual component), `Command`/`Payload` (`pre.code`, runnable, never pseudocode), `Lab` (`ul.chk` checkboxes, one verifiable action each, with `.labtgt` naming the authorized target), `Check yourself` (`div.quiz` — mark the right option `data-ok="1"` and give **every** option a `data-why`).
6. Fill the completion screen's next-lesson cards: next page in this track, the matching outcome page (career / bounty / freelance), and back to Start Here.
7. Add the page to the `CORE` / `TRACKS` / `GOALS` data in `start-here.html` — set its `h:` to the real path so it stops rendering as "soon".

### Visual components available

`.tiles` (numbers/facts) · `.flow` (step→step→step, vertical on mobile) · `.layers` (OSI, memory layout, kill chain) · `.vs` (attacker vs defender, weak vs strong) · `.chips` (vocabulary) · `.term` (expected output, non-copyable) · `.note` / `.note.tip` / `.note.legal` · `.tw > table` (comparisons only) · `details.more` (collapsed deep dive).

## Configuration

`start-here.html` has a `LINKS` object in its `<script>`:

```js
var LINKS = {
  discord: "https://whop.com/checkout/3Ugn8Q3jNpHU2kPeEN-0Xm3-uqfq-nck6-mRWOKnNAVQNB/"
};
```

## Hosting on GitHub Pages

Settings → Pages → deploy from branch `main`, folder `/ (root)`.

**Base:** `https://prashantdangi1.github.io/cybersecurity-academy/`

Paste the module URLs below into Whop Web app embeds. Internal links are relative.

### Module URLs (Whop embeds)

#### Entry
- https://prashantdangi1.github.io/cybersecurity-academy/
- https://prashantdangi1.github.io/cybersecurity-academy/start-here.html
- https://prashantdangi1.github.io/cybersecurity-academy/community/discord-hub.html

#### CyberCore
- https://prashantdangi1.github.io/cybersecurity-academy/cybercore/networking-fundamentals.html
- https://prashantdangi1.github.io/cybersecurity-academy/cybercore/linux-command-line-essentials.html
- https://prashantdangi1.github.io/cybersecurity-academy/cybercore/cybersecurity-essentials.html
- https://prashantdangi1.github.io/cybersecurity-academy/cybercore/secure-java-development.html

#### Web Application Security
- https://prashantdangi1.github.io/cybersecurity-academy/web-application-security/web-attacks.html
- https://prashantdangi1.github.io/cybersecurity-academy/web-application-security/advanced-web-attacks.html
- https://prashantdangi1.github.io/cybersecurity-academy/web-application-security/api-security-testing.html

#### Penetration Testing
- https://prashantdangi1.github.io/cybersecurity-academy/penetration-testing/penetration-testing.html
- https://prashantdangi1.github.io/cybersecurity-academy/penetration-testing/network-penetration-testing.html
- https://prashantdangi1.github.io/cybersecurity-academy/penetration-testing/active-directory-attacks.html
- https://prashantdangi1.github.io/cybersecurity-academy/penetration-testing/evasion-techniques-breach.html

#### Career (Job gate)
- https://prashantdangi1.github.io/cybersecurity-academy/career/resume-portfolio.html
- https://prashantdangi1.github.io/cybersecurity-academy/career/interview-prep.html
- https://prashantdangi1.github.io/cybersecurity-academy/career/certification-roadmap.html

#### Bug Bounty
- https://prashantdangi1.github.io/cybersecurity-academy/bug-bounty/bug-bounty-fundamentals.html
- https://prashantdangi1.github.io/cybersecurity-academy/bug-bounty/recon-asset-discovery.html
- https://prashantdangi1.github.io/cybersecurity-academy/bug-bounty/writing-reports.html
- https://prashantdangi1.github.io/cybersecurity-academy/bug-bounty/advanced-bounty-techniques.html

#### Freelancing
- https://prashantdangi1.github.io/cybersecurity-academy/freelancing/first-client.html
- https://prashantdangi1.github.io/cybersecurity-academy/freelancing/pricing-contracts.html
- https://prashantdangi1.github.io/cybersecurity-academy/freelancing/building-portfolio.html
- https://prashantdangi1.github.io/cybersecurity-academy/freelancing/client-management.html

#### Defensive Security
- https://prashantdangi1.github.io/cybersecurity-academy/defensive-security/soc-analyst-fundamentals.html
- https://prashantdangi1.github.io/cybersecurity-academy/defensive-security/incident-response-dfir.html
- https://prashantdangi1.github.io/cybersecurity-academy/defensive-security/threat-hunting.html
- https://prashantdangi1.github.io/cybersecurity-academy/defensive-security/detection-engineering.html

#### GRC
- https://prashantdangi1.github.io/cybersecurity-academy/grc/grc-fundamentals.html
- https://prashantdangi1.github.io/cybersecurity-academy/grc/risk-management.html
- https://prashantdangi1.github.io/cybersecurity-academy/grc/compliance-frameworks.html
- https://prashantdangi1.github.io/cybersecurity-academy/grc/security-auditing.html

#### AI Security
- https://prashantdangi1.github.io/cybersecurity-academy/ai-security/ai-llm-security-fundamentals.html
- https://prashantdangi1.github.io/cybersecurity-academy/ai-security/ai-red-teaming.html

#### Exploit Development & Vuln Research
- https://prashantdangi1.github.io/cybersecurity-academy/vulnerability-research/reverse-engineering-fundamentals.html
- https://prashantdangi1.github.io/cybersecurity-academy/exploit-development/linux-exploitation.html
- https://prashantdangi1.github.io/cybersecurity-academy/vulnerability-research/fuzzing-vulnerability-discovery.html
- https://prashantdangi1.github.io/cybersecurity-academy/exploit-development/binary-exploitation-advanced.html
- https://prashantdangi1.github.io/cybersecurity-academy/vulnerability-research/cve-research-disclosure.html

## Content guardrails

Every lab targets systems the learner owns, an intentionally vulnerable app they installed, a dedicated range, or a bug bounty program whose scope they've read. No instructions for attacking third-party systems without authorization. Outcomes are stated as realistic market context, never as income guarantees. Certification advice is honest about what employers actually value.

## Build status

Full curriculum shipped (CyberCore → Offense → Job gate → Bounty/Freelance/Defense/GRC/AI/Research + Discord unlock hub).
