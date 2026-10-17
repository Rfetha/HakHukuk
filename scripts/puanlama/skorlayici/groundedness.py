#!/usr/bin/env python3
"""Hukuki Groundedness skorlayıcı — claim-level faithfulness (FactScore + ALCE iskeleti).

Karar (2026-06-08, [[eval-accuracy-gate]]): ANA metrik = groundedness/sadakat. "LLM 1-10
versin" DEĞİL — literatürdeki decompose-then-verify formatında, sayısal + tekrar-üretilebilir.

İKİ AŞAMALI (gerçek FactScore, Min+2022 — claim-count kaymasını azaltır):
  Aşama 1  extract_claims: CEVABI atomik iddialara böl (sıkı granülerlik kuralı, temp 0).
  Aşama 2  verify_claims:  her iddiayı KAYNAK MADDEYE karşı etiketle + atıfları GOLD'a
           karşı sınıflandır.  (Bölme ile doğrulama ayrı çağrı → bağlaşım kırılır.)

Metrikler:
  faithfulness     = SUPPORTED / toplam_iddia                       ∈ [0,1]   (FactScore)
  hallucination    = (CONTRADICTED + NOT_IN_SOURCE) / toplam_iddia   (sıkı — kaynağa-dayan)
  unsupported      = (CONTRADICTED + NOT_IN_SOURCE∧¬makul) / toplam  (gerçekten temelsiz;
                     "doğru ama bu maddede yok" iddiaları DIŞLAR → flu #4 ayrımı)
  cit_precision    = CORRECT / yapılan_atıf                          (ALCE, Gao+2023)
  wrong_ref_rate   = WRONG_REF / yapılan_atıf   ← yanlış maddeye yönlendirme (en tehlikeli)
  cit_recall       = gold madde doğru atıflandı mı (0/1)

Yer-gerçeği = `--source-field` (varsayılan `referans`). Mod:
  --mode data  (vars.): kaynak = TEK gerçek madde; "kaynak dışı" = ceza (grounded veri için doğru).
  --mode model: referans avukat-cevabı olabilir; NOT_IN_SOURCE∧makul cezası gevşetilir
                (tek-madde yer-gerçeği gerçek QA'yı tam ölçemez — gerçek groundedness Faz 2 RAG).

Tekrar-üretilebilirlik: claim sınırı hakem-öznel + temp=0 tam deterministik değil → `--runs N`
ile N kez koş-havuzla (claim havuzu birleşir, oran stabilize). Paper için runs≥3 önerilir.

Hakem yanlılığı (flu #2): üreten ile AYNI aile hakem self-preference yapar → faithfulness şişer.
`--judge-model` ile farklı/güçlü model seç (paper: gpt-4o / cross-family). Kullanılan hakem
summary'ye yazılır (şeffaflık). İnsan-κ kalibrasyonu (flu #3) = Aşama C (paper), kod kapatamaz.

Çıktı: outputs/eval/gnd_{label}.jsonl + gnd_{label}_summary.json
  Her girdi kalemi bir satır alır; `durum` ∈ puanli · sifir_iddia · hakem_hata · bos_girdi
  (F0.5 a — eskiden hakem hatası ve boş girdi kalemi sessizce düşürüyordu). Dosya iş bitene kadar
  `.part` adını taşır (F0.5 c); bütçe biterse koşu `.part` bırakıp durur, puanlanamaz.
Kullanım:
  python scripts/puanlama/skorlayici/groundedness.py --details outputs/eval/gnd_gpt_detail.jsonl --label gnd_gpt
  python scripts/puanlama/skorlayici/groundedness.py --details outputs/eval/gnd_gpt_detail.jsonl --label gnd_gpt \
         --judge-model gpt-4o --runs 3        # paper-grade
"""
import argparse
import json
import os
import statistics
from dataclasses import asdict

import openai

# Fiyat + kapı + JSON-modu tek yerde: llm_client (ADR-0029). Script başına kopya fiyat YOK —
# maliyet-normalize parite iddiası (ADR-0017) tek ve denetlenebilir bir tabloya dayanmalı.
# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────

