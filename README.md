# HakHukuk

> **A Turkish legal assistant: a 4B model small enough to run on a laptop, trained to say
> "that isn't in these sources."**
> Open-source **product** — weights + code + data + **the complete research record**.

[**Model card**](MODEL_CARD.md) · [Türkçe](README.tr.md) · [Roadmap](ROADMAP.md) · [Weights](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) · [Index](https://huggingface.co/datasets/Rfetha/HakHukuk-mevzuat-bge-m3-s2) · [License](LICENSE)

Most of a legal assistant's job is not answering — it is **not answering when the sources
don't support it.** A confident, wrong article number is worse than silence. `HakHukuk-4B` was
trained for both halves: **ground** the answer in the legislation it was given, and **abstain**
when that legislation does not cover the question.

## Install

All three components are published: weights, search index, and code. The container path
**enforces** the binding server flags — with a manual setup you must write them yourself.

```bash
git clone https://github.com/Rfetha/HakHukuk && cd HakHukuk
docker compose up          # API 127.0.0.1:8000 · llama-server 127.0.0.1:8080
```

The `indir` box pulls the GGUF and the index from a **pinned revision**, behind a `sha256` +
byte-count gate; if the gate fails, **neither daemon starts**. Requires an NVIDIA GPU and
Docker (compose v2.30+).

As a package:

```bash
pip install -e .
hakhukuk "Askerlik nedeniyle iş sözleşmesi ne olur?"   # CLI
hakhukuk-tui                                           # single-screen TUI
hakhukuk-api                                           # HTTP API
```

Weights alone:

```bash
hf download Rfetha/HakHukuk-4B-GGUF HakHukuk-4B-v0.3-Q4_K_M.gguf --local-dir models/gguf
```

⚠️ **The model alone does not reproduce the reported number.** The headline was measured with
the retrieval layer **on**; without sources the model produces confidently wrong legal content.

## Headline numbers

DEV set, `n=80` · retrieval on (`k=10`) · no preamble · seed 3407 · budget 1536.

| axis | value |
| :--- | ---: |
| **faithful-answer mass** | **69.4-80.1%** |
| `recall@10` (ceiling on mass) | 0.9500 |
| fabricated article numbers | **0 / 114** |
| over-refusal (gold in context, abstained anyway) | 4 / 80 |
| misattribution | 8 / 80 |
| VRAM (ctx 4,096) · cost per answer | 3.09 GiB · **$0** |

⚠️ **The headline is not one number but an unconditional range:** two independent judge
families scored the same 80 answers and got **0.8011 ↔ 0.6940**. Formatting the headline to the
outcome — one number when a gate passes, a range when you're unsure — is a self-deception
pattern this project rejects.

Competitor comparison, measurement regime, axis definitions, limits, and the sentences that are
**not** constructed from these numbers: [**MODEL_CARD.md**](MODEL_CARD.md).

## What it does **not** promise

- **It is not legal advice.** Every article number it produces must be verified on
  [mevzuat.gov.tr](https://www.mevzuat.gov.tr).
- **It is not 100% accurate.** Across 80 questions: 8 misattributions and 4 over-refusals.
- **Currency lives in the library, not in the weights.** Laws change; weights don't.
- **Scope: current Republic of Türkiye statutes only** (892 laws, 40,496 articles; a
  2026-08-06 snapshot). Regulations, decrees and communiqués are out of scope.
- **No parity claim.** The comparison is on DEV, without cost normalization.

## Versioning — three numbers, none interchangeable

| number | today | what it names |
| :--- | :--- | :--- |
| artifact | `HakHukuk-4B-v0.1` | the weights themselves; **permanent** |
| file | `HakHukuk-4B-v0.3-Q4_K_M.gguf` | content never changed, so **neither does the name** |
| product / claim | **`v1.0`** | the verification level the measuring instrument reached |

⚠️ **`v1.0` does not mean "the model improved"** — the weights never changed. What closed is
that the release gate's three clauses passed **under a second, independent judge family**
([ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)).

## Repository map

| where | what |
| :--- | :--- |
| [`hakhukuk/`](hakhukuk/) | **product package** — prompt · service · CLI · TUI · HTTP API · downloader |
| [`scripts/`](scripts/) | **the measuring instrument**, deliberately separate from the product |
| [`docs/record/research_log/`](docs/record/research_log/) | chronological research record — through **#71** |
| [`docs/adr/`](docs/adr/) | decision ledger — through **0085** |
| [`docs/record/kollar.md`](docs/record/kollar.md) | artifact registry. *An artifact with no row is nameless.* |
| [`docs/record/yurutme-tuzaklari.md`](docs/record/yurutme-tuzaklari.md) | the *"produces a wrong number without erroring"* patterns — every one has actually bitten |
| [`outputs/eval/`](outputs/eval/) | raw evaluation outputs and run manifests |
| [`tests/`](tests/) | `pytest` — **335 passed, 2 xfailed** |

## The research record is itself the asset

**Negative results are first-class.** This repository keeps, stamped and visible: runs voided
by their own pre-registered gate, a decision **reversed** because measurement contradicted it
([ADR-0052](docs/adr/0052-merge-norm-dengeleme-hukmu-tersine.md)), and a mid-gate that
**failed** ([ADR-0045](docs/adr/0045-ara-kapi-merge-onarim-kontrolu.md)).

Numbers are **sourced, not remembered**: every result's metric, `n`, judge, seed and output
file are fixed in a run manifest (`KUNYE.json`).

## Data and license

Sources are public and appropriately licensed only: mevzuat.gov.tr · the Official Gazette ·
the Court of Cassation's open portal · openly licensed datasets · synthetic pairs generated
from real statute text and **verified**. PII is masked in training data.
Data plan: [`docs/VERI_PLANI.md`](docs/VERI_PLANI.md).

**License: Apache-2.0** ([`LICENSE`](LICENSE)) — weights, code, data and research record. The
base model `Qwen/Qwen3.5-4B` is Apache-2.0; the attribution chain is in [`NOTICE`](NOTICE).

## Contributing

Contributions, criticism and **reproduction attempts** — especially reproduction attempts — are
welcome. If you cannot reproduce a number, that is a bug report.
