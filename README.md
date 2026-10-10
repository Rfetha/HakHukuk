# HakHukuk

A 4B Turkish legal assistant that runs on a laptop GPU and answers only from the statutes it is given.

[Model card](MODEL_CARD.md) · [Türkçe](docs/README.tr.md) · [Roadmap](docs/ROADMAP_v1.md) · [Weights](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) · [Index](https://huggingface.co/datasets/Rfetha/HakHukuk-mevzuat-bge-m3-s2) · [License](LICENSE)

## What it does

Given a question and the text of the relevant articles, the model either answers and cites the
article it relied on, or says that the provided sources do not cover the question. In law a
confident but wrong article number does more harm than silence, so the two behaviours were
trained separately: one LoRA branch for grounding, one for abstention, merged as task vectors
with TIES on top of `Qwen/Qwen3.5-4B`. A retrieval layer (BM25 + `bge-m3`) finds the articles
and ships with the model.

## Quick start

Container (recommended; it enforces the server flags the numbers were measured with and verifies
every download by `sha256`):

```bash
git clone https://github.com/Rfetha/HakHukuk && cd HakHukuk
docker compose -f docker/compose.yaml up      # API 127.0.0.1:8000 · llama-server 127.0.0.1:8080
```

Python package (expects `llama-server` on `127.0.0.1:8080`; flags in
[MODEL_CARD §7](MODEL_CARD.md#7-çalıştırma)):

```bash
pip install -e .
hakhukuk "Askerlik nedeniyle iş sözleşmesi ne olur?"
```

Weights only:

```bash
hf download Rfetha/HakHukuk-4B-GGUF HakHukuk-4B-v0.5-Q4_K_M.gguf --local-dir models/gguf
```

The model alone does not reproduce the reported numbers; they were measured with the retrieval
layer on.

## Headline numbers

| DEV set, n=80, retrieval on | |
| :--- | ---: |
| Faithful-answer mass (two judge families) | 0.694 – 0.801 |
| Fabricated article numbers | 0 / 114 |
| Unnecessary abstention (gold article in context) | 4 / 80 |
| Answer resting on the wrong article | 8 / 80 |
| VRAM (4,096 context) | 3.09 GiB |
| Cost per answer | $0 (local) |

The two ends of the range are the same 80 answers scored by `gpt-4o-mini` (0.8011) and
`claude-sonnet-5` (0.6940). Competitor comparison, frozen-test result and limits:
[MODEL_CARD §5](MODEL_CARD.md#5-sonuçlar).

## What it does not promise

- It is not legal advice. Every article number it produces must be checked on
  [mevzuat.gov.tr](https://www.mevzuat.gov.tr).
- Without the retrieval layer it does not produce the reported results; without sources it gives
  confident but wrong legal content.
- Scope is Turkish statutes in force only: 892 laws, 40,496 articles, a 2026-08-06 snapshot.
  Regulations, bylaws, decrees and communiqués are not covered.
- No parity claim with the competitor models.

`v0.5` is a measurement release: the weights have not changed since `v0.3`. It was tagged `v1.0`
until 2026-10-10; the name `v1` is reserved for the release at the end of the next training round.
The version numbers (artifact, file, product) are explained in [MODEL_CARD §1](MODEL_CARD.md#1-model-nedir).

## Repository map

| where | what |
| :--- | :--- |
| [`hakhukuk/`](hakhukuk/) | product package: `cekirdek/` (service, prompt, classifier) · `arayuz/` (CLI, TUI, HTTP API) · `dagitim/` (verified download) |
| [`scripts/`](scripts/) | the measurement line, kept separate from the product |
| [`docker/`](docker/) | Dockerfile and `compose.yaml` |
| [`docs/`](docs/README.md) | all documents; index in `docs/README.md` |
| [`docs/adr/`](docs/adr/README.md) | decision ledger, through ADR-0088 |
| [`docs/record/`](docs/record/README.md) | chronological research record, through entry #71 |
| [`outputs/eval/`](outputs/eval/README.md) | raw evaluation outputs and run manifests, as `<group>/<run>/` |
| [`tests/`](tests/) | `pytest`: 335 passed, 2 xfailed |

## Research record

Negative results are kept with the same care as positive ones: runs voided by their own
pre-registered gate, decisions reversed by measurement, a gate that failed. Every number has a run
manifest (`KUNYE.json`) that fixes its metric, `n`, judge, seed and output file. Detailed
measurement tables are in [`docs/OLCUM.md`](docs/OLCUM.md).

## Contributing

Criticism, fixes and especially reproduction attempts are welcome
([`docs/YENIDEN_URETIM.md`](docs/YENIDEN_URETIM.md)). A number that cannot be reproduced is a
bug report.

## License

Apache-2.0 ([`LICENSE`](LICENSE)) for weights, code, data and the research record. The base model
`Qwen/Qwen3.5-4B` is Apache-2.0.