from llm_client import (make_client, resolve, price, Dusunme, HakemKimligi,  # noqa: E402
                        note_provider, seen_providers, loads_tolerant, kullanim_oku, fatura_ozeti)
import runlock  # noqa: E402  — aynı label'a paralel yazım = sessiz bozulma (bkz. runlock.py)
from part_dosya import part_ile_yaz, tamamlanmis_jsonl  # noqa: E402
import olcum_aleti  # noqa: E402  — RQ2 anahtarları (F0.5 b): altın madde kırpması
import sonuc_deposu  # noqa: E402  — #74 R4: aynı hakem aynı girdiyi bir kez puanlar (vars. kapalı)

# Why bu liste: SDK yeniden denemeleri tükendikten sonraki API hatası (openai.APIError) ve
# hakemin bozuk/eksik JSON'u (loads_tolerant → ValueError; beklenmeyen biçim → TypeError,
# AttributeError, KeyError). Kalem `hakem_hata` satırı alır ve kütle o kalemde durur (kutle.py).
# KeyboardInterrupt ve öteki BaseException'lar yutulmaz; dosya `.part` kalır.
_HAKEM_HATALARI = (openai.APIError, ValueError, TypeError, AttributeError, KeyError)

# --- Aşama 1: atomik iddia çıkarımı (sıkı granülerlik → count kayması azalır) ---
EXTRACT_SYSTEM = (
    "Sen bir metni atomik OLGU iddialarına bölen bir ayrıştırıcısın. Sana bir hukuki CEVAP "
    "verilir; onu bağımsız doğrulanabilir iddialara böl. KURALLAR (count tutarlılığı için):\n"
    "- Bir iddia = TEK doğrulanabilir hukuki önerme (tek özne + tek yüklem).\n"
    "- Bileşik cümleleri 've / ayrıca / ancak' sınırlarından ayrı iddialara böl.\n"
    "- Selamlama, yönlendirme ('avukata danışın'), atıf parantezi İDDİA DEĞİL — dahil etme.\n"
    "- META/ATIF iddiası OLGU İDDİASI DEĞİL — ÇIKARMA: bir kanun/maddenin var olduğu, bir konuyu "
    "'düzenlediği', bir işlemin 'şu kanuna/maddeye tabi olduğu', 'şu maddede yer aldığı' türü "
    "ifadeler maddenin İÇERİĞİ hakkında bilgi taşımaz (atıf zaten ayrıca puanlanır). SADECE maddenin "
    "NE DEDİĞİNE — hangi hak/yükümlülük/şart/süre/usulü koyduğuna — dair önermeleri iddia yaz.\n"
    # ADR-0041: RAFT şablonunun 1. adımı kaynağın İÇİNDEN değil, kaynak SEÇİMİ hakkında bir
    # cümledir; iddia sayılınca `τ_g` içeren her hücre sistematik ceza alıyordu (CP6: desteksiz
    # iddiaların %58'i). Muafiyet DAR tutulur — sınırı yeniden hakem koşusunda elle doğrulanır.
    "- KAYNAK SEÇİMİ/ELEME cümlesi İDDİA DEĞİL — ÇIKARMA: öznesi bir kaynak olan ('KAYNAK 3', "
    "'bu kaynak', 'diğer kaynaklar') ve yüklemi o kaynağın soruyla İLGİLİ/İLGİSİZ olduğunu, hangi "
    "KONUYU ele aldığını ya da soruyu cevaplayıp cevaplamadığını söyleyen cümleler — ör. 'İlgili "
    "kaynak KAYNAK 3'tür', 'diğer kaynaklar farklı konuları ele almaktadır', 'KAYNAK 2 doğrudan "
    "sorunun cevabını vermemektedir', 'bu kaynak X'e dair bilgi sunmaktadır'. Bunlar ayrıştırma "
    "sürecini anlatır, hukuki bir önerme kurmaz.\n"
    "  ⚠️ MUAFİYETİN SINIRI DAR: kaynağın NE DEDİĞİNE dair her cümle normal şekilde iddia yazılır "
    "— 'KAYNAK 3'e göre süre 15 gündür' bir İDDİADIR (kaynak seçimi değil, kaynağın içeriği).\n"
    "- İddiayı kaynak metne bakmadan, yalnız cevaptan, kısa ve kendi başına anlaşılır yaz.\n"
    'SADECE JSON: {"claims": ["<iddia>", ...]}'
)

