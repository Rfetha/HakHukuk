# CLAUDE.md

> **2026-09-12 — the doc layer is REBUILT and `docs/superpowers/` has been EMPTIED. Read this box before trusting a pointer.**
>
> Deleted 2026-09-06 (human decision, on a backup branch): `ROADMAP.md` · `TODO.md` ·
> `TASARIM.md` · `docs/VISION.md` · `docs/PAPER_TARGET.md` · `docs/_arsiv/**`.
> The measurement record (`docs/record/**`), the decision ledger (`docs/adr/**`) and
> `outputs/eval/**` were **kept** — they are the source of every number published here.
>
> **Rebuilt 2026-09-07 (Görev 13):** [`PRODUCT.md`](PRODUCT.md) — what the product is and what it
> **does NOT promise** · [`ROADMAP.md`](ROADMAP.md) — direction, every step tied to a *measured* gap ·
> [`TODO.md`](TODO.md) — only what is runnable today · [`docs/MIMARI.md`](docs/MIMARI.md) — the `v1`
> chain. `tests/test_belgeler.py` walks every link in them, so a dead pointer now FAILS a test.
>
> **Emptied 2026-09-12:** `docs/superpowers/` carried two specs and three plans; **all five were
> deleted** when the `hp` → Hat A → Hat B plan closed at **115/115**. Their load-bearing content —
> the register of **32 defects**, the handover table, and the architectural core of the deleted
> design — was moved into [`ADR-0083`](docs/adr/0083-kusur-sicili-adrye-tasindi.md). The folder now
> holds **exactly one** file. The 9 links that died with the deletion are listed in ADR-0083 §(D)
> and are **deliberately left unrepaired** inside `docs/adr/**` and `docs/record/**`.
>
> | you want | read |
> | :--- | :--- |
> | **what to do next** | [`docs/superpowers/00-IS-SIRASI.md`](docs/superpowers/00-IS-SIRASI.md) — **the work order**, and the folder's only file. `v1-son-iş` is **IN EXECUTION** (plan: [`plans/2026-09-12-v1-son-is.md`](docs/superpowers/plans/2026-09-12-v1-son-is.md), currently step 6.8 of 9) — the κ debt closed and the gate re-passed under a second judge ([ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)); steps 7-9 (push, public review, visibility) remain. `v2-RL-GRPO` is parked. |
> | the defect register, the handover, the deleted design's core | [`ADR-0083`](docs/adr/0083-kusur-sicili-adrye-tasindi.md) — **5 defects still open** (5a · 10 · 23 · 27 · 31) · **3 handed on** (6 · 11 · 12b) · closed in the `v1-son-iş` round: **24** (`b077f13`) · **29** (adım 6.3.1) · **33** (`cc12b6e`) · **25** (Adım 8, kesir birimi düzeltildi) |
> | what closed on 2026-09-12 | the `hp-hat-a-hat-b` round, **115/115** — narrative in [#66](docs/record/research_log/2026-09-11-urun-yuzeyi-ve-aygit-kusurlari.md) and [#67](docs/record/research_log/2026-09-12-konteyner-ve-alet-onarimlari.md) |
> | what closed on 2026-09-06/07 | the `faz0-olcum-zinciri` plan, **48/48** *(plan deleted 2026-09-12)* — [#62](docs/record/research_log/2026-09-06-faz0-olcum-zinciri.md) |
> | the rescued debt queue | `DEVIR-PROMPT.md` *(deleted 2026-09-07 — its job was done)*; the queue it carried was folded into the `hp-hat-a-hat-b` plan, and from there into [`ADR-0083`](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §(C) |
>
> **Framing: open-source PRODUCT** — a legal adviser a Turkish citizen can actually ask.
> `v1` = model layer · `v2` = app layer · arxiv is a **by-product**.
>
> **Pointer repair done 2026-09-07 (Görev 13 Adım 5).** `docs/_arsiv/README.md` is still gone;
> the binding doc-type table is the one further down in this file.
> `docs/record/**` and `docs/adr/**` were deliberately NOT touched — they record *"on that day
> this document said this"*.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **This file is a MAP, not a report.** It says *where things are* and *what rules bind you*.
> It does **not** carry measurement tables or sprint narratives — those live in
> `docs/record/research_log/` and `docs/adr/`. Duplicating them here is how this file grew to
> 33 KB and went stale in several places at once *(cleaned 2026-08-06)*.
> **Rule: when a round closes, update the POINTERS here — not the numbers.**

## What this repository is

**HakHukuk** — an open-source Turkish legal assistant built on a small language
model. Mission: make legal language legible to the citizen.

**FRAMING CHANGED 2026-08-03 — read this before anything else.**

This was a **master's thesis** project (private repo, proprietary licence, claim-driven).
It is now a **fully public open-source product**: Apache-2.0, weights + code + data +
the entire research record. An arxiv paper may follow, but it is **no longer the goal**.

```
WAS   thesis  → prove a claim  → gates, pre-registration, ablations serve the claim
IS    product → build the best model → same discipline, now a "don't fool yourself" tool
```

**The goal is the model.** Beat Gemini 3.1 Flash-Lite, then reach Flash and Pro.
Priorities live in [`ROADMAP.md`](ROADMAP.md), tied to measured gaps.

| constraint the reframing removed | now |
| :--- | :--- |
| **ONE size point** (ADR-0028, ~4B) | **lifted** — 8B/12B are open, multiple sizes may ship |
| **graph-RAG out of scope** (ADR-0019) | **lifted** — not forbidden, just *unplanned*; no line item in `ROADMAP.md` |
| **Kapı 5 / CP4-CP5 baselines** | **optional** — deferred, `docs/_arsiv/sprint2b.md` *(deleted 2026-09-06)* |
| **frozen TEST seen once** | repurposed as a **release acceptance test** |
| *"never say frontier"* | moot |

**What it keeps — all of it.** Fixed seeds · logged runs · run manifests (`KUNYE.json`) ·
pre-registered gates · same-day research log · an ADR per decision · the trap list.
**This is not ceremony:** the discipline has repeatedly caught numbers that were about to be
published wrong — a metric that rewarded refusing, a validity gate that voided a degenerate
model, a normalization prescription that measurement reversed
([ADR-0052](docs/adr/0052-merge-norm-dengeleme-hukmu-tersine.md)), and both of the harness's own
stated justifications.

## Current state — one glance, then follow the pointer

**Artifact: `HakHukuk-4B-v0.1`** (internal id `tgta_v1`) — two LoRA branches trained
independently from the raw base, merged as task vectors with **raw TIES**.
Card: [`MODEL_CARD.md`](MODEL_CARD.md) · registry: [`docs/record/kollar.md`](docs/record/kollar.md).

```
product number — v2 unit, 2026-09-07 (harness ON, k=10, S2 corpus, NO preamble — ADR-0063)
             faithful-answer mass          69.4-80.1% (claude-sonnet-5 ↔ gpt-4o-mini) ← headline
             recall@10                     0.9500     ← mass cannot exceed this
             over-refusal (by eye)          4/80
             misattribution (by eye)        8/80      ← next first-rank axis (B1)
             fabricated article numbers     0/114     ↔ competitors 0 · 4 · 4  (re-scored 2026-09-11)

   ⚠️ The headline is an UNCONDITIONAL RANGE across the two judge families that have scored it
   (ADR-0084, 2026-09-13): formatting the headline to the outcome — one number when a gate
   passes, a range when you're unsure — is a self-deception pattern. The three competitor arms
   remain SINGLE-judge and are stamped as such in every table (ADR-0057); the asymmetry is
   deliberate, not an oversight.

   v1.0 GATE CLOSED 2026-09-07 — all three clauses, with numbers (ADR-0064):
   (1) mass ≥ 3.5 Flash − 2,0 p   0.8011 ↔ threshold 0.7225   PASSED  +5.86 p
   (2) misattribution no worse    anchor re-nailed at 8/80      PASSED
   (3) M5 must not rise           memorised mass −6.82 p vs BASE PASSED
   (*) eye-reading at every counting step — the tool was wrong TWICE

   RE-READ 2026-09-12 under a SECOND, independent judge family (ADR-0084): the κ debt closed
   under ADR-0074's own one-sentence condition (`3.5 Flash` scored by the same second judge)
   and all three clauses PASS again, margins vs. the anchor +5.86 p (`gpt-4o-mini`) / +7.57 p
   (`claude-sonnet-5`). κ itself did NOT move (still 0.534/0.409, below 0.6) — what closed was
   the absence of an equal exam, not κ. This is still not `v1.0`: that label is step 9's job.

   The gain came from the INSTRUMENT, not the model. Weights never changed. Five defects were
   found, each of the "produces a wrong number without erroring" class: question set (ADR-0067)
   · RRF fusion (0068) · DEV↔TEST composition (0069) · a production budget that was NOT equal
   to the competitor's (0070) · a gate clause with NO ANCHOR (0073, trap 2.17).
   → docs/record/research_log/2026-09-06-faz0-olcum-zinciri.md (#62)

~~previous headline: mass 68.4% with the sufficiency preamble (ADR-0058)~~ — SUPERSEDED.
   The preamble was removed (ADR-0063): it was adopted for RAISING mass and was measured to
   LOWER it. Old unit = v1 question set + 1024 budget; NOT comparable, and no comparison is made.
ceiling        (harness OFF, gold guaranteed)     71.6%     pre-Faz 0, old unit
```

**Both ON figures were rescored on 2026-09-06 and two things flipped.** The abstention
detector scanned the whole answer in one branch, so our template's discarded-sources rationale
read as a refusal — a bug **specific to our own answer template**, which is why fixing it moved
our numbers (62.8% → 68.4%) and left the competitor's untouched (measured, not assumed).
The ablation turned out to be the **higher** column, which **inverted ADR-0058's own
rationale** (the preamble was adopted for raising mass; it lowered it by 4.6 points).
**S14 is CLOSED 2026-09-06 → the preamble was REMOVED** ([ADR-0063](docs/adr/0063-yeterlilik-onsozu-kaldirildi.md)):
the product's default regime is now **preamble-free** and the preamble run became the ablation.
Binding metric is **mass** — an unanswered question is worthless to a citizen; misattribution
is paid on **its own axis** (B1), not with a prompt patch.
[ADR-0061](docs/adr/0061-cekinme-dedektoru-istem-rejimi-bagimliligi.md) ·
[#61](docs/record/research_log/2026-09-06-dedektor-onarimi-b10-yeniden.md)

> ⚠️ **This row was RE-SCORED on 2026-09-11 and one competitor number moved AGAINST us.** The
> citation verifier was repaired (trap **1.13**): it used to resolve a law name loosely and land on
> the **wrong law**, stamping `DOGRULANDI` against the wrong statute in **7 of the 16** laws whose
> corpus name carries a parenthetical (after the repair: **0/16**). All five arms were then re-scored
> through the **published** pipeline (`scripts/puanlama/harness_tablo.py`), and the calibration gate
> passed — our own `harness_tablo.json` was reproduced **field for field** (mass `0.8011`, `coverage`
> `0.9375`, `A1` `0.8545` included). **Of 702 citations exactly ONE changed**, and it was a stamp
> wrongly held **against a competitor**: `gemini-3.1-flash-lite`, item 25, *"Gelir Vergisi Kanunu
> Madde 73"* — old `1319 Emlak Vergisi → MADDE_YOK`, new `193 GELİR VERGİSİ KANUNU (G.V.K.) →
> DOGRULANDI` (read by eye; the corpus witness exists and is not repealed). ⇒ **`1/152` → `0/153`**.
> **We lost a lead and we say so:** on the one deterministic axis where we were ahead of every
> competitor, 3.1 Flash-Lite is now **level with us**. What we bought is an **equal exam**
> (ADR-0057): all five arms are now scored by the **same** tool. The other three arms did not move.
> Each arm was run **twice**, byte-identical both times.
> ⚠️ **The unit of this row:** numerator = `MADDE_YOK + KANUN_YOK`, denominator = **`DOGRULANDI`**
> (not total citations). This was written down nowhere and had already misled one probe.
> Measurement: `outputs/eval/g22-rakip-yeniden-puanlama/BULGU.md` · repair: `g22-atif-onarim/BULGU.md`.

**Product version is `v0.3` (tagged 2026-09-09); the model artifact is still `HakHukuk-4B-v0.1`.**
`v1.0` was NOT granted — the acceptance test on the frozen TEST ran (raw mass **0,5804**, ceiling
`recall@10` **0,7500**) and the blocker is **the measuring instrument, not the model**: every
figure is still one judge family's verdict and κ is **0,534**, below the tool's 0,6 threshold
([ADR-0077](docs/adr/0077-v1-0-verilmedi-v0-3.md) · [#65](docs/record/research_log/2026-09-09-kabul-testi-ve-frontier-kiyasi.md)).
Weights are published at `Rfetha/HakHukuk-4B-v0.3-Q4_K_M` and are **currently private** while
open defects are resolved — **5 are still open**, registered in
[ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §(A)/§(C) (5a · 10 · 23 · 27 · 31).
Closed in the running `v1-son-iş` round: **24** (`b077f13`, the stale README table),
**29** (adım 6.3.1, the backup file in the image), **33** (`cc12b6e` — the one-command
reproduction path's `recall@10` gate read a field that does not exist, so it **always** failed
with a false *"harness OYNAMIŞ"* accusation; it fails on the anchor's own data too) and **25**
(Adım 8 — `MODEL_CARD`'ın uydurulmuş-madde satırı iki farklı kesir birimi taşıyordu, tüm
paydalar `DOGRULANDI`'ya çevrildi, sayı oynamadı).
Defect **10** is exactly this one: the HF **visibility** half is still a human decision.
**A frontier subject entered the pool and is AHEAD:** `claude-sonnet-5` mass **0,8348** ↔ ours
**0,8011** (eye-corrected reading). The claim *"we are not behind on B1"* held only in the Gemini
pool: `wrong_ref_rate` **0,0769 ↔ 0,0083**.
~~**The product path is NOT the measured path:** `hakhukuk.servis.answer()` returns a blank
answer on ~5% of questions (4/80, non-termination) and would fail ADR-0040's own 5% validity
gate. Recorded, not fixed.~~ → **FIXED 2026-09-11** ([ADR-0080](docs/adr/0080-urun-yolu-zorunlu-dusunce-kapatmasi.md),
a REGIME change taken by the human): the product path now forces the thinking channel closed in
a second pass, exactly as the measurement line does. Blank answers went **4/80 → 0/80** and
truncation **8,75% → 3,75%**, so ADR-0040's gate now **passes**. Only **4 of 80** answers changed
byte-wise — the four that were broken. ⚠️ The fix lives in `hakhukuk/servis.py`: a caller who
drives `llama-server` directly, without this package, still hits the original defect.

Still `v0.1` as an artifact, not `v1.0` — **and the reason changed on 2026-09-07.** The gate's three
clauses now **pass on DEV** (above), but two things are still missing: the **acceptance test on
the frozen TEST** had not run at the time this sentence was written — **it ran on 2026-09-09**
(raw mass **0,5804**, above) and clause (a) is **closed**; what follows is kept because the
*ceiling* argument still binds (its retrieval ceiling is ≈75%, not DEV's 95% — [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md)),
and **every number is still one judge family's verdict** (`gpt-4o-mini`, no κ, self-preference
unmeasured — ADR-0064 *"Ne KURULMAZ"* clause 2). Product vs. claim versioning is split:
[ADR-0065](docs/adr/0065-bolunmus-surumleme.md).
The OFF number is a **ceiling, not a rival** — the two settings do not measure the same
thing (OFF hands the model the gold article by construction).

**Where the numbers actually live — do not re-derive them here:**

| you want | read |
| :--- | :--- |
| every measurement, dated, with its source file | [`docs/record/research_log/README.md`](docs/record/research_log/README.md) — entries **#39-#70** |
| what to work on next, tied to measured gaps | [`docs/superpowers/00-IS-SIRASI.md`](docs/superpowers/00-IS-SIRASI.md) — `v1-son-iş` is **IN EXECUTION** ([plan](docs/superpowers/plans/2026-09-12-v1-son-is.md), steps 7-9 remain) · direction in [`ROADMAP.md`](ROADMAP.md) |
| the open debt queue | [`ADR-0083`](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §(A) register + §(C) handover — **5 open** (5a · 10 · 23 · 27 · 31; four of the original nine — 24 · 29 · 33 · 25 — closed inside the `v1-son-iş` round), 3 handed on *(it passed through `DEVIR-PROMPT.md` and the `hp-hat-a-hat-b` plan, both deleted)* |
| why a decision went the way it did | [`docs/adr/`](docs/adr/) — ledger runs to **0084**, next is **0085** |
| questions raised and not yet answered | the nine items that go **into the grill**, [`ADR-0083`](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §EK E.5 *(they passed through `docs/open_questions.md` and then the `hp-hat-a-hat-b` plan, both deleted)* |

**Two things a new session must not get wrong** (both were *measured*, not assumed):

- **Both of the harness's stated justifications are refuted.** *"The citation verifier closes
  A1"* — dead: fabricated article numbers are **0/118**, the class was empty. *"The rejection gate
  closes M2b"* — tested 2026-08-05 and **the gate failed**: on a matched exam the harness-ON arm
  scored *below* the OFF anchor, and the gate cannot even fire in this regime
  ([#56](docs/record/research_log/2026-08-05-olcum-bosluklari.md)). What survived is *"without a
  retriever there is no product"* plus a set of measured mechanisms. M2b is now a **training** debt.
- **The ARA KAPI (mid-gate) verdict flipped on 2026-08-06 — it now FAILS.** The
  pre-registered thing was the *formula* (`merge M2b ≥ 0,90 × base's answer-blind M2b`),
  not the number. Re-derived with the single repaired tool: threshold **0,8649** ↔ merge
  **0,766** → **fails by 9,9 points** (and fails the old 0,887 threshold too; denominators
  are equal, 77 ↔ 77). ADR-0050: the *tool* was fixed, the threshold was **not touched**.
  This is the gate that authorized CP4-CP5 spending — **that authorization is gone.**
  [ADR-0045](docs/adr/0045-ara-kapi-merge-onarim-kontrolu.md) ·
  [#58](docs/record/research_log/2026-08-06-payda-tekillesmesi.md).
- **The biggest single loss is over-refusal, and the model owns it** — the gold article is *in
  context* and the model abstains anyway. Retrieval cannot fix this. Debt **B10**.
- **The abstention DETECTOR itself is under repair — do not quote B10's counts as settled.**
  Measured 2026-09-06: in the no-preamble regime `exact_reject` scores a correct, cited answer
  as an abstention, because it scans the whole answer and the discarded-sources rationale trips
  the refusal regex. The official anchor holds at least one verified false positive and the
  contamination size is **unmeasured**. A programmatic probe was wrong in *both* directions, so
  the only closing move is reading all 80 items by eye — decided, scheduled, and pre-registered
  ([#60](docs/record/research_log/2026-09-06-hasat-kabul-olcutu-coktu.md); the decision was taken
  as open question **S13** — a pointer with no target left, the question carrier having been
  `docs/open_questions.md` and then the `hp-hat-a-hat-b` plan, both deleted. Its outcome is
  [ADR-0061](docs/adr/0061-cekinme-dedektoru-istem-rejimi-bagimliligi.md) and
  [#61](docs/record/research_log/2026-09-06-dedektor-onarimi-b10-yeniden.md)).
- 🧭 **Framing, 2026-09-06: the release language is v1/v2.** `v1` = a fine-tuned model release
  that actually works end to end (weights + code + data + research record, shipped with the
  retriever and the preamble, because the headline number is not reproducible without them);
  `v2` = the API over that same model; arxiv is a **by-product, not the goal**. Sequenced plan,
  acceptance criteria and rejected options:
  the drafts `specs/2026-09-06-v1-v2-roadmap-taslak.md` and
  `specs/2026-09-06-yeni-belge-katmani-design.md` — **both deleted** (2026-09-06 and 2026-09-12);
  what survived of the second is [ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §EK ·
  direction stays in [`ROADMAP.md`](ROADMAP.md).

**Status of work: B10 over-refusal round CLOSED 2026-09-06 — the target was met with NO
training** ([ADR-0062](docs/adr/0062-b10-turu-kapatildi-hedef-egitimsiz-karsilandi.md)).
Tasks 0-3 ran, Tasks 4-10 **never did**, `τ_a` v2 **was never trained**. The plan carries its
closing block:
`plans/2026-08-06-asiri-red-tau-a-v2.md` *(deleted with the doc layer; its closing block is quoted in [ADR-0062](docs/adr/0062-b10-turu-kapatildi-hedef-egitimsiz-karsilandi.md))*.

The round set out to train over-refusal down from 14/80 into a pre-registered 8-11/80 band.
Its own **read-it-by-eye** step (Task 3.8) instead refuted the harvest acceptance criterion —
6 of 10 sampled "abstentions" were full, cited answers — and repairing the detector put the
true number at **8/80 by eye (9/80 by tool) with nothing trained**: **43% of the "problem" was
the measuring instrument.** Harvesting anyway would have cost 5.3 h and ≈$5.2 for a gap of two
items, so the round was closed. Over-refusal is **smaller, not gone** — 8/80 still sits above
3.5 Flash-Lite's 6/80, and *"how far would training push it"* was **never measured**.

**Three things a new session must carry forward from that closure:**
- **Next first-rank axis is B1** (misattribution, 5/80) — B10 stepped down; the gap between them
  narrowed 2.8× → 1.6×, and B1 has never been worked on.
- **The round's tooling is intact and reusable** — `scripts/veri_hazirlik/b10_hasat.py`, Modal `harvest_b10`
  (ADR-0047 m.2 carrier, verified on L4), the leakage filter (13,350 → 12,914, byte-identical in
  the container). Do not rebuild it for B1.
- **The thresholds re-derived under ADR-0061 Karar 2 stand unused** (`aşırı-red < 0.4125`, etc.)
  — this round did not need them; **the next training round will**.

**What caught it was not a numeric gate** — the gate (`kabul_orani 0.1733 > 0.10`) **passed** the
broken measurement. The eyeball step caught it, and it has now caught something three times —
[#60](docs/record/research_log/2026-09-06-hasat-kabul-olcutu-coktu.md) ·
[#61](docs/record/research_log/2026-09-06-dedektor-onarimi-b10-yeniden.md) ·
[#65](docs/record/research_log/2026-09-09-kabul-testi-ve-frontier-kiyasi.md). *(The record layer
credits this to "ADR-0051"; that ADR's subject is `τ_a`'s M2b pairs and it carries the
read-it-by-eye rule only as its closing lesson. The rule is quoted here **without an ADR number**
so nobody chases a decision that was never written as one.)*

**Not blocked by any of that:** the Phase 0 cheap repairs run in parallel —
[`ROADMAP.md`](ROADMAP.md) · [`TODO.md`](TODO.md).

### Target audience: the CITIZEN — but read the trap

Plain language is the **presentation layer of a correct answer, not a training target.** Training
toward plain/short answers was tried and **lowered accuracy**; the citizen-register round matched
base while abstention collapsed ([ADR-0010](docs/adr/gemma4-12b-dersler.md#adr-0010), in force).
So: train for correctness and abstention, simplify at the **prompt layer**.

## Document map

**Belge türü → yeri.** The authoritative table lives in
`docs/_arsiv/README.md` *(archive deleted 2026-09-06; the doc-type table below is now the binding one)* and it binds:

| type | where | holds |
| :--- | :--- | :--- |
| **record** | `docs/record/` | *what happened, what the number was* — retrospective, no checkboxes |
| **decision** | `docs/adr/` | *why this way, which alternative was eliminated* |
| **spec** | a `specs/` folder under `docs/superpowers/` | *what we will build* — `brainstorming`/`grill` output. **Gone since 2026-09-12**; recreated when the next spec is written |
| **plan** | a `plans/` folder under `docs/superpowers/` | *what will be done* — `- [ ]` boxes; gets a closing block when executed. **Gone since 2026-09-12** — the convention (ADR-0056) survives the emptying: **at most one live plan**, and today there is none ([ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md)) |
| **execution** | repo root `sprint*.md` | **only the OPEN sprint's** live doc |
| **archive** | `docs/_arsiv/` | anything of any type no longer in force |

Two rules: a doc that says *"what's next"* is a **plan** and cannot sit under `record/`; and a
**closed execution doc moves to the archive** — the root holds only what is open.
`docs/record/` and `docs/adr/` are **NOT archives** — they are the live research record and
decision ledger.

### Read before doing anything

- **[`docs/record/yurutme-tuzaklari.md`](docs/record/yurutme-tuzaklari.md) — before ANY run.**
  The list of *"produces a wrong number without erroring"* patterns, every one of which has
  actually bitten: dropped `--data`/`--thinking off`, uncalibrated refusal regex, missing
  `--target-modules`, `set -e` swallowing the error, half-finished quantization that still leaves
  a file on disk. **This line's failure class is silent wrongness, not crashes.**
- **[`docs/adr/gemma4-12b-dersler.md`](docs/adr/gemma4-12b-dersler.md) — the retired 12B line's
  26 ADRs (0001-0026) in one file.** Part **(A) lessons** is base-agnostic and is what you read —
  *"plain SFT destroys abstention"*, *"the eval mirror is mandatory"*, *"`spawn()` not `remote()`"*
  live there. Part (B) is the decision record with each ADR's status in the new line; part (C) is
  entry points into the raw log. Every `ADR-00NN` reference elsewhere still resolves — the file
  carries an anchor per ADR (`#adr-0011`). **Read part A before designing any experiment.**
- 🌳 **[`docs/model-soyagaci.mmd`](docs/model-soyagaci.mmd) — the model family tree** (Mermaid):
  raw base → the two branches → the three merge variants → the published artifact → harness →
  the `v1.0` gate. Renders the *shape* of what `kollar.md` records row by row. **Not a
  timeline** — branches are independent and merge variants are alternatives, not a chain.
- **[`docs/record/kollar.md`](docs/record/kollar.md) — the artifact registry.** Every trained
  branch AND merge has its identity here; *an artifact with no row is nameless and must not be
  used*. `tg_v1` (‖τ‖ 10,4722 — **and 10,4589 in `kollar.md` is also right**: the first is measured at merge time from the bf16-materialized ΔW, the second from the standalone artifact; the 0,13% gap is bf16 and [#47](docs/record/research_log/2026-07-30-cp2s-boru-hatti.md) logged it as an *independent cross-check*, not a discrepancy — do not "fix" either) · `ta_v1` (‖τ‖ 1,1806) · **`tgta_v1` = `HakHukuk-4B-v0.1`**. Both
  names stay and do different jobs: `tgta_v1` is internal traceability (*which branch, which
  version* answerable from the filename), `HakHukuk-4B-v0.1` is outward-facing. Carries the
  base/ours/Gemini table under an explicit **"NOT a parity claim"** banner.
- [`docs/record/research_log/README.md`](docs/record/research_log/README.md) — the chronological
  record, **authoritative for "what happened."** New findings continue at **#71**.
- [`docs/adr/`](docs/adr/) — new decisions get a new ADR; numbering continues at **0085**.
  **0059 is RESERVED** — the round's `τ_a` v2 data-symmetry ADR, written in Görev 10. Six
  places already cite `ADR-0059 §sapma-1`; do not take that number for anything else.

### Direction and scope

- [`ROADMAP.md`](ROADMAP.md) — **the authority on direction.** Priorities tied to measured gaps.
- [`TODO.md`](TODO.md) — the active task list.
- [`PRODUCT.md`](PRODUCT.md) — mission, design principles, 5-phase evolution
  (SLM → RAG/Graph → niche → agentic → citizen platform). Authoritative for *what* and in what order.
- [`docs/FINE_TUNING.md`](docs/FINE_TUNING.md) — Phase 1 playbook: hardware, QLoRA/Unsloth stack,
  data pipeline, recipe, ablation matrix. Authoritative for *how*.
- [`docs/VERI_PLANI.md`](docs/VERI_PLANI.md) — **the authoritative data plan.**
- [`docs/BEDESTEN_API.md`](docs/BEDESTEN_API.md) — live legislation API contract.
- [`ADR-0083`](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §EK E.5 — the nine questions raised
  and not yet answered; they go into the grill that writes the `v1-son-iş` plan.

### Historical — still load-bearing, no longer authority

- **`TASARIM.md` *(deleted 2026-09-06; its eval protocol lives on in `docs/adr/` + `docs/record/`)* (repo root)** — the thesis-era design doc, flagged historical
  2026-08-03. Authority moved to `ROADMAP.md` + the active plan. Still live for what it
  *measures*: the eval protocol, DEV/TEST split, gates, and **the rejected alternatives with their
  reasons** (§11). Its claim layer (Kapı 5, parity matrix) is arxiv-conditional.
- **`referans-design-doc.md` *(silindi 2026-09-07)* — the user's original draft. Its function was taken over by [`docs/MIMARI.md`](docs/MIMARI.md) on 2026-09-07 (Görev 13 Adım 4).** Its numbers were illustrative placeholders and were deliberately NOT carried over.
- `docs/_arsiv/` *(deleted 2026-09-06)* — closed sprints (**1 · 2 · 3-part-1**), the deferred claim layer
  (`sprint2b.md`), and superseded 12B-era plans. Its `README.md` says why each one is there.
- [`docs/record/sprint1/sprint1-sonuc-tablosu.md`](docs/record/sprint1/sprint1-sonuc-tablosu.md) ·
  [`docs/record/sprint2/defter.md`](docs/record/sprint2/defter.md) — the distilled records of those
  sprints. Sprint 1's table is **not a parity claim** (harness off, cost not normalized).
- **Kapı 5 lost clause (d) on 2026-07-29** —
  [ADR-0039](docs/adr/0039-kapi-6-parametrik-sizinti.md): M5 (parametric leakage) became its own
  **Kapı 6**, anchored at **base** (not the competitor): coverage ≤ 37.5%, memorized-mass ≤ 10.7%.
  Not a loosening — `τ_g` fails it today and that is reported, and every cell is *also* reported
  against the original (d). A hard M5 veto had made Kapı 5 unpassable by any `τ_g`-containing cell,
  so the gate closed before it could measure what it was built to measure.

## Documentation discipline (HARD RULE — the rule survived the reframing, its reason changed)

**Old reason:** *"we must be able to write the paper months later."* **Current reason, and it is
stronger:** this is an **intermittent solo OSS project**. Weeks can pass between sessions, and the
repo is the only thing that remembers. It is also what a public project owes its readers — the
research record is the most valuable thing here, more than the weights.

- **Every significant experiment, result, or decision → write it down immediately**, while context is fresh. Two homes: `docs/record/research_log/README.md` (chronological narrative + numbers + lesson) and `docs/adr/` (a discrete ADR per big decision). A finding that lives only in chat is a finding lost.
- **Numbers are sourced, not remembered.** Record the exact metric, n, judge, seed, and the file the result lives in (`outputs/eval/...`). Reproducibility is the point — it makes an OSS release verifiable and keeps the arxiv door open as a side effect.
- **Negative/surprising results are first-class** — log them with the same rigor as wins. Several of this line's most useful findings are refutations of its own plans.
- When a decision contradicts an older doc, **flag the contradiction in both places** rather than silently overwriting — the audit trail is the asset.

## Core constraints that shape every decision

These are non-negotiable framing from the docs — honor them in any code or recommendation:

- **Accessibility over raw performance.** Product target = run on consumer GPUs. **The base is a PARAMETER, not a decision (ADR-0026): no script carries a default; an undefined base must fail EARLY** — silently falling back to the wrong model turns a multi-hour run into invisible garbage. Current **working assumption** = a ~4B-class instruct model (ADR-0027, supersedes ADR-0003's Gemma 4 12B), and **no run starts before it clears the 6-item verification gate** in `TASARIM.md` §8: llama.cpp architecture support (ADR-0025 is now a *base selection criterion*) · chat-template render verified **by eye** (`research_log` #38: minja mis-rendered a branch, the model never stopped, and a CANON run was silently wasted) · turn-marker assert · Unsloth/sm_120 · quantization (**Q4_K_M** absent an official QAT checkpoint — ADR-0023's pure-Q4_0 was QAT-specific and does **not** transfer) · license.
  **≤8 GB = SOFT GATE (not a hard limit):** preferred band ≤8 GB, but configurations above it (12/16/24 GB) are still reported, *at a cost on the accessibility axis* — a cost-performance **curve**, not a single point (ADR-0018). ADR-0028's one-size-point narrowing was **LIFTED 2026-08-03** along with the thesis. What survives is the *engineering* reason it was attractive: a ~4B base trains on the local RTX 5070 at **$0** (the 12B line had to send every run to Modal), so the recipe is cheapest to develop there. **Sequencing preference, not a lock:** push 4B toward its ceiling first, then port the recipe up — the recipe transfers upward, measurements do not transfer downward.
  **Three costs are accepted and must appear in Limitations, not be glossed as "future work":** (a) the **external-validity gap does not close** — "are these findings specific to this base?" stays unanswered; (b) the **capacity question is unmeasurable** — "does the skill conflict shrink as capacity grows?" cannot be asked at one size point; (c) **ADR-0018's curve requirement is not met** — a single marked point is reported, not a measured curve. The same-family rule from ADR-0027 is **deferred, not cancelled**: whenever that second pass happens, family and size must not change together, or the difference is attributable to neither (ADR-0017).
  Harness never enters the GPU (embedder on CPU, index in CPU RAM/disk) — that is the fits/doesn't-fit difference. Historical note: the "bottleneck is KV-cache, not weights" claim was **measured false for the 12B base** (KV was 18% of weights); re-measure per base, never assume.
- **Actual dev machine (corrected 2026-05-29): RTX 5070 Laptop, ~12 GB VRAM, Blackwell (sm_120), CUDA 13.1** — NOT the RTX 4070 / 8 GB the older docs assume. Blackwell/sm_120 + CUDA 13.1 is bleeding-edge: PyTorch, `bitsandbytes`, `flash-attn`, `Unsloth` all need recent Blackwell-compatible builds. The 8 GB figure in older docs is the *end-user accessibility target*, not our training rig.
- **Local machine is for prototyping; real training runs go to the cloud** (Modal; Colab/Kaggle/RunPod as alternatives). Validate the pipeline locally on tiny models before spending cloud quota.
- **Currency lives in the library, not the model's brain.** Laws change; weights don't. Keep legal-currency concerns for the RAG layer — do not try to bake current statutes into fine-tuning.
- **Expert register is the training target; citizen plain-language is an app-layer prompt mode** (ADR-0010, in force — see the trap above). Correctness/grounding comes from RAG. Register held at ~1.0 across the 12B line.
- **License-clean data.** Use only public/open sources (Mevzuat.gov.tr, Resmi Gazete, Yargıtay open portal, Kaggle/HF open datasets). **Never** use commercial sources (Lexpera, Kazancı) — copyright poison. Mask PII in training data. (Repo is **Apache-2.0 and fully public** — this rule is why that transition needed no cleanup.)

## Technical stack

- **Environment:** `uv` + Python 3.11. WSL2 (Ubuntu 22.04) + **Blackwell-compatible CUDA (13.x — exact version verified at install; NOT 12.1)**. Python work runs under `source ~/code/global_venv/bin/activate`.
- **Training:** PyTorch 2.4+, Unsloth (primary; fall back to TRL+PEFT+transformers), bitsandbytes 0.43+ (NF4 4-bit), FlashAttention-2.
- **Method: QLoRA per branch, then task-vector merge (ADR-0027).** Per-branch QLoRA — `r=16`, `lora_alpha=32`, `target_modules="all-linear"`, `lora_dropout=0.05`, `batch=1`, `gradient_checkpointing=True`. **Every branch trains from the RAW BASE, independently.** This is a validity requirement, not a style choice: a task vector is defined as `τ = θ_ft − θ_base`, so all branches must share one `θ_base`. Training one branch on top of another produces sequential SFT, not a task vector — it destroys the very thing we set out to measure.
  Merging is **simultaneous k-way** TIES/DARE, not iterative — `TIES(TIES(τg,τa),τr) ≠ TIES(τg,τa,τr)`, because TIES trims, elects signs and averages across *all* vectors at once. Each LoRA is materialized as `ΔW = (α/r)·BA` in **bf16**, merged in **full weight space**, and quantized **last**. Merging runs on **host RAM, streaming tensor-by-tensor** — never on the GPU.
  **The main result is RAW TIES; norm-balanced is the ablation — [ADR-0052](docs/adr/0052-merge-norm-dengeleme-hukmu-tersine.md) reversed ADR-0036's prescription.** ADR-0036's *premise* was confirmed and still holds: branches train at very different scales (`τ_g` 1.083 steps @1e-4 · `τ_a` 70 steps @1e-5, ‖τ‖ ratio **8,87×**) and TIES' sign-election is mass-weighted. Its *inference* — "without normalization the small branch is erased" — was **measured false**: raw TIES did not erase `τ_a` (0,506 → 0,766 — **re-scored 2026-08-06**, [#57](docs/record/research_log/2026-08-06-cekinme-aleti-onarimi.md); the old tool read 0,607 → 0,877 and the **jump is unchanged at +0,26**); balancing crushed `τ_g` instead. `‖τ‖` is measured and reported **unconditionally** for every branch.
  **Merging itself costs no training compute** — that is what makes sweeping merge techniques realistic. But sweep on **DEV**, never on the frozen CANON test set.
- **Deploy pipeline:** per-branch QLoRA (NF4) → materialize ΔW (bf16) → k-way merge (full weight space, host RAM) → quantize via llama.cpp (**Q4_K_M**) → GGUF → consumer GPU.
- **Multimodal / OCR is NOT a base-selection argument and never was measured.** For Turkish the right architecture is a **separate OCR preprocessor, not native VLM OCR**: dedicated engines beat general VLMs on Turkish, and `ğ→˘g` / `ş→¸s` / `İ→Ì` breakages corrupt RAG matching in legal text (OCRTurk, arXiv:2602.03693).
- **Data format:** chat-template JSON (`messages` with `user`/`assistant` roles).
- **Eval: 6-mode CANON (ADR-0011), extended by ADR-0027 with a DEV/TEST split.** Modes: M1 distractor-faithfulness · M4 oracle ceiling · M2 near-miss refusal · M2b multi-source-miss refusal · M3 empty-context refusal · **M5 blind/parametric = ANTI-TARGET** (must NOT rise). Harness-ON counterparts: `h1`, `h2b`.
  **Regime invariants — a mismatch does not error, it just voids the comparison:** seed **3407** · eval-mirror **900-char** chunk clip · A1 = **answered-only** macro · **thinking ON with a budgeted forced close: 1024 thinking + 512 answer tokens** (ADR-0043).
  **Why forced closure exists** (`research_log` #42): under `--thinking on` the bare base **never closes `</think>`** in M1/M2/M5 — it oscillates between answering and abstaining and returns an empty `content` with HTTP 200. **Non-termination, not truncation**: raising the budget 8× changed nothing. `τ_g` *does* terminate on its own — fine-tuning stabilized the reasoning. Cost of the mode: **249 → ~1198 tokens/answer (~4.8×)**.
  **TEST = `data/eval/canon/` (40+35), frozen. DEV = CANON-protocol items**, and all merge/hyperparameter selection happens there — sweeping against the frozen set would burn it for selection and make every number optimistic.
  **Judge = four-layer defense:** judge-free backbone (regex abstention + deterministic citation verification) · a 3-family panel only on judgment axes (M1/M4), κ via `judge_agreement.py` · **family exclusion** (no subject graded by its own family's judge) · self-preference measured. **Human-κ DESCOPED.** The judge's **re-run noise floor is ~0,3 A1 points** — nothing smaller is interpreted.
  **Mandatory pre-step:** calibrate the refusal-detection regex on *every* competitor family. Left uncalibrated it undercounts their refusals and shifts scores **in our favor**.
- **Comparison fairness — [ADR-0057](docs/adr/0057-harness-rekabet-kapisi-esit-sinav.md), "eşit sınav".** An ON ↔ OFF comparison delivers a verdict **only on matched axes**: same questions · **same source count** · same gold condition · same regime. Unmatched axes are reported with a **CEILING/undefined** stamp, and the sentence *"ON is behind here"* is **not constructed** for them.

## Working notes

- Project docs and the working language are **Turkish.** Match that language in docs, comments, and commit messages unless asked otherwise. Code identifiers stay in English. *(This file is the exception — it stayed English.)*
- This **is a git repository**. Eval outputs in `outputs/eval/`, data in `data/`, tests in `tests/` (`pytest`). There is no formal build/lint setup — add when it earns its keep.
- **`scripts/` is grouped into five folders by function (T5, 2026-09-07)** — 72 files were a single flat pile:

  | folder | what lives there |
  | :--- | :--- |
  | `scripts/egitim/` | training · merge · GGUF · toolchain setup |
  | `scripts/olcum_uretim/` | harness runners · the single generation body · diagnostics · VRAM/token measurement |
  | `scripts/puanlama/` | judging · scoring · tables · `llm_client` · `runlock` |
  | `scripts/erisim_korpus/` | retriever · recall · corpus integrity · citation verification |
  | `scripts/veri_hazirlik/` | SFT/ORPO/RAFT dataset construction · B8/B10/CP2 harvest chain |

  **Sibling imports are extension-less** (`import runlock`, `from build_sft_v2b import …`) and
  survive the split only because **26 files carry an identical path-bridge block** — grep it with
  `grep -rl "yol köprüsü" scripts/`. `tests/conftest.py` mirrors the same logic. **If you change one,
  change both**, or the tests will exercise a path production never sees.
  Historical paths in `docs/record/**` and `docs/adr/**` were **deliberately left pointing at the old
  flat layout** — they record *"on that day it was run from this path"*. The record is not cleaned.
- **Base model = a parameter with a working assumption, not a fixture.** Operative base: **Qwen3.5-4B**. We do our OWN fine-tune. Mecellem stays **cite-only** (ADR-0016/0020) — it is a CPT foundation base, not an assistant, so "we beat it" is a category error and is never claimed. TurboQuant (arXiv:2504.19874) is future-work and **is not in llama.cpp**; today's lever is `--cache-type-k/-v q8_0` (`knowledge/summary_turboquant.md`).
- **Data hard rule, learned the hard way: EDA-verify every dataset before trusting it** — `newmindai/EuroHPC-Legal` looked great (43K, Apache 2.0) but sampling revealed garbage (mismatched Q&A, hallucinated laws, Ottoman-era content) and was rejected. Scope is **current Republic-of-Turkey legislation only.** Ground truth = Mevzuat.gov.tr. Data we lack (plain-language, citizen-niche, scenario→statute) is produced via **grounded synthetic generation** (real statute text → LLM generates pairs → verify).
- **Live legislation source: the `bedesten.adalet.gov.tr/mevzuat` JSON API** — reverse-engineered from `saidsurucu/mevzuat-mcp` (MIT), contract verified 4/4. Auth-free, no Playwright. Search + full text + article tree; the same backend also serves case law. Contract: [`docs/BEDESTEN_API.md`](docs/BEDESTEN_API.md), probe: `scripts/erisim_korpus/bedesten_probe.py`. **Requires a Turkish IP** (the gov firewall blocks foreign/VPN IPs). The contract works but **the product does not use it yet** — debt B6.
- **Corpus and index:** `data/corpus/mevzuat_maddeler.jsonl`; the live index is `data/index/mevzuat_bge_m3_s2/` (**S2** — carries the validity field + sub-article identity), and **since 2026-09-07 the retriever actually USES it**: `getir()` defaults to `Yururluk.YALNIZ_YURURLUKTE` and drops repealed articles. Until that day this line MISLED — the field was carried but never read, and 2 of 800 retrieved sources on a real run were repealed articles served to the citizen. Measured: the filter left `recall@10` at **0,9500** and took the leak from **2 → 0**. The corpus now also carries a snapshot manifest (`data/corpus/KUNYE.json`: 2026-08-06 · 892 laws · 40.496 articles · 2.547 repealed · scope = statutes only). The pre-S2 index is kept only to reproduce pre-S2 numbers. Retrieval is hybrid BM25 + `bge-m3` fused with RRF; a vector database was measured and **rejected** (brute force is 8,2 ms/query, index 83 MB).
