#!/usr/bin/env python
"""Tek model erişim kapısı — hakem paneli + rakip ölçümü aynı yerden (ADR-0029).

NEDEN TEK KAPI
  · Hakem paneli üç AİLEDEN oluşacak (ADR-0027, dört katmanlı savunma). Bugünkü kod tek
    aile (OpenAI) ile çakılı — `bench_scorecard.py` bunun self-preference'ı gidermediğini
    zaten not etmiş.
  · Dış parite matrisi (Sprint 5) rakipleri API'den koşacak.
  · Maliyet muhasebesi tez iddiasının yarısı (ADR-0017: maliyet-normalize parite) →
    fiyat tablosu TEK ve denetlenebilir olmalı, script başına kopya değil.

KULLANIM
    from llm_client import make_client, resolve, price, family, request_kwargs, loads_tolerant
    client, gw = make_client()
    m = resolve("openai/gpt-4o-mini", gw)
    r = client.chat.completions.create(model=m, messages=[...], **request_kwargs(m))
    d = loads_tolerant(r.choices[0].message.content)

ORTAM
    OPENROUTER_API_KEY  → varsa kapı OpenRouter (çok-aile)
    OPENAI_API_KEY      → yoksa/kapı=openai ise doğrudan OpenAI (geriye dönük uyumlu)
    LLM_GATEWAY         → "openrouter" | "openai" (otomatik seçimi ezmek için)
    LLM_PROVIDER_ORDER  → virgüllü upstream sağlayıcı sırası; pinlenir, fallback KAPALI

⚠️ İKİ TUZAK — ikisi de sessizdir, ikisi de sayıyı BİZİM LEHİMİZE kaydırır:
  (1) SAĞLAYICI YÖNLENDİRME. OpenRouter aynı model kimliğini farklı upstream sağlayıcıya
      yollayabilir (farklı kuantizasyon/örnekleme). Hata vermez, sayı değişir. → sağlayıcıyı
      pinle + HER koşuda gerçekten hizmet vereni kaydet (`seen_providers()`); küme birden
      fazla eleman içeriyorsa yönlendirme pinlenmemiştir.
  (2) FİYAT. Kapının kendi marjı var. Parite matematiği BİRİNCİL-KAYNAK liste fiyatıyla
      yapılır (aşağıdaki tablo); kapıya ödenen tutar ayrı, operasyonel bir sayıdır.
      Ödenen tutarı parite fiyatı sanmak rakibi pahalı gösterir — kalibre edilmemiş red
      regex'iyle aynı hata sınıfı.
"""
import json
import os
import re
from dataclasses import dataclass
from enum import Enum

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Kısa ad → kanonik (aile/model) kimlik. Eski komut satırları ("gpt-4o-mini") bozulmasın diye.
ALIAS = {
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4o": "openai/gpt-4o",
    # F0.14 (2026-10-15, kronoloji #81): OpenRouter'ın `canonical_slug`'ı — sürümü tarihle sabitler.
    # F0.6'da doğrulandı: 10 koşu, sağlayıcı DeepInfra, hakem hatası 0 (kronoloji #85).
    "deepseek-v4.1-flash": "deepseek/deepseek-v4.1-flash-20260910",
}