# --- Aşama 2: doğrulama + atıf sınıflama (kaynağa karşı) ---
VERIFY_SYSTEM = (
    "Sen Türk hukukunda titiz bir DOĞRULAMA uzmanısın. Sana SORU, KAYNAK METİN (gerçek kanun "
    "maddesi — yegâne yer-gerçeği), GOLD ATIF (kaynağın gerçek kanunu+madde no'su), tam CEVAP "
    "ve cevaptan çıkarılmış İDDİA LİSTESİ verilir.\n\n"
    "ÖNCE: kaynak metnin HANGİ KONUDAN bahsettiğini bir cümlede belirle (zihninde). Sonra her "
    "iddiayı SADECE bu kaynak metne göre etiketle. KENDİ HUKUK BİLGİNİ KULLANMA — iddia genel "
    "olarak doğru olsa bile, içeriği kaynak metinde GEÇMİYORSA destekli SAYILMAZ.\n"
    "(1) Etiketler:\n"
    "- SUPPORTED: iddianın içeriği kaynak metinde AÇIKÇA yazıyor / doğrudan çıkarılıyor.\n"
    "- CONTRADICTED: iddia kaynak metinle çelişiyor (yanlış aktarım).\n"
    "- NOT_IN_SOURCE: iddianın konusu kaynak metinde YOK (kaynak başka şeyden bahsediyor, ya da "
    "metin bir değişiklik/atıf listesi olup esas içerik içermiyor). İddia doğru görünse bile, "
    "kaynak sessizse → NOT_IN_SOURCE. `plausible`: genel hukuk bilgisiyle makul mü (true/false). "
    "⚠️ `plausible=true` iddiayı ASLA SUPPORTED yapmaz — yalnızca NOT_IN_SOURCE alt-ayrımıdır.\n"
    "ÖRNEK: kaynak '506 sayılı Kanunun 97nci maddesi değiştirilmiştir' gibi bir DEĞİŞİKLİK "
    "LİSTESİ ise ve iddia 'işsizlik sigortası için işten çıkarılmak gerekir' diyorsa → kaynak bu "
    "konuda sessiz → NOT_IN_SOURCE (plausible=true olabilir ama SUPPORTED DEĞİL).\n\n"
    "(2) Cevaptaki her kanun/madde ATFINI GOLD'a göre sınıflandır:\n"
    "- CORRECT: gold ile AYNI kanun VE AYNI madde no.\n"
    "- WRONG_REF: yanlış yönlendirme — doğru kanun ama YANLIŞ/var olmayan madde no, ya da "
    "tanınmayacak kadar bozuk kanun adı (ör. 'ASKE CEA KANUNU'). (Hukuken en tehlikeli.)\n"
    "- UNVERIFIABLE: GOLD'dan FARKLI, var olabilen bir kanuna düzgün atıf — kaynakla "
    "doğrulanamaz ama yanlış da değil. (Bozuk/uydurma değilse buraya koy, WRONG_REF'e değil.)\n"
    "Gold madde en az bir CORRECT atıfla anıldıysa source_cited=true.\n\n"
    "SADECE JSON: {"
    '"labels": [{"claim":"<iddia>","label":"SUPPORTED|CONTRADICTED|NOT_IN_SOURCE","plausible":true|false}], '
    '"citations": [{"ref":"<cevaptaki atıf>","verdict":"CORRECT|WRONG_REF|UNVERIFIABLE"}], '
    '"source_cited": true|false}'
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True, help="{label}_detail.jsonl yolu")
    p.add_argument("--label", required=True)
    p.add_argument("--out-dir", default="outputs/eval")
    p.add_argument("--source-field", default="referans")
    p.add_argument("--answer-field", default="cevap")
    p.add_argument("--mode", choices=["data", "model"], default="data",
                   help="data=tek-madde grounded veri (sıkı); model=avukat-ref eval (gevşek)")
    p.add_argument("--judge-model", default=os.environ.get("GND_JUDGE", "gpt-4o-mini"),
                   help="paper için üreticiden FARKLI/güçlü model (ör. gpt-4o)")
    p.add_argument("--hakem-saglayici", default=None,
                   help="OpenRouter'da sabitlenen sağlayıcı (yedeğe düşme kapalı). Verilmezse "
                        "LLM_PROVIDER_ORDER; DeepSeek ailesinde ZORUNLU (F0.6)")
    p.add_argument("--hakem-dusunme", choices=[d.value for d in Dusunme], default=None,
                   help="hakemin KENDİ düşünme modu; düşünme modu olan ailede ZORUNLU, varsayılansız")
    p.add_argument("--runs", type=int, default=1, help="N kez koş-havuzla (count gürültüsü ↓)")
    p.add_argument("--sonuc-deposu", choices=[m.value for m in sonuc_deposu.DepoModu],
                   default=sonuc_deposu.DepoModu.KAPALI.value,
                   help="kullan: aynı hakemin aynı girdiye önceki sonucu yeniden kullanılır (yalnız "
                        "--runs 1). Gürültü tabanı, kayma çıpası ve tekrarlarda KAPALI kalır")
    p.add_argument("--sonuc-deposu-kok", default="outputs/eval/_hakem_deposu")
    p.add_argument("--n", type=int, default=-1)
    olcum_aleti.argparse_ekle(p)
    return p.parse_args()


