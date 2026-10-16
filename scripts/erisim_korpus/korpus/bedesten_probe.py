#!/usr/bin/env python
"""bedesten.adalet.gov.tr/mevzuat JSON API kanıt testi (reverse-engineered).

mevzuat-mcp'den çıkarılan contract:
- POST {BASE}/searchDocuments , /getDocumentContent , /mevzuatMaddeTree
- Sarmalama: {"data": <inner>, "applicationName": "UyapMevzuat"} (+ "paging": true aramada)
- İçerik base64 (HTML/PDF) -> decode + tag temizle
Auth/Playwright YOK. Sadece stdlib (urllib).
"""
import base64
import json
import re
import urllib.request

BASE = "https://bedesten.adalet.gov.tr/mevzuat"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://mevzuat.adalet.gov.tr",
    "Referer": "https://mevzuat.adalet.gov.tr/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36",
    "Accept": "application/json",
}


def post(path, inner, paging=False):
    payload = {"data": inner, "applicationName": "UyapMevzuat"}
    if paging:
        payload["paging"] = True
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"),
                                 headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip_html(t):
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    import html as _h
    return "\n".join(l.strip() for l in _h.unescape(t).split("\n") if l.strip())


print("=== 1) searchDocuments: KANUN, mevzuatNo=4857 (İş Kanunu) ===")
body = post("/searchDocuments", {
    "pageSize": 5, "pageNumber": 1,
    "sortFields": ["RESMI_GAZETE_TARIHI"], "sortDirection": "desc",
    "mevzuatNo": "4857", "mevzuatTurList": ["KANUN"],
}, paging=True)
meta = body.get("metadata", {})
print("FMTY:", meta.get("FMTY"), "| total:", (body.get("data") or {}).get("total"))
docs = (body.get("data") or {}).get("mevzuatList", [])
# Why: alan adı `mevzuatId` (BEDESTEN_API.md §48). Eski kod `documentId`/`id`
# arıyordu; arama SUCCESS dönerken id None kalıyor ve prob, API çalışırken
# "bozuk" raporluyordu — sessiz yanlışlık, 2026-08-04'te yakalandı.
for d in docs[:3]:
    print("  id:", d.get("mevzuatId"), "| ad:", str(d.get("mevzuatAdi"))[:50], "| tur:", d.get("mevzuatTur"))

if docs:
    did = docs[0].get("mevzuatId")
    print(f"\n=== 2) getDocumentContent (id={did}) ===")
    c = post("/getDocumentContent", {"documentType": "MEVZUAT", "id": did})
    cmeta = c.get("metadata", {})
    data = c.get("data") or {}
    print("FMTY:", cmeta.get("FMTY"), "| mime:", data.get("mimeType"))
    decoded = base64.b64decode(data.get("content", "")).decode("utf-8", "replace")
    txt = strip_html(decoded) if "html" in (data.get("mimeType") or "") else "(PDF/binary)"
    print("içerik (ilk 400 karakter):\n", txt[:400])

    print(f"\n=== 3) mevzuatMaddeTree (mevzuatId={did}) ===")
    t = post("/mevzuatMaddeTree", {"mevzuatId": did})
    print("FMTY:", t.get("metadata", {}).get("FMTY"))
    kok = (t.get("data") or {}).get("children") or []
    yigin, maddeler = list(kok), []
    while yigin:
        n = yigin.pop()
        yigin.extend(n.get("children") or [])
        if n.get("maddeNo") is not None:
            maddeler.append(n)
    print(f"madde sayısı: {len(maddeler)}")
    for m in maddeler[:3]:
        print("  maddeId:", m.get("maddeId"), "| no:", m.get("maddeNo"),
              "| başlık:", m.get("title"), "| güncelleme:", m.get("guncellemeTarihi"))

    if maddeler:
        mid = maddeler[0]["maddeId"]
        print(f"\n=== 4) getDocumentContent MADDE (id={mid}) — retriever'ın kullanacağı yol ===")
        cm = post("/getDocumentContent", {"documentType": "MADDE", "id": mid})
        dm = cm.get("data") or {}
        print("FMTY:", cm.get("metadata", {}).get("FMTY"), "| mime:", dm.get("mimeType"))
        mtxt = base64.b64decode(dm.get("content", "")).decode("utf-8", "replace")
        print("madde metni (ilk 300):\n", strip_html(mtxt)[:300])