# ⚠️ BİRİNCİL-KAYNAK liste fiyatı (USD / token), (girdi, çıktı). Kapı marjı DAHİL DEĞİL.
# Fiyat değişirse satırı silme — tarih düşerek yenisini ekle (sayı kaynaklı olmalı).
PRICE = {  # 2026-07-24 itibarıyla
    "openai/gpt-4o-mini": (0.15 / 1e6, 0.60 / 1e6),
    "openai/gpt-4o": (2.50 / 1e6, 10.0 / 1e6),
    # ── Rakip çıkarım fiyatı (ADR-0017 maliyet ekseni · Görev 2, Adım 2.1b) ────────
    # Birincil kaynak: https://ai.google.dev/gemini-api/docs/pricing — Google'ın kendi
    # resmî API fiyat sayfası. Okundu 2026-08-06, "Paid tier / Standard" satırları.
    # ⚠️ Alınan değer TEXT modalitesi; ses girdisi (3.1 FL'de $0,50/M) ayrı ve
    # kullanılmıyor — bu hattın girdisi yalnız metin.
    # ⚠️ Sayfa açıkça diyor: DÜŞÜNCE (thinking/reasoning) token'ları ÇIKTI tarifesinden
    # faturalanır. `--reasoning-budget 1024` bu yüzden doğrudan maliyet kalemidir.
    "google/gemini-3.1-flash-lite": (0.25 / 1e6, 1.50 / 1e6),
    "google/gemini-3.5-flash-lite": (0.30 / 1e6, 2.50 / 1e6),
    # ── HP hakem paneli · ikinci aile (Anthropic) ─────────────────────────────────
    # Birincil kaynak: OpenRouter `GET /api/v1/models` — bu hattın hakem çağrıları
    # OpenRouter üzerinden faturalanıyor, dolayısıyla liste fiyatı da oradan alınır.
    # Ölçüldü 2026-09-07 (plan Görev 1 Adım 1): girdi $2,00/M · çıktı $10,00/M.
    "anthropic/claude-sonnet-5": (2.00 / 1e6, 10.00 / 1e6),
    # ── F0.6 hakemi · DeepSeek V4.1 Flash, sabit sağlayıcı DeepInfra (fp8) ────────────────
    # Birincil kaynak: OpenRouter `GET /api/v1/models/deepseek/deepseek-v4.1-flash/endpoints`,
    # okundu 2026-10-15 14:39 UTC (kronoloji #81). Fiyat MODELİN değil SAĞLAYICININ: aynı model
    # 33 sağlayıcıda $0,02-0,60 girdi arası satılıyor; sağlayıcı sabit olduğu için fiyat da onun.
    # Önbellekli girdi $0,0042/M bu tabloda yok (tahmin önbelleksiz ⇒ üstten).
    # ⚠️ Uç noktada `discount: 0.3` işareti vardı — fiyat ileride değişebilir; koşu günü yeniden okunur.
    "deepseek/deepseek-v4.1-flash-20260910": (0.14 / 1e6, 0.42 / 1e6),
    # ⛔ `anthropic/claude-sonnet-5:batch` (liste fiyatı tam yarısı) buradan KULLANILAMAZ —
    # ölçüldü 2026-09-07: senkron chat-completions çağrısı 404 döndürüyor,
    # "This model is only available through the Batch API. Use /api/beta/batches".
    # Bu istemci senkron; batch yolu ayrı bir taşıyıcı demek ⇒ kapsam dışı bırakıldı.
}

# Yalnız bu aileler `response_format={"type":"json_object"}` ile güvenilir çalışıyor kabul
# edilir. Diğerlerinde alan GÖNDERİLMEZ ve çıktı `loads_tolerant` ile ayrıştırılır.
# ⚠️ CP0.5'te her panel ailesi için GERÇEK çağrıyla doğrula — varsayma.
JSON_MODE_FAMILIES = {"openai"}

_SEEN_PROVIDERS = set()


def family(model):
    """Aile kimliği — aile-dışlama kuralı bunun üzerinden işler."""
    m = ALIAS.get(model, model)
    return m.split("/", 1)[0] if "/" in m else "openai"


def resolve(model, gateway):
    """Kanonik kimliği kapının beklediği biçime çevir."""
    m = ALIAS.get(model, model)
    if gateway == "openrouter":
        return m
    fam = family(m)
    if fam != "openai":
        raise SystemExit(
            f"[llm] '{model}' ({fam}) doğrudan OpenAI kapısından koşulamaz. "
            f"OPENROUTER_API_KEY tanımla ya da OpenAI ailesinden bir model seç.")
    return m.split("/", 1)[-1]