def extract_claims(client, hakem, cevap):
    r = client.chat.completions.create(
        model=hakem.model, temperature=0, **hakem.istek_ekleri(),
        messages=[{"role": "system", "content": EXTRACT_SYSTEM},
                  {"role": "user", "content": f"CEVAP:\n{cevap}"}])
    note_provider(r)
    d = loads_tolerant(r.choices[0].message.content)
    return [c for c in (d.get("claims") or []) if c and c.strip()], kullanim_oku(r)


def dogrulama_istemi(soru, source, gold, cevap, claims, altin_kirpma):
    """Doğrulama çağrısının kullanıcı mesajı. Sıra önbelleğe uygun (F0.6): kalemin her kolda
    ortak kısmı (soru · altın madde · altın atıf) başta, kola özgü cevap ve iddialar sonda."""
    claims_txt = "\n".join(f"- {c}" for c in claims)
    return (f"SORU:\n{soru}\n\nKAYNAK METİN (yer-gerçeği):\n{altin_kirpma.kirp(source)}\n\n"
            f"GOLD ATIF: {gold or '(bilinmiyor)'}\n\n"
            f"CEVAP (tam):\n{cevap}\n\nİDDİA LİSTESİ:\n{claims_txt}")


def verify_claims(client, hakem, soru, source, gold, cevap, claims, altin_kirpma):
    user = dogrulama_istemi(soru, source, gold, cevap, claims, altin_kirpma)
    r = client.chat.completions.create(
        model=hakem.model, temperature=0, **hakem.istek_ekleri(),
        messages=[{"role": "system", "content": VERIFY_SYSTEM},
                  {"role": "user", "content": user}])
    note_provider(r)
    d = loads_tolerant(r.choices[0].message.content)
    return d, kullanim_oku(r)


