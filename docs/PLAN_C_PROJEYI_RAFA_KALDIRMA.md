# Plan C — projeyi `v0.5` hâlinde rafa kaldırma (uygulanmıyor, yalnız plan)

> **Durum: uygulanmıyor.** Bu belge yalnız bir eylem planıdır; karar verilene kadar hiçbir adım atılmaz.
> Karar verilirse adımlar sırayla işlenir, kutular kontrol geçince işaretlenir, iş bitince bu dosya silinir.

## Ne olacak (karar verilmiş uç durum)

- **`master`** = `v0.5` kodu. Yayında görünen şey (GitHub varsayılan dalı) budur.
- **HF modeli** (`Rfetha/HakHukuk-4B-GGUF`) olduğu gibi kalır; ağırlıklar değişmez.
- **Sürüm numarası `v0.5` kalır.** `v0.5.1` etiketi yok. `pyproject` sürümü ve model kartı `v0.5` der.
- **`develop`** olduğu gibi kalır; silinmez, temizlenmez. Geri dönüş yolu budur.
- **Pano (`law-slm-board`)** kapatılır; önce içeriği bir `.md` yedeğine alınır.
- Yeni konu (eczacı fikri vb.), tez ve hoca görüşmesi **bu planın dışında**.

## Verilen kararlar (2026-10-19)

| # | karar |
| :--- | :--- |
| K1 | `v0.5` etiketi (`ab3641e`) **yerinde kalır**; master etiketin önüne geçer, numara aynı kalır |
| K2 | Model kartındaki iki düzeltme (aşağıda) master'a **girer** |
| K3 | HF'deki model kartı master'daki kartla aynı olacak şekilde **güncellenir** (herkese açık yükleme; yine de yüklemeden önce son bir onay) |
| K4 | Depo **arşivlenmez**; bitmemiş olsa da açık ve yazılabilir kalır |

## Neden master'da kod düzeltmesi gerekiyor

Master'daki `hakhukuk` paketi `scripts/` klasörüne yol köprüsüyle bağlı (`hakhukuk/cekirdek/araclar.py:24`,
`atif_dogrula`, `getirici`, `madde_anahtar`, `ret_deseni` `scripts/` içinde). `develop`'ta bunlar pakete
taşındı (kusur 11). Master olduğu gibi kalırsa kod yalnız depo klasöründen çalışır; `pip install` ile kurulan paket
çalışmaz. Düzeltme kapsamı (`git diff master develop` ile ölçüldü, 2026-10-19): `hakhukuk/` altında 11 dosya,
+701 / −30 satır; ağırlıklar ve ölçüm değişmez.

