# Codebook: nuclear passages in Indian parliamentary and MEA texts

Version 1.0 (frozen 26 October 2026). Do not change it while coding.

## What you code

Each item is a **passage**: up to 250 words of text around a nuclear keyword, taken from a speech
in the Lok Sabha or Rajya Sabha or from the MEA *Foreign Affairs Record*, 1962–1999. You see the
text only, not the speaker, party, date or source. Do not try to guess them; code what the
passage says.

The text was converted from scanned pages. Expect broken words ("nu- clear"), misreadings
("pucicar" for "nuclear") and fragments of neighbouring speeches. Read through the noise. If the
passage mixes two speakers, code the part that contains the nuclear content; if both speak about
it, code the dominant view and lower your confidence.

Code in this order: **relevance → frames → stance → confidence**.

---

## 1. Relevance

`relevant` = **yes** if the passage discusses nuclear weapons, nuclear explosions or tests,
nuclear energy, nuclear materials, or nuclear diplomacy (treaties, safeguards, disarmament talks)
in any country. Otherwise **no**, and stop.

Code **no** for: "atomic" or "nuclear" used only as a name with no content ("the Atomic Energy
Department's canteen staff"); a heading, agenda item, index line or table-of-contents entry with
no sentence about a nuclear matter; a passing mention inside a sentence about something else that
says nothing about the nuclear matter itself; text too garbled to read (note "unreadable").
Code **yes** for a factual question about a nuclear plant: relevance is about topic, not depth.
Code **yes** for general statements about the danger of nuclear war or the arms race.

---

## 2. Frames (mark every frame that is present; zero, one or several)

A frame is **present** when the passage uses that idea to describe, explain or justify a
position — not when a word merely appears. Mark a frame if a reader would say "this passage makes
that point", even briefly.

### disarmament
The goal or process of reducing, banning or eliminating nuclear weapons or tests worldwide:
general and complete disarmament, test bans (partial or comprehensive) as disarmament steps,
nuclear-weapon-free world, the Six-Nation Initiative, the Rajiv Gandhi Action Plan.
- Include: India presenting itself as a champion of disarmament; calls on the great powers to
  disarm.
- Exclude: a treaty mentioned only by name with no disarmament content (code the frame the
  passage actually uses about it, e.g. discrimination).

### peaceful_use
Nuclear energy or explosions for development: power stations, reactors, isotopes, "peaceful
purposes", "peaceful nuclear explosion" (PNE), self-sufficiency in fuel for power.
- Include: the 1974 explosion described as peaceful or as an experiment for mining or
  engineering.
- Exclude: "peaceful" in a general foreign-policy sense with no nuclear-energy content.

### option_open
India should keep, or has kept, the freedom or capability to make nuclear weapons without
committing to make them now: "keep the option open", "the nuclear option", "we will not
foreclose", "freedom of action", "we will decide in the light of circumstances".
- Include: refusal to give up the choice even while saying India does not intend to build now.
- Exclude: "options open" about non-nuclear matters (trade, a treaty's withdrawal clause as a
  legal point with no weapons content). A treaty or protocol counts only if the passage ties it to
  India's freedom to make weapons (e.g. an agreement on not attacking nuclear installations that
  "forecloses options" is not this frame unless weapons choice is meant). Example of exclusion: a member saying a treaty's
  withdrawal clause leaves "options open to us" while arguing India should sign — that is about
  legal exit, not the weapons option, unless the passage ties it to a weapons choice.

### discrimination
The international nuclear order treats states unequally: NPT/CTBT as discriminatory, nuclear
"haves and have-nots", "nuclear apartheid", "club", monopoly or hegemony of nuclear powers,
vertical vs horizontal proliferation, unequal obligations.
- Exclude: discrimination in a domestic sense (caste, regions, jobs).

### deterrence_weapon
Nuclear weapons as instruments of security for India or others: making, testing or
weaponising a bomb; deterrence (minimum, credible); nuclear-weapon-state status; no-first-use;
second strike; delivery systems; arsenals.
- Include: arguments against India's bomb that engage with weapons logic ("a bomb would not
  deter China").
- Exclude: other states' weapons mentioned only as a threat with no weapons-policy content for
  anyone (code security_threat).

### security_threat
External danger to India: China, Pakistan, other states' nuclear programmes or tests,
blackmail, encirclement, guarantees or a nuclear umbrella from others, national security
in general.
- Include: China's 1964 test as a danger; Pakistan's programme; great-power guarantees offered
  to non-nuclear states.
- Exclude: China or Pakistan mentioned as a place with no danger or security point (e.g. a trade
  delegation).