def score_record(client, hakem, soru, source, gold, cevap, mode, altin_kirpma):
    """Tek (kayıt × tek koşu): iki aşama → ham sayaçlar (havuzlama için) + çağrı başına
    (aşama, Kullanim) listesi."""
    claims, k1 = extract_claims(client, hakem, cevap)
    kullanimlar = [("cikarim", k1)]
    if not claims:
        return {"n_claims": 0, "sup": 0, "con": 0, "nis": 0, "nis_unsup": 0,
                "n_cit": 0, "cit_ok": 0, "cit_wrong": 0, "source_cited": False,
                "labels": [], "citations": []}, kullanimlar
    d, k2 = verify_claims(client, hakem, soru, source, gold, cevap, claims, altin_kirpma)
    kullanimlar.append(("dogrulama", k2))
    labels = d.get("labels") or []
    if not labels:
        # Why: iddia çıkarıldı ama doğrulama boş döndü — sıfır iddia değil, hakem arızası.
        raise ValueError(f"doğrulama {len(claims)} iddia için boş etiket döndü")
    sup = sum(1 for c in labels if c.get("label") == "SUPPORTED")
    con = sum(1 for c in labels if c.get("label") == "CONTRADICTED")
    nis_items = [c for c in labels if c.get("label") == "NOT_IN_SOURCE"]
    nis = len(nis_items)
    # model modunda "kaynak dışı ama makul" iddiayı temelsiz SAYMA (flu #4/#5 gevşetme)
    nis_unsup = sum(1 for c in nis_items if not (mode == "model" and c.get("plausible")))
    cits = d.get("citations") or []
    return {
        "n_claims": len(labels), "sup": sup, "con": con, "nis": nis, "nis_unsup": nis_unsup,
        "n_cit": len(cits), "cit_ok": sum(1 for c in cits if c.get("verdict") == "CORRECT"),
        "cit_wrong": sum(1 for c in cits if c.get("verdict") == "WRONG_REF"),
        "source_cited": bool(d.get("source_cited")),
        "labels": labels, "citations": cits,
    }, kullanimlar


def ratios(acc):
    n = acc["n_claims"]
    nc = acc["n_cit"]
    return {
        "n_claims": n, "n_supported": acc["sup"], "n_contradicted": acc["con"],
        "n_not_in_source": acc["nis"], "n_unsupported": acc["con"] + acc["nis_unsup"],
        "faithfulness": round(acc["sup"] / n, 4) if n else None,
        "hallucination_rate": round((acc["con"] + acc["nis"]) / n, 4) if n else None,
        "unsupported_rate": round((acc["con"] + acc["nis_unsup"]) / n, 4) if n else None,
        "n_citations": nc, "n_citations_ok": acc["cit_ok"], "n_citations_wrong": acc["cit_wrong"],
        "cit_precision": round(acc["cit_ok"] / nc, 4) if nc else None,
        "wrong_ref_rate": round(acc["cit_wrong"] / nc, 4) if nc else None,
        "cit_recall": 1 if acc["source_cited"] else 0,
    }


def _bos_satir(rid, soru, gold, runs, durum, hata=""):
    rec = {"id": rid, "soru": soru, "gold": gold, "runs": runs, "durum": durum,
           **ratios({k: 0 for k in ("n_claims", "sup", "con", "nis", "nis_unsup", "n_cit",
                                    "cit_ok", "cit_wrong")} | {"source_cited": False}),
           "labels": [], "citations": [], "source_cited": False}
    if hata:
        rec["hata"] = hata[:300]
    return rec