Model kartı / README'de `develop`'ta düzeltilmiş iki iddia (master'da hâlâ yanlış/eksik):
- Master: "QLoRA (NF4)". Doğrusu: bf16 taban + LoRA, QLoRA değil ([ADR-0031](adr/kararlar-0027-0044.md#adr-0031)).
- Master'da yok: eğitim ve ölçüm sorularının çoğu `gpt-4o-mini` (OpenAI) ile üretildi, çekinme cevapları şablon.

> `develop`'taki `README.md` ve `MODEL_CARD.md` bağlantıları develop'un klasör düzenine göre (`docs/yontem/...`).
> Master'ın düzeni eski (`docs/OLCUM.md`). **develop'tan dosya kopyalama; yalnız yukarıdaki iki içerik
> düzeltmesini master'ın kendi bağlantılarıyla elle uygula.**

## Adımlar

### A — Hazırlık (yerel, geri alınabilir)

- [ ] **A1. Pano yedeği.** `gh issue list -R Rfetha/HakHukuk --state all --limit 500 --json number,title,state,labels,body,createdAt,closedAt,comments,url`
  ve `gh project item-list 3 --owner Rfetha --format json --limit 500` çıktıları tek `.md`'ye çevrilir
  (pano durumuna göre grup, her kartın gövdesi + etiketi + durumu + yorumları, sayı değiştirilmez) →
  `docs/arsiv/pano-yedegi-<tarih>.md`, `develop`'a commit. **Doğrulama:** kart sayısı 74, yorum sayısı 19
  (2026-10-19 itibarıyla), dosyada gizli bilgi yok (`grep -iE "ghp_|gho_|secret|password"`).
- [ ] **A2. Yerel paket yedeği.** `git bundle create ~/yedek/HakHukuk-<tarih>-develop.bundle --all` →
  **doğrulama:** `git bundle verify` temiz.
- [ ] **A3. Çalışan iş kalmadığını gör.** `modal app list` (çalışan/zamanlanmış iş yok) ·
  `/home/ersoy/code/Hukuk-SLM-15` işçi ağacı `develop` ile aynı commit'te (2026-10-19: ikisi de `b643cb6`),
  hiçbir şey commit'lenmemiş bırakılmadı → **doğrulama:** `git -C ... status -sb` temiz.

### B — `master` düzeltmesi

Ayrı işçi ağacında yapılır, `develop` bozulmaz: `git worktree add ../Hukuk-SLM-v05 master`.

- [ ] **B1. Paket düzeltmesini al.** `git checkout develop -- hakhukuk` — **yalnız `hakhukuk/`**.
  `pyproject.toml` alınmaz (farkı iki yorum satırıdır, develop'un test yollarını anar). `tests/` alınmaz:
  master'da testler düz klasörde (`tests/test_*.py`), develop'ta `tests/urun/...` altında; iki düzeni karıştırma.
- [ ] **B2. Pakete scripts'ten bağımsızlık kontrolü.** Temiz bir venv'e `pip install .` →
  `hakhukuk --help` çalışmalı; `scripts/` klasörü olmayan bir kopyada `from hakhukuk.cekirdek.getirici import Retriever`
  hata vermemeli. **Doğrulama:** develop'taki `tests/urun/test_kusurlar.py` dosyası **commit'lenmeden**, geçici
  olarak master işçi ağacına kopyalanıp koşulur (kusur 11'in kapısı bu testtir); yeşil olmalı.
- [ ] **B3. Master'ın kendi testleri bozulmadı.** `python -m pytest -q -p no:cacheprovider -m "not slow"` master
  işçi ağacında düzeltmeden **önce** ve **sonra** koşulur; sonuç karşılaştırılır. Master'ın `scripts/` kopyaları
  ile paket artık aynı kaynağı paylaşmıyor olabilir; kırılan test varsa nedeni yazılır, **zorla geçirilmez**.
- [ ] **B4. Model kartı düzeltmeleri (K2).** `MODEL_CARD.md` ve `README.md`'de yalnız şu iki içerik
  düzeltmesi, master'ın kendi bağlantılarıyla: (1) QLoRA → bf16 + LoRA, (2) `gpt-4o-mini` ile üretim beyanı.
  README'deki "335 passed, 2 xfailed" satırı, B2/B3'te çıkan gerçek sayıyla değiştirilir ya da develop'taki gibi
  sayısız bırakılır. **Doğrulama:** `git diff master -- MODEL_CARD.md README.md` yalnız bu üç yeri gösterir.
- [ ] **B5. Commit.** Tek commit, Türkçe, yapay zekâ imzası yok (CLAUDE.md "No AI attribution"). Etiket
  **taşınmaz** (K1); `v0.5` hâlâ `ab3641e`'yi gösterir.
- [ ] **B6. Sürüm numarası kontrolü.** `grep -rn "0\.5\|0\.1" pyproject.toml hakhukuk/__init__.py` → paket sürümü
  ve GGUF dosya adı (`HakHukuk-4B-v0.5-Q4_K_M.gguf`) tutarlı.

### C — Pano kapatma (A1 `develop`'a **push edilmiş** olmalı)

- [ ] **C1. Yedek GitHub'da görünüyor.** `develop`'ta `docs/arsiv/pano-yedegi-<tarih>.md` açılıyor.
- [ ] **C2. Kartları kapat.** 66 açık kart tek yorumla kapatılır ("proje `v0.5` hâlinde rafa kaldırıldı;
  yedek: `docs/arsiv/pano-yedegi-<tarih>.md`"). **Doğrulama:** `gh issue list --state open` boş.
- [ ] **C3. Panoyu kapat.** `gh project close 3 --owner Rfetha`. Silme **yok** (kapalı pano geri açılır).

### D — Yayın (herkese açık, geri dönüşsüz sayılır → her biri ayrı onay)

- [ ] **D1. Push.** `master` ve `develop` push'u **sende**: `git push origin master develop`.
- [ ] **D2. HF kartı (K3).** Yüklemeden önce son onay alınır. `Rfetha/HakHukuk-4B-GGUF` model kartı master'daki `MODEL_CARD.md` ile aynı olacak
  şekilde güncellenir; dosya adı ve revizyon değişmez. **Doğrulama:** HF sayfasında "QLoRA" geçmiyor.
- [ ] **D3. Dışarıdan kurulum.** Temiz bir ortamda `pip install git+https://github.com/Rfetha/HakHukuk.git` →
  `hakhukuk --help` çalışıyor; README bağlantıları 404 vermiyor (`curl -sI`).
- [ ] **D4. Oturum hafızası.** `~/.claude/projects/.../memory/` içindeki "bu proje sürüyor" notları
  (`phase1-execution-state`, `law-slm-board`, `paper-target` vb.) rafa kalktığını yansıtacak şekilde güncellenir.

## Geri dönüş

`develop` ve `outputs/`, `data/` olduğu gibi duruyor; A2'deki paket yedeği ayrıca var. Projeye dönmek:
`git checkout develop`, pano `gh project` ile yeniden açılır, kartlar A1 yedeğinden `gh issue reopen` ile geri
alınır. `develop`, master'ın soyundan geldiği için (`git merge-base --is-ancestor master develop` doğru) projeye
dönüşte master'daki düzeltme commit'i `develop`'a `git merge master` ile alınır; B4'teki model kartı farkları
`develop`'ta zaten düzeltilmiş olduğundan orada çakışma çıkabilir, elle çözülür.

## Kapsam dışı

- Yeni konu seçimi, tez konusu, danışmanla görüşme.
- Ağırlıkları, GGUF'u ya da ölçüm sayılarını değiştirmek.
- `develop`'u temizlemek, depoyu arşivlemek (K4), geçmişi yeniden yazmak.