### autonomy
India's independence of decision against outside pressure: sovereignty, national interest,
self-reliance, refusing to bow to pressure, sanctions, coercion, "we will not surrender our
right", decisions taken "in our own national interest".
- Exclude: "pressure" in a technical or domestic sense (pressure vessels, price pressure).

---

## 3. Stance on India's own nuclear posture (choose exactly one)

Ask: **what does this passage say India should do, or is doing, about nuclear weapons?** Apply
the rules in this order and stop at the first that fits.

1. `other_country` — The passage is only about another state's programme, test or policy, and
   says nothing about what India should do. (China's test described, with no Indian response
   proposed.)
2. `critical_of_tests` — It criticises a test India has carried out (Pokhran 1974 or 1998), its
   timing, its handling or its consequences (isolation, sanctions, arms race), whether or not it
   accepts keeping the option. Judge from the text alone; do not guess the date. Example: "There was a national consensus on keeping the nuclear
   option open. There was no consensus on your exercising that option." (1998).
3. `pro_bomb` — India should make, test, deploy or weaponise nuclear weapons, or the passage
   welcomes or justifies India's tests or its status as a nuclear-weapon state. Includes demands
   after China's 1964 test that India build the bomb, and post-1998 defences of the tests even when
   they also affirm India's commitment to disarmament.
4. `keep_option` — India should keep the capability and freedom to build, or refuse treaties
   that would close the choice (NPT, CTBT), without calling for a bomb now. Includes "we will not
   sign a discriminatory treaty" when not paired with a call to build. Example: "Let us keep the
   nuclear options open as a deterrent ... it will be our strategy to decide at which particular
   stage we would like to enter into nuclear-weapons manufacture." (1972).
5. `disarmament` — India should not build nuclear weapons, and/or should seek global
   disarmament as its answer; renunciation statements ("we will not manufacture the bomb") count
   here when not paired with keeping the option.
6. `peaceful_only` — The passage argues for, defends or reports favourably on India's nuclear
   energy or peaceful programme and takes no position on weapons. A bare factual question or
   statistic about a plant is `neutral`, not this.
7. `neutral` — Procedural, factual or a question without a position (asking for a statement,
   reporting a meeting, figures on a plant's output with no argument, a question about publicity
   after a test that does not criticise it). General fear of nuclear war with no call to action is
   `neutral`.

Tie-breaks:
- Calls to remove other powers' nuclear weapons from India's region (Indian Ocean as a zone of
  peace, opposing nuclear-armed ships or bases) → `disarmament`. Merely reporting such deployments
  with no Indian position → `other_country`.
- "We will not make the bomb, but we will not sign the NPT either" → `keep_option`.
- A government statement that the 1974 explosion was peaceful and India has no weapons plans →
  `peaceful_only` if the passage is about the explosion's purpose; `disarmament` if it stresses
  renouncing weapons.
- A member asking the government whether it will make the bomb, with no view → `neutral`; if the
  question is loaded ("Will the government at last make the bomb we need?") → `pro_bomb`.

---

## 4. Confidence

`3` clear; `2` some doubt (noisy text, mixed speakers, or two stances close); `1` a guess.

---

## 5. Recording

One row per passage: `code_id, coder, relevant, disarmament, peaceful_use, option_open,
discrimination, deterrence_weapon, security_threat, autonomy, stance, confidence, note`
(frames as 1/0; `note` optional, under 20 words — required when confidence is 1).

Coder ids: `human_1` (author), `human_2` (second person, if any), `claude_a`, `claude_b`. Claude
coders must not see each other's codes, the dictionary codes, or metadata.

## 6. Pilot and freezing

1. Pilot (done under 0.1 by `claude_a` and `claude_b`; author did not hand-code): code the same 30 passages: the first 6 code_ids of each voice (LS members, RS members, ministers, MEA, near-miss), listed in `subsets.csv` (author decision, 26 October 2026: balanced across voices).
2. Compare; for each disagreement, decide whether the rule was unclear. Revise definitions and
   tie-breaks only; do not add or remove frames or stance categories.
3. Record changes in the changelog below, set version 1.0, and code the rest. Pilot passages are
   recoded under version 1.0.

## Changelog
- 0.1 — first draft.
- 1.0 — after the pilot (Claude coders A and B; the author chose not to hand-code, and asked that
  doubts be resolved by Opus): relevance rules for headings, passing mentions, unreadable text and
  general nuclear-war fears; option_open limited to weapons choice; pro_bomb covers justifying the
  tests; peaceful_only vs neutral for plant facts; foreign deployments in the region → disarmament;
  post-test publicity questions → neutral.