def main():
    a = parse_args()
    alet = olcum_aleti.argumanlardan(a)
    rows = tamamlanmis_jsonl(a.details)
    if a.n and a.n >= 0:
        rows = rows[:a.n]

    client, gateway = make_client()
    a.judge_model = resolve(a.judge_model, gateway)
    try:
        hakem = HakemKimligi(a.judge_model, a.hakem_saglayici,
                             Dusunme(a.hakem_dusunme) if a.hakem_dusunme else None)
    except ValueError as e:
        raise SystemExit(f"[gnd] 🚫 {e}")
    price(a.judge_model)   # Why: fiyatı kayıtsız hakem ilk çağrıdan (paradan) ÖNCE reddedilir
    depo = None
    if sonuc_deposu.DepoModu(a.sonuc_deposu) is sonuc_deposu.DepoModu.KULLAN:
        if a.runs != 1:
            raise SystemExit("[gnd] 🚫 --sonuc-deposu kullan yalnız --runs 1 ile; tekrarlar "
                             "aynı girdiyi yeniden puanlatmak içindir")
        depo = sonuc_deposu.SonucDeposu(a.sonuc_deposu_kok, hakem.kunye())
    budget = float(os.environ.get("OPENAI_BUDGET_USD", "5") or "5")

    os.makedirs(a.out_dir, exist_ok=True)
    op = os.path.join(a.out_dir, f"gnd_{a.label}.jsonl")
    # 🚨 YARIŞ KAPISI: aynı label'a yazan ikinci bir süreç varsa BURADA dur — para harcamadan.
    runlock.acquire(op, tag=f"gnd {a.label}")
    spent, out = 0.0, []
    fatura = []   # (aşama, Kullanim): koşunun bütün başarılı hakem çağrıları
    print(f"[gnd] {a.label}: {len(rows)} cevap | mod={a.mode} | hakem={a.judge_model} "
          f"| runs={a.runs} | kaynak={a.source_field}")
    with part_ile_yaz(op) as f:
        for i, r in enumerate(rows):
            soru = r.get("soru", "")
            source = (r.get(a.source_field) or "").strip()
            cevap = (r.get(a.answer_field) or "").strip()
            rid = r.get("id", i)
            ka, mn, kn = r.get("kanun_adi") or "", r.get("madde_no"), r.get("kanun_no")
            gold = ((f"{ka}" + (f" (kanun no {kn})" if kn else "")
                     + (f", madde {mn}" if mn not in (None, "") else "")).strip()
                    if ka else "")
            if not source or not cevap:
                print(f"  id={rid} kaynak/cevap boş → bos_girdi")
                rec = _bos_satir(rid, soru, gold, a.runs, "bos_girdi")
                out.append(rec)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue
            # N koşuyu HAVUZLA (claim havuzu birleşir → oran stabilize; flu #1)
            acc = {k: 0 for k in ("n_claims", "sup", "con", "nis", "nis_unsup", "n_cit",
                                  "cit_ok", "cit_wrong")}
            acc["source_cited"] = False
            last, hata, kalem_kullanim = None, "", []
            k_depo = (sonuc_deposu.anahtar(hakem.kunye(), (EXTRACT_SYSTEM, VERIFY_SYSTEM), a.mode,
                                           soru, alet.altin_kirpma.kirp(source), gold, cevap)
                      if depo else None)
            depodan = False
            for _ in range(max(1, a.runs)):
                if spent >= budget:
                    # Why: kalan kalemler puanlanmadan dosya tamamlanmış sayılamaz → `.part` kalır.
                    raise SystemExit(f"[gnd] 🚫 BÜTÇE doldu (${spent:.4f} ≥ ${budget}) — "
                                     f"{op}.part tamamlanmadı, puanlanmaz; bütçeyi artırıp yeniden koş.")
                s = depo.bul(k_depo) if depo else None
                depodan = s is not None
                if not depodan:
                    try:
                        s, kl = score_record(client, hakem, soru, source, gold, cevap, a.mode,
                                             alet.altin_kirpma)
                    except _HAKEM_HATALARI as e:
                        # Why: koşulardan biri bile düşerse kalem eksik sayıyla havuzlanmaz.
                        hata = f"{type(e).__name__}: {e}"
                        print(f"  id={rid} hakem hata: {hata}")
                        break
                    spent += sum(ku.liste_maliyeti(hakem.model) for _, ku in kl)
                    kalem_kullanim += kl
                    if depo:
                        depo.ekle(k_depo, s, a.label)
                for k in ("n_claims", "sup", "con", "nis", "nis_unsup", "n_cit",
                          "cit_ok", "cit_wrong"):
                    acc[k] += s[k]
                acc["source_cited"] = acc["source_cited"] or s["source_cited"]
                last = s
            fatura += kalem_kullanim
            if hata:
                rec = _bos_satir(rid, soru, gold, a.runs, "hakem_hata", hata)
                out.append(rec)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue
            m = ratios(acc)
            rec = {"id": rid, "soru": soru, "gold": gold, "runs": a.runs,
                   "durum": "puanli" if m["n_claims"] else "sifir_iddia", **m,
                   "labels": last["labels"], "citations": last["citations"],
                   "source_cited": acc["source_cited"],
                   "kullanim": [{"asama": asama, **asdict(ku)} for asama, ku in kalem_kullanim],
                   **({"depodan": depodan} if depo else {})}
            out.append(rec)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"  id={rid:>2} faith={m['faithfulness']} hall={m['hallucination_rate']} "
                  f"unsup={m['unsupported_rate']} claims={m['n_claims']} "
                  f"citP={m['cit_precision']} wrongRef={m['wrong_ref_rate']} citR={m['cit_recall']}")

    sayac = {d: sum(1 for r in out if r["durum"] == d)
             for d in ("puanli", "sifir_iddia", "hakem_hata", "bos_girdi")}
    # Why: oranlar eskiden olduğu gibi hakemin gerçekten puanladığı kalemler üzerinden (puanlı +
    # sıfır iddialı); hakem hatası ve boş girdi yalnız sayaçta görünür.
    out = [r for r in out if r["durum"] in ("puanli", "sifir_iddia")]

    def s(k):
        return sum(r[k] for r in out if r.get(k) is not None)
    tot_claims, tot_cit = s("n_claims"), s("n_citations")
    summary = {
        "label": a.label, "n": len(out), "mode": a.mode, "judge_model": a.judge_model,
        "n_girdi": len(rows), **{f"n_{d}": v for d, v in sayac.items()},
        "olcum_aleti": alet.kunye(),
        "hakem": hakem.kunye(),
        # ⚠️ len(judge_providers) > 1 → yönlendirme pinlenmemiş, sayı tek bir servis
        # yığınına ait değil (ADR-0029). Koşuyu tekrarla, LLM_PROVIDER_ORDER ile pinle.
        "judge_gateway": gateway, "judge_providers": seen_providers(),
        "runs": a.runs, "total_claims": tot_claims,
        # mikro (claim-havuzu) — headline
        "faithfulness_micro": round(s("n_supported") / tot_claims, 4) if tot_claims else None,
        "hallucination_micro": round((s("n_contradicted") + (tot_claims - s("n_supported")
                                      - s("n_contradicted"))) / tot_claims, 4) if tot_claims else None,
        "unsupported_micro": round(s("n_unsupported") / tot_claims, 4) if tot_claims else None,
        "cit_precision_micro": round(s("n_citations_ok") / tot_cit, 4) if tot_cit else None,
        "wrong_ref_rate_micro": round(s("n_citations_wrong") / tot_cit, 4) if tot_cit else None,
        "cit_recall_macro": round(statistics.mean([r["cit_recall"] for r in out]), 4) if out else None,
        # makro (örnek-başı) — dağılım
        "faithfulness_macro": round(statistics.mean(
            [r["faithfulness"] for r in out if r["faithfulness"] is not None]), 4) if out else None,
        "judge_cost_usd": round(spent, 4),
        # #74 R1: yanıttan okunan gerçek maliyet ve önbellek; judge_cost_usd liste fiyatıyla tahmin kalır
        "fatura": {"toplam": fatura_ozeti(hakem.model, [ku for _, ku in fatura]),
                   **{asama: fatura_ozeti(hakem.model, [ku for b, ku in fatura if b == asama])
                      for asama in ("cikarim", "dogrulama")}},
        "sonuc_deposu": {"mod": a.sonuc_deposu, "yol": depo.yol if depo else None,
                         "n_depodan": sum(1 for r in out if r.get("depodan"))},
        "note_validity": "LLM-judge (insan-κ kalibresiz, Aşama C) → mutlak değil, model-vs-model sıralama.",
    }
    sp = os.path.join(a.out_dir, f"gnd_{a.label}_summary.json")
    with part_ile_yaz(sp) as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n[gnd] ÖZET {a.label}: {json.dumps(summary, ensure_ascii=False)}")
    print(f"[gnd] detay → {op}\n[gnd] özet → {sp}")
    return summary


if __name__ == "__main__":
    main()