def price(model):
    """USD/token (girdi, çıktı). Bilinmeyen model → SESSİZ VARSAYILAN YOK, hata."""
    m = ALIAS.get(model, model)
    if m not in PRICE:
        raise SystemExit(
            f"[llm] '{model}' için fiyat kaydı yok. llm_client.PRICE'a birincil-kaynak "
            f"liste fiyatını tarihiyle ekle — yanlış fiyatla maliyet raporlanmasın.")
    return PRICE[m]


# ⚠️ Timeout/retry dayanıklılığı (2026-07-25): tek bir API timeout'u koca bir CANON koşusunu
# (480 çağrı) kırıyordu — "m5 got cut by timeout" (Gemini skorlaması). OpenAI SDK'sı
# APITimeoutError / APIConnectionError / 408 / 409 / 429 / 5xx üzerinde ÜSTEL GERİ-ÇEKİLMEYLE
# otomatik retry yapar; varsayılan max_retries=2 yetmiyordu. Bunu yükseltmek "wait + oto-retry"yi
# bedavaya getirir. timeout: tek istek bu kadar saniyede asılı kalırsa retry'a düşer (600s asılı
# kalıp koşuyu boğmasın). Ortamla ezilebilir: LLM_MAX_RETRIES / LLM_TIMEOUT_S.
_MAX_RETRIES = int(os.environ.get("LLM_MAX_RETRIES", "8"))
_TIMEOUT_S = float(os.environ.get("LLM_TIMEOUT_S", "120"))


def gateway_of():
    """Hangi kapı kullanılacak — İSTEMCİ KURMADAN. `make_client()` de bunu çağırır.

    Why ayrı: hiç çağrı yapmayacak bir koşu (ör. payda tanımdan geliyor + verdict önceki
    skorlamadan okunuyor) kapının kimliğini istememeli, ama koşu kaydına yine de hangi
    kapının geçerli olduğunu yazmalı. İki yerde ayrı ayrı türetilirse sessizce ayrışır.
    """
    want = (os.environ.get("LLM_GATEWAY") or "").strip().lower()
    return want or ("openrouter" if os.environ.get("OPENROUTER_API_KEY", "").strip()
                    else "openai")


def make_client():
    """(client, gateway) döndürür. OpenRouter varsa onu, yoksa doğrudan OpenAI'ı kullanır.
    Client, timeout'larda otomatik retry+backoff yapacak şekilde kurulur (üstteki not)."""
    from openai import OpenAI
    or_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    oa_key = os.environ.get("OPENAI_API_KEY", "").strip()

    gateway = gateway_of()
    if gateway == "openrouter":
        if not or_key:
            raise SystemExit("[llm] OPENROUTER_API_KEY yok (.env yükle)")
        return OpenAI(api_key=or_key, base_url=OPENROUTER_BASE,
                      max_retries=_MAX_RETRIES, timeout=_TIMEOUT_S), "openrouter"
    if not oa_key:
        raise SystemExit("[llm] OPENAI_API_KEY yok (.env yükle)")
    return OpenAI(api_key=oa_key, max_retries=_MAX_RETRIES, timeout=_TIMEOUT_S), "openai"


def request_kwargs(model, seed=3407, saglayici=None):
    """Modele göre JSON modu + sağlayıcı pinleme. `create(**request_kwargs(m))` diye geçir.
    `saglayici` verilirse o sabitlenir; verilmezse LLM_PROVIDER_ORDER (eski komutlar)."""
    kw = {}
    if family(model) in JSON_MODE_FAMILIES:
        kw["response_format"] = {"type": "json_object"}
    if seed is not None:
        kw["seed"] = seed
    order = [p.strip() for p in (saglayici or os.environ.get("LLM_PROVIDER_ORDER") or "").split(",")
             if p.strip()]
    if order:
        kw["extra_body"] = {"provider": {"order": order, "allow_fallbacks": False}}
    return kw


