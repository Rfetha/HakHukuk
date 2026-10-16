# CLAUDE.md

Guidance for Claude Code in this repository. **This file is a MAP, not a report**: it says *where
things are* and *what rules bind you*. Measurement tables, sprint narratives and dated status live in
`docs/record/` and `docs/adr/`. When a round closes, update the **pointers** here, not numbers.
**Git history was reset on 2026-10-10** ([ADR-0088](docs/adr/kararlar-0064-0085.md#adr-0088)): the
repository restarts from a single commit. The old history (590 commits, all branches, tags `v0.2` ·
`v0.3` · `v1.0`) lives **outside** the repo in a local bundle, `~/yedek/HakHukuk-2026-10-10.bundle`.
Every commit hash cited in `docs/adr/**` and `docs/record/**` (e.g. `301a82f`) resolves there:
`git clone ~/yedek/HakHukuk-2026-10-10.bundle eski && git -C eski show 301a82f:<path>`.

## What this repository is

**HakHukuk** — an open-source Turkish legal assistant built on a small language model. Mission: make
legal language legible to the citizen. Apache-2.0: weights, code, data and the whole research record
are public. Began as a master's thesis; since 2026-08-03 it is a **product**: the goal is the model
(beat Gemini 3.1 Flash-Lite, then reach Flash and Pro). An arxiv paper is a by-product.

- `v1` = model layer (fine-tuned model + retriever + harness, shipped end to end). **Tagged `v0.5`**
  (tagged `v1.0` on 2026-09-13, renamed 2026-10-10; the name `v1` is reserved for the release at the end
  of the next training round). `v2` = app layer / RL (`v2-RL-GRPO`, parked).
- Artifact: **`HakHukuk-4B-v0.1`** (internal id `tgta_v1`) — two LoRA branches trained independently
  from the raw base, merged as task vectors with **raw TIES**. Weights `Rfetha/HakHukuk-4B-GGUF`, public.
  Product/claim version (`v0.5`) and artifact version (`v0.1`) are deliberately split; since 2026-10-10
  the GGUF file name carries the product version (`HakHukuk-4B-v0.5-Q4_K_M.gguf`, same bytes)
  ([ADR-0065](docs/adr/kararlar-0064-0085.md#adr-0065)).
- `v0.5` (then named `v1.0`) was granted by re-reading the gate under a **second judge family** — the instrument changed,
  the weights did not ([ADR-0084](docs/adr/kararlar-0064-0085.md#adr-0084)). κ stayed below the tool's
  0.6 threshold; the judge panel is two families, not three.

**What the reframing kept — all of it.** Fixed seeds · logged runs · run manifests (`KUNYE.json`) ·
pre-registered gates · same-day record · an ADR per decision · the trap list. This is not ceremony: the
discipline repeatedly caught numbers about to be published wrong (a metric that rewarded refusing, a
validity gate that voided a degenerate model, a normalization prescription that measurement reversed).

## File tree

```
CLAUDE.md  README.md  MODEL_CARD.md  LICENSE  pyproject.toml  requirements.lock.txt
hakhukuk/            PRODUCT package (pip-installable)
  cekirdek/            core: tipler · istem · terazi · servis · araclar
  arayuz/              interfaces: cli · tui · api (thin shells over cekirdek)
  dagitim/             indir (artifact download + identity gate)
  veri/KUNYE.json      symlink -> data/corpus/KUNYE.json (single source, package-data)
scripts/             MEASUREMENT line, grouped by function (see "Working notes")
  egitim/ olcum_uretim/ puanlama/ erisim_korpus/ veri_hazirlik/  (+ hf_kart.py, yeniden_uret.sh)
tests/               pytest; unit (fake/stub) + real-DB integration (`@pytest.mark.slow`)
docker/              Dockerfile · Dockerfile.dockerignore · compose.yaml  (build context = repo root)
docs/                every document except the three root ones (index: docs/README.md)
  PRODUCT.md ROADMAP_v1.md ROADMAP_uygulama.md YAYIN_YOL_HARITASI.md EGITIM_ORTAMI.md MIMARI.md OLCUM.md README.tr.md
  BEDESTEN_API.md YENIDEN_URETIM.md HF_KARTI_INDEKS.md model-soyagaci.mmd
  adr/                 decision ledger   (kararlar-*.md + gemma4-12b-dersler.md)
  record/              research record   (kronoloji-*.md · kollar.md · yurutme-tuzaklari.md)
  superpowers/plans/   at most one live plan (ADR-0056; the ADR-0106 exception closed 2026-10-16); exists only while a phase plan is open
data/                corpus/ (ground truth) · eval/ (frozen) · train/ · index/ · _ham_ve_ara/
outputs/             eval/<group>/<run>/ (+ _artefakt/) · egitim/<task>/ (training-side evidence) · tg_v1/ · ta_v1/ (adapters; private HF backup per ADR-0091, F0.1)
models/              merged/ · gguf/   (28 GB, gitignored)
configs/  knowledge/ (literature summaries, thesis era · `mike-tarama/`: reference-app scan for the agent app)
```

`outputs/eval/` groups: `sprint1` · `cp` · `sprint2-olcum` · `faz0` · `gorev` · `hp`
([ADR-0087](docs/adr/kararlar-0064-0085.md#adr-0087); index in `outputs/eval/README.md`). A new run goes to
`outputs/eval/<group>/<run>/` with its own `KUNYE.json`. Files **inside** `outputs/eval/**` still carry the
old flat `outputs/eval/<run>` strings — the old→new map is in the ADR.

## Where to look

| you want | read |
| :--- | :--- |
| what to do next | **Status lives only on the board** [`law-slm-board`](https://github.com/users/Rfetha/projects/3) — one issue per task, an `epic` issue per phase; a card is closed by hand once its check passes, commits carry `refs #N` ([ADR-0108](docs/adr/kararlar-0064-0085.md#adr-0108)) · tasks and their checks: [`docs/ROADMAP_v1.md`](docs/ROADMAP_v1.md), phases F0–F5. Order decided 2026-10-10: Checkpoint 1 (Makale 1) → Checkpoint 2 (GRPO on the Checkpoint 1 winner, Makale 2, thesis) → legislation-scope/freshness round. `00-IS-SIRASI.md` was deleted that day · live plan: [`docs/superpowers/plans/2026-10-11-F0-zemin.md`](docs/superpowers/plans/2026-10-11-F0-zemin.md) (F0, opened 2026-10-11) · the agent app is a separate line outside the paper line: [`docs/ROADMAP_uygulama.md`](docs/ROADMAP_uygulama.md) ([ADR-0104](docs/adr/kararlar-0064-0085.md#adr-0104); calendar, tool-call measurement and tool-use RL placement: [ADR-0105](docs/adr/kararlar-0064-0085.md#adr-0105)) |
| direction and why | [`docs/YAYIN_YOL_HARITASI.md`](docs/YAYIN_YOL_HARITASI.md) — the two-paper plan, decisions, budget, risks · locked training environment: [`docs/EGITIM_ORTAMI.md`](docs/EGITIM_ORTAMI.md) · what the product promises and does **NOT** promise: [`docs/PRODUCT.md`](docs/PRODUCT.md) |
| the `v1` chain, product modules | [`docs/MIMARI.md`](docs/MIMARI.md) |
| every measurement, dated, with its source file | [`docs/record/README.md`](docs/record/README.md) — entries #39-#87 in five chronology files, per-entry anchors; **new findings continue at #88** (`kronoloji-87-98.md`) |
| why a decision went the way it did | [`docs/adr/README.md`](docs/adr/README.md) — one line per ADR with anchor; ledger runs to **0109**, next is **0110**; new ADRs are appended to `kararlar-0064-0085.md` with `<a id="adr-NNNN"></a>`. **0059 is RESERVED** (six places cite `ADR-0059 §sapma-1`); **0100 is reserved** for F0.12's data-license ADR (ADR-0099) |
| open defects and handover | [`ADR-0083`](docs/adr/kararlar-0064-0085.md#adr-0083) — 4 open (5a · 23 · 27 · 31), 3 handed on (6 · 11 · 12b); §EK E.5 holds the nine questions that go into the next grill |
| artifact registry | [`docs/record/kollar.md`](docs/record/kollar.md) — every trained branch and merge has its identity here; **an artifact with no row is nameless and must not be used**. Family tree: [`docs/model-soyagaci.mmd`](docs/model-soyagaci.mmd) |
| the headline number and its caveats | [`MODEL_CARD.md`](MODEL_CARD.md) and `docs/record/kronoloji-63-71.md` — never quote from memory |
| all docs | [`docs/README.md`](docs/README.md) |

`tests/test_belgeler.py` walks every link in the live docs (root files and `docs/*.md`), so a dead
pointer **fails a test**. Older prose saying "`research_log` #42" means "chronology #42"; every ADR and
entry carries an HTML anchor (`ADR-0057` → `kararlar-0045-0063.md#adr-0057`). Never "repair" an old path
inside `docs/adr/**` or `docs/record/**` on your own — they record what that day said.

### Read before doing anything

- **[`docs/record/yurutme-tuzaklari.md`](docs/record/yurutme-tuzaklari.md) — before ANY run.** The list of
  *"produces a wrong number without erroring"* patterns, every one of which has actually bitten: dropped
  `--data`/`--thinking off`, uncalibrated refusal regex, missing `--target-modules`, `set -e` swallowing the
  error, half-finished quantization that still leaves a file on disk. **This line's failure class is silent
  wrongness, not crashes.**
- **[`docs/adr/gemma4-12b-dersler.md`](docs/adr/gemma4-12b-dersler.md)** — the retired 12B line's ADRs
  0001-0026. Part (A) lessons is base-agnostic: *"plain SFT destroys abstention"*, *"the eval mirror is
  mandatory"*, *"`spawn()` not `remote()`"*. **Read part A before designing any experiment.**

## Lessons a new session must not get wrong (all measured, not assumed)

- **The gain came from the INSTRUMENT, not the model.** Five "wrong number without erroring" defects were
  found in the measuring line (question set, RRF fusion, DEV↔TEST composition, an unequal production
  budget, a gate clause with no anchor). Weights never changed. Trust a number only with its `KUNYE.json`.
- **Read it by eye.** A numeric gate passed a broken measurement; reading the items one by one caught it
  three times (chronology #60 · #61 · #65). Count nothing you have not looked at.
- **Both of the harness's original justifications are refuted** (fabricated article numbers: the class was
  empty; the rejection gate cannot fire in this regime, #56). What survived: without a retriever there is no
  product, plus a set of measured mechanisms.
- **The biggest single loss is over-refusal and the model owns it** — the gold article is in context and the
  model abstains anyway. The abstention *detector* was itself wrong (it read our own answer template's
  discarded-sources rationale as a refusal, [ADR-0061](docs/adr/kararlar-0045-0063.md#adr-0061)); the
  sufficiency preamble was removed ([ADR-0063](docs/adr/kararlar-0045-0063.md#adr-0063)).
- **Binding metric is mass** (faithful-answer mass) — an unanswered question is worthless to a citizen.
  Misattribution is paid on its own axis (B1), not with a prompt patch. The headline is an **unconditional
  range across the judge families that scored it**, never a single number picked after the fact; competitor
  arms stay single-judge and are stamped as such ([ADR-0057](docs/adr/kararlar-0045-0063.md#adr-0057)).
- **The product path must equal the measured path.** `hakhukuk.cekirdek.servis.answer()` forces the thinking
  channel closed in a second pass exactly as the measurement line does
  ([ADR-0080](docs/adr/kararlar-0064-0085.md#adr-0080)); a caller driving `llama-server` directly still hits
  the original blank-answer defect.
- **Plain language is the presentation layer, not a training target.** Training toward plain/short answers
  lowered accuracy ([ADR-0010](docs/adr/gemma4-12b-dersler.md#adr-0010)). Train for correctness and
  abstention; simplify at the prompt layer.
- **Next first-rank axis is B1 (misattribution).** The B10 over-refusal round closed with NO training
  ([ADR-0062](docs/adr/kararlar-0045-0063.md#adr-0062)); its tooling (`scripts/veri_hazirlik/b10_hasat.py`,
  Modal `harvest_b10`, the leakage filter) is intact and reusable — do not rebuild it.

## Documentation discipline (HARD RULE)

Intermittent solo OSS project: weeks can pass between sessions and the repo is the only thing that
remembers. The research record is the most valuable thing here, more than the weights.

- **Every significant experiment, result or decision is written down immediately.** Two homes:
  chronology under `docs/record/` (narrative + numbers + lesson, appended to the newest `kronoloji-*.md`
  with an `<a id="NN"></a>` anchor) and `docs/adr/` (a discrete ADR per big decision). A finding that
  lives only in chat is lost.
- **Numbers are sourced, not remembered:** exact metric, n, judge, seed and the file it lives in
  (`outputs/eval/...`).
- **Negative and surprising results are first-class** — same rigor as wins.
- When a decision contradicts an older doc, **flag the contradiction in both places** rather than silently
  overwriting.
- Doc types: **record** (what happened) · **decision** (why, which alternative was eliminated) · **spec**
  (`docs/superpowers/specs/`) · **plan** (`docs/superpowers/plans/`, `- [ ]` boxes, closing block when
  executed; **at most one live plan**, ADR-0056) · **execution** (`sprint*.md` at root, only the open one).
  Empty specs/plans folders do not exist (git tracks no empty folder). A closed plan is deleted the day it
  closes and becomes record (ADR-0083 precedent). A doc that says "what's next" is a plan and cannot sit
  under `record/`.

## Core constraints that shape every decision

- **Accessibility over raw performance.** Product target = consumer GPUs. **The base is a PARAMETER, not a
  decision (ADR-0026): no script carries a default; an undefined base must fail EARLY** — silently falling
  back to the wrong model turns a multi-hour run into invisible garbage. Working assumption: **Qwen3.5-4B**
  (ADR-0027). No run starts before the 6-item base verification gate (llama.cpp architecture support ·
  chat-template render verified **by eye** · turn-marker assert · Unsloth/sm_120 · quantization · license).
  **≤8 GB is a SOFT gate** (ADR-0018): larger configs are reported at a cost on the accessibility axis.
  Sequencing preference, not a lock: push 4B toward its ceiling first, then port the recipe up — the recipe
  transfers upward, measurements do not transfer downward. Three accepted costs belong in Limitations, not
  "future work": external validity does not close, the capacity question is unmeasurable at one size, and
  ADR-0018's curve is not met.
- Harness never enters the GPU (embedder on CPU, index in CPU RAM/disk). Re-measure the KV-cache-vs-weights
  claim per base; never assume.
- **Dev machine: RTX 5070 Laptop, ~12 GB VRAM, Blackwell (sm_120), CUDA 13.x** — bleeding edge; PyTorch,
  `bitsandbytes`, `flash-attn`, Unsloth need Blackwell-compatible builds. The 8 GB figure in older docs is
  the end-user target, not our rig.
- **Local = prototyping only; real training and all measurement runs go to rented GPUs** — training on
  Modal, measurement on one GPU type chosen by the F0 pilot
  ([ADR-0097](docs/adr/kararlar-0064-0085.md#adr-0097)). The laptop is never counted as GPU capacity.
  Validate on tiny models locally first.
- **Currency lives in the library, not the model's brain.** Laws change, weights don't; keep legal currency
  in the RAG layer.
- **Expert register is the training target; citizen plain language is an app-layer prompt mode** (ADR-0010).
- **License-clean data.** Only public/open sources (Mevzuat.gov.tr, Resmi Gazete, Yargıtay open portal,
  Kaggle/HF open datasets). **Never** Lexpera/Kazancı. Mask PII.

## Technical stack

- **Environment:** `uv` + Python 3.11 (venv `~/code/global_venv`, activate in the same command:
  `source ~/code/global_venv/bin/activate && ...`). WSL2 Ubuntu 22.04 + Blackwell-compatible CUDA 13.x.
- **Training:** PyTorch, Unsloth (fall back to TRL+PEFT), bitsandbytes NF4, FlashAttention-2.
- **Method: QLoRA per branch, then task-vector merge (ADR-0027).** `r=16`, `lora_alpha=32`,
  `target_modules="all-linear"`, `lora_dropout=0.05`, `batch=1`, gradient checkpointing. **Every branch
  trains from the RAW BASE, independently** — a task vector is `τ = θ_ft − θ_base`, so all branches must share
  one `θ_base`; training one on top of another is sequential SFT and destroys what we measure. Merging is
  **simultaneous k-way** TIES/DARE (`TIES(TIES(τg,τa),τr) ≠ TIES(τg,τa,τr)`), each LoRA materialized as
  `ΔW = (α/r)·BA` in **bf16**, merged in full weight space on **host RAM, streaming tensor-by-tensor**,
  quantized **last**. **The main result is RAW TIES; norm-balanced is the ablation**
  ([ADR-0052](docs/adr/kararlar-0045-0063.md#adr-0052) reversed ADR-0036). `‖τ‖` is measured and reported
  unconditionally per branch. Sweep merges on **DEV**, never on the frozen TEST. The task-vector line is
  **frozen at `v1`** (`v2` starts from `tgta_v1`, ADR-0075).
- **Deploy:** per-branch QLoRA → materialize ΔW (bf16) → k-way merge → quantize via llama.cpp
  (**Q4_K_M**) → GGUF → consumer GPU. Containers: three boxes, two daemons, two images (ADR-0078);
  `docker/compose.yaml` is a **regime lock** (llama-server flags are the published ones, parsed as a gate in
  `tests/test_konteyner.py`). Run: `docker compose -f docker/compose.yaml up`. vLLM is not a measurement engine
  (ADR-0109); it is reserved for GRPO rollout generation (June 2027 pilot). The vLLM pilot scripts
  (`scripts/olcum_uretim/gguf_hf_cevir.py`, `toplu_uret.py`, `modal_pilot_vllm.py`) stay as tools.
- **OCR/multimodal is not a base-selection argument.** For Turkish, a separate OCR preprocessor, not VLM OCR.
- **Data format:** chat-template JSON (`messages` with `user`/`assistant`).
- **Eval: 6-mode CANON (ADR-0011) + DEV/TEST split (ADR-0027).** Modes: M1 distractor-faithfulness · M4
  oracle ceiling · M2 near-miss refusal · M2b multi-source-miss refusal · M3 empty-context refusal · **M5
  blind/parametric = ANTI-TARGET** (must NOT rise). Harness-ON: `h1`, `h2b`.
  **Regime invariants — a mismatch does not error, it voids the comparison:** seed **3407** · eval-mirror
  **900-char** chunk clip · A1 = answered-only macro · **thinking ON with budgeted forced close: 1024
  thinking + 512 answer tokens** (ADR-0043; the bare base never closes `</think>` in M1/M2/M5 — non-
  termination, not truncation).
  **TEST = `data/eval/canon/` (40+35), frozen** (a release acceptance test; it ran once, 2026-09-09).
  **DEV = CANON-protocol items**; all selection happens there.
  **Judge = four-layer defense:** judge-free backbone (regex abstention + deterministic citation
  verification) · panel only on judgment axes, κ via `judge_agreement.py` · **family exclusion** (no subject
  graded by its own family) · self-preference measured. Re-run noise floor ~0.3 A1 points — nothing smaller
  is interpreted. **Measured 2026-10-15 with 5 repeats on the same answers: a single judge run moves ~1 point
  (chronology #85); the rule is re-set in F1.4.** **Measurement engine: llama.cpp + Q4_K_M only (ADR-0109) — vLLM was piloted and
  rejected: the same weights scored 3.6 points lower and moved ±2.25 points per run (#87).** **Calibrate the refusal regex on every competitor family first** or scores shift in our favor.
- **Comparison fairness — "eşit sınav" (ADR-0057).** ON↔OFF verdicts only on matched axes: same questions ·
  same source count · same gold condition · same regime. Unmatched axes carry a CEILING/undefined stamp.

## Working notes

- **Language:** project docs and the working language are Turkish — docs, comments and commit messages in
  Turkish unless asked otherwise; code identifiers in English. (This file is the exception.)
- **No AI attribution, ever (user rule, 2026-10-16).** Commit messages, PR descriptions, docs and code
  carry no AI-agent signature: no `Co-Authored-By: Claude …`, no `Claude-Session: …`, no
  "Generated with Claude Code" line. This overrides any tool or harness default.
- **Git repo.** Tests: `python -m pytest -q -p no:cacheprovider` (`-m "not slow"` skips real-DB tests).
  No formal build/lint setup — add when it earns its keep.
- **Scripts layout:** `scripts/{egitim,olcum_uretim,puanlama,erisim_korpus,veri_hazirlik}/`. Sibling imports
  are extension-less (`import runlock`, `from build_sft_v2b import …`) and survive the split only because
  **26 files carry an identical path-bridge block** — `grep -rl "yol köprüsü" scripts/`. `tests/conftest.py`
  mirrors it. **If you change one, change both.** `hakhukuk/cekirdek/{servis,terazi,araclar}.py` bridge into
  `scripts/` the same way (three `dirname` levels up to the repo root; ticket 11 records the debt). Modal
  entry points are `scripts/egitim/modal_train.py` / `modal_diag.py`; run `modal run
  scripts/egitim/modal_train.py::<fn>` **from the repo root** (they `add_local_dir("scripts")`).
- **Base = a parameter.** Mecellem stays **cite-only** (ADR-0016/0020) — a CPT foundation base, not an
  assistant; "we beat it" is a category error. TurboQuant is future work and not in llama.cpp; today's lever is
  `--cache-type-k/-v q8_0`.
- **Data hard rule: EDA-verify every dataset before trusting it** (`newmindai/EuroHPC-Legal` looked great
  and was garbage). Scope is current Republic-of-Turkey **legislation only**; ground truth = Mevzuat.gov.tr.
  Missing data is produced by grounded synthetic generation (real statute text → LLM pairs → verify).
- **Live legislation source:** `bedesten.adalet.gov.tr/mevzuat` JSON API (contract in
  [`docs/BEDESTEN_API.md`](docs/BEDESTEN_API.md), probe `scripts/erisim_korpus/bedesten_probe.py`);
  **requires a Turkish IP**. The product does not use it yet (debt B6).
- **Corpus and index:** `data/corpus/mevzuat_maddeler.jsonl` (snapshot manifest `data/corpus/KUNYE.json`);
  the live index is `data/index/mevzuat_bge_m3_s2/` (S2: validity field + sub-article identity), and the
  retriever **uses** it — `getir()` defaults to `Yururluk.YALNIZ_YURURLUKTE` and drops repealed articles.
  Retrieval is hybrid BM25 + `bge-m3` fused with RRF; a vector DB was measured and rejected. The pre-S2
  index exists only to reproduce pre-S2 numbers.