class Dusunme(Enum):
    """Hakemin KENDİ düşünme modu (öznenin değil). Bağlayıcı mod F1.4'te seçilir (F0.6)."""
    ACIK = "acik"
    KAPALI = "kapali"


# Hakemin kendi düşünme modu olan aileler: modun AÇIKÇA verilmesi zorunlu, varsayılan yok.
# Sabit sağlayıcısı zorunlu aileler: yedek sağlayıcıya düşme kapalı, ortam değişkenine düşülmez.
# F0.14 (2026-10-15, #81): sabit sağlayıcı `deepinfra/fp8`. DeepSeek'in kendi belgesine göre düşünme
# modunda `temperature` YOK SAYILIR (hata vermez) — hakemin düşünmesi açıkken sıcaklık hiçbir şeyi sabitlemez.
DUSUNME_AILELERI = {"deepseek"}
SAGLAYICI_ZORUNLU_AILELER = {"deepseek"}


@dataclass(frozen=True)
class HakemKimligi:
    """Hakem = model + sağlayıcı + hakemin düşünme modu. RQ2'nin hakem anahtarı ve F0.6'nın
    DeepSeek geçişi bu nesnedir (ADR-0099 m.1). Geçersiz bileşim nesne kurulurken reddedilir —
    yani ilk hakem çağrısından, dolayısıyla paradan önce."""
    model: str
    saglayici: str | None      # OpenRouter upstream; None → LLM_PROVIDER_ORDER (eski komutlar)
    dusunme: Dusunme | None    # None yalnız düşünme modu olmayan ailede

    def __post_init__(self):
        aile = family(self.model)
        if aile in DUSUNME_AILELERI and self.dusunme is None:
            raise ValueError(f"{self.model}: hakemin düşünme modu açıkça verilmeli "
                             f"(--hakem-dusunme acik|kapali; varsayılan yok, F0.6)")
        if aile not in DUSUNME_AILELERI and self.dusunme is not None:
            raise ValueError(f"{self.model}: bu ailenin düşünme modu yok; --hakem-dusunme verilmez")
        if aile in SAGLAYICI_ZORUNLU_AILELER and not self.saglayici:
            raise ValueError(f"{self.model}: sağlayıcı açıkça sabitlenmeli (--hakem-saglayici); "
                             f"yedek sağlayıcıya düşme kapalı (tuzak 2.7)")

    def istek_ekleri(self, seed=3407) -> dict:
        kw = request_kwargs(self.model, seed=seed, saglayici=self.saglayici)
        if self.dusunme is not None:
            kw.setdefault("extra_body", {})["reasoning"] = {"enabled": self.dusunme is Dusunme.ACIK}
        return kw

    def kunye(self) -> dict:
        return {"model": self.model, "saglayici": self.saglayici,
                "dusunme": self.dusunme.value if self.dusunme else None}


def note_provider(resp):
    """Yanıtı gerçekten kim servis etti — koşu kaydına yazılmak üzere biriktir."""
    p = getattr(resp, "provider", None)
    if p is None:
        try:
            p = resp.model_dump().get("provider")
        except Exception:
            p = None
    if p:
        _SEEN_PROVIDERS.add(str(p))
    return p


def seen_providers():
    """Koşu boyunca hizmet veren sağlayıcılar. len>1 → yönlendirme PİNLENMEMİŞ, sayı şüpheli."""
    return sorted(_SEEN_PROVIDERS)


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def loads_tolerant(txt):
    """JSON modu olmayan ailelerin çıktısını ayrıştır (kod çiti / çevresel metin toleranslı)."""
    txt = (txt or "").strip()
    try:
        return json.loads(txt)
    except Exception:
        pass
    m = _FENCE.search(txt)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            pass
    i, j = txt.find("{"), txt.rfind("}")
    if i >= 0 and j > i:
        return json.loads(txt[i:j + 1])
    raise ValueError(f"JSON ayrıştırılamadı: {txt[:200]!r}")
