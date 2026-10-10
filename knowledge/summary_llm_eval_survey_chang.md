# A Survey on Evaluation of Large Language Models (Chang ve ark., arXiv 2307.03109) — proje notu

> **LİTERATÜR ÖZETİ.** Kaynak: TeX kaynağı (`https://arxiv.org/src/2307.03109`, v-son; ACM TIST biçimi). Başlık kaynaktan doğrulandı: "A Survey on Evaluation of Large Language Models". Makale Temmuz 2023 itibarıyla literatürü tarar; sonrası (RAG-özgü, hakem-LLM yanlılığı, sızıntı ölçümü) kapsam dışıdır. Bu notta makalenin verdiği ile bizim çıkarımımız ayrıdır; çıkarımlar "Çıkarım" diye işaretlidir.
> Aynı alandaki mevcut özet [`summary_eval_benchmark_literature.md`](summary_eval_benchmark_literature.md) RAG sadakati, çekinme ve hukuk-özgü ölçüt tasarımını kapsar; burada tekrar edilmez.

## TL;DR

Makale, LLM değerlendirmesini üç eksende tasnif eden geniş bir taramadır: **ne** değerlendirilir (görev/yetenek sınıfları), **nerede** (46 benchmark; genel, alt-görev, çok kipli), **nasıl** (otomatik ↔ insan). Yeni yöntem ya da deney yoktur. Hukuk payı çok küçüktür (Sec. 3.3: iki çalışma + tabloda CUAD). Bizim için değeri, (a) kendi 6 modlu CANON'umuzu yetenek taksonomisinde konumlamak, (b) insan değerlendirmesi için ölçüt/evaluatör uzmanlığı/sayı çerçevesi, (c) sonuç bölümündeki "statik ve açık benchmark sızıntıya açıktır; dinamik/evrilen değerlendirme gerekir" tezidir. Makale tek bir "en iyi protokol" olmadığını açıkça söyler (Sec. 6).

## Ana katkılar

1. **Üç eksenli taksonomi** (Sec. 1): what / where / how.
2. **Ne:** (Sec. 3) NLP görevleri (anlama, akıl yürütme, üretim, çok dillilik, olgusallık) · sağlamlık/etik/yanlılık/güvenilirlik · sosyal bilim (hukuk burada) · doğa bilimi ve mühendislik · tıp · ajan · eğitim, arama/öneri, kişilik testi.
3. **Nerede:** (Sec. 4) 46 benchmark, üç sınıf: genel (MMLU, HELM, BIG-bench, MT-Bench, Chatbot Arena, AlpacaEval, AGIEval, PromptBench, GLUE-X, DynaBench...), alt-görev (MultiMedQA, FreshQA, CUAD, C-Eval, CMMLU, TruthfulQA benzeri, API-Bank, ToolBench...), çok kipli (MME, MMBench, SEED-Bench...).
4. **Nasıl:** (Sec. 5) otomatik değerlendirme (doğruluk: EM/F1/ROUGE; kalibrasyon: ECE, seçici doğruluk-kapsama AUC; adalet: DPD, EOD; sağlamlık: ASR, PDR) ve insan değerlendirmesi (6 ölçüt: doğruluk, ilgi, akıcılık, şeffaflık, güvenlik, insan uyumu; evaluatör sayısı ve uzmanlık düzeyi).
5. **Başarı/başarısızlık özeti** (Sec. 6) ve **yedi açık sorun** (Sec. 7).

## Akılda tutulacak teknik ayrıntılar

- **Otomatik ↔ insan ayrımı ölçütü:** ölçüt otomatik hesaplanabiliyorsa otomatik, değilse insan (Sec. 5). Ayrım, "LLM-hakem" için ayrı bir sınıf açmaz; LLM-EVAL ve PandaLM "gelişmiş otomatik teknik" olarak anılır (Sec. 5.1). Hakem-LLM yanlılığı/uyumu (κ, kendini tercih) makalede ele alınmaz.
- **İnsan değerlendirmesi** (Sec. 5.2): yüksek varyans ve kararsızlık riski (kültürel/bireysel farklar) not edilir; evaluatör sayısı "yeterli temsil + istatistiksel anlamlılık", uzmanlık ise "alan bilgisi, görev aşinalığı, metodolojik eğitim" olarak sayılır. Anlaşma katsayısı (κ, Krippendorff) önerilmez; sayısal rehber yoktur.
- **Kalibrasyon metrikleri:** ECE (güven aralıklarına bölüp ortalama doğruluk), **seçici doğruluk-kapsama AUC** (Sec. 5.1). İkincisi bizim "kapsama × A1" kütlesine kavramsal olarak en yakın hazır ölçüdür.
- **Olgusallık** (Sec. 3.1.5): FActScore (metni atomik olgulara ayırıp F1), SelfCheckGPT, NLI/soru-üretimi tabanlı olgusal tutarlılık (Honovich vd.: ikili etiket, yalnız girdiyle çelişki), TruthfulQA (modeli yanıltmak için tasarlı; ölçek tek başına doğruluğu artırmaz).
- **Sağlamlık:** PDR = 1 - (saldırılı istemde metrik / temiz istemde metrik); ASR. PromptBench karakter/kelime/cümle/anlam düzeyinde saldırır (Sec. 3.2.1).
- **Güvenilirlik:** "tutarlılık" bulgusu (Xie vd.): sorgulama, olumsuzlama, yanıltıcı ipucu karşısında doğru ilk karar bozulur (Sec. 3.2.3).
- **Hukuk (Sec. 3.3):** Deroy vd.: dava özetlemede sıfır-atış performansı vasat; yarım cümle, anlamsız birleştirme, tutarsız/halüsine bilgi. Nay vd.: istem iyileştirme + doğru hukuk metni verilince daha iyi, ama uzman vergi avukatı düzeyinde değil. CUAD: uzman-etiketli sözleşme inceleme (Tablo benchmarks).
- **Sonuç (Sec. 6):** başarısızlık listesinde "gerçek zamanlı/dinamik bilgiyi içermede sınırlı", "istem duyarlılığı", "düşük kaynaklı diller/Latin dışı yazılar", "halüsinasyon" yer alır; tek model her görevde en iyi değildir.
- **Yeni protokol eğilimleri** (Sec. 6.2): nesnel hesaptan insan-döngüde teste; statikten kitle-kaynaklı/dinamik test kümesine (DynaBench, DynamicTempLAMA); birleşikten zorlayıcı kuruluma (CheckList, AdaFilter, PromptBench). AdaFilter için "düşmanca kurulum adil olmayabilir" uyarısı.
- **Açık sorunlar** (Sec. 7): AGI benchmark tasarımı · tam davranışsal değerlendirme · sağlamlık · **dinamik ve evrilen değerlendirme** (statik açık kümeler ezberlenir, eğitim verisi kirlenir) · **ilkeli ve güvenilir değerlendirme** (ölçüm kuramı; dinamik testin gerçekten OOD ürettiğini nasıl garanti ederiz) · tüm görevleri destekleyen birleşik değerlendirme · değerlendirmeden sonra iyileştirme (analiz + öneri sunan sistemler, ör. PromptBench dikkat görselleştirmesi).

## HakHukuk için somut uygulamalar

Çoğu öneri makalenin söylediğinin **bizim durumumuza çevrilmesidir (Çıkarım)**; makalede karşılığı olan dayanak parantezde verilir.

### Değerlendirme protokolü

1. **Sızıntı/kirlenme bölümü: açık, eski ve yeni kümeler arasında ayrı rapor** (Sec. 7.4; Sec. 6.2). Yol haritası §2.5.1'de eski TEST + yeni ~200 + mühürlü ~100 zaten ayrı raporlanıyor; makalenin dinamik/evrilen değerlendirme tezi bunu savunmak için atıflanabilir. Çıkarım: mühürlü parçanın "bir kez açılır" kuralı, makalenin statik açık kümeler sızıntıya yatkındır uyarısının bizdeki karşılığıdır. Aşama: Checkpoint 2 (mühürlü parça açılışı) ve Makale 2 Sınırlar.
2. **Seçici doğruluk-kapsama AUC'sini kütlenin tamamlayıcı eğrisi olarak raporlamak** (Sec. 5.1, kalibrasyon). Kütle = kapsama × A1 tek noktadır; modelin güveni/çekinme eşiği değiştikçe eğri çıkarmak (risk-kapsama) over-refusal baskısını göstermek için ek bilgi verir. Çıkarım: bizim çekinmemiz ikili regex olduğundan eğri ancak güven sinyali (ör. mantıksal olasılık) eklenirse çıkar; kapsam dışı olabilir, YAGNI ile değerlendirilmeli. Aşama: yalnız Makale 2 isteğe bağlı ek.
3. **İstem sağlamlığı için PDR benzeri tek sayı** (Sec. 3.2.1, Sec. 5.1). Düşünce koruma (§2.5.4) ve sunucu bayrakları duyarlılığı (#66) zaten kırılganlığı gösteriyor. Soru ifadesi/şablon varyantlarında kütle düşüşünü PDR = 1 - kütle(varyant)/kütle(temiz) olarak raporlamak, "tek bir kümede tek ifade" eleştirisine karşı ucuz bir kalkan olur. Not: ürün yolu = ölçülen yol kuralı korunmalı, yalnızca soru metni değişir. Aşama: Checkpoint 2 sonrası, ikincil analiz.
4. **Tutarlılık testi** (Sec. 3.2.3, Xie vd.): cevap verdikten sonra "emin misin / yanlış" itirazıyla doğru cevabın bozulması. Bizim M1/M4'te doğru cevap veren kalemler için küçük bir yeniden-sorgulama sondası, "yaltaklanma" ekseni olarak eklenebilir. Çıkarım ve yeni eksen; ADR gerektirir, öncelik düşük.

### İnsan değerlendirmesi

5. **Makalenin üç faktörünü (sayı, ölçüt, uzmanlık) §2.5.3 protokol tablosuna açıkça eşlemek** (Sec. 5.2, Tablo human). Bizde: sayı ~300 cevap + üçte biri ikinci okuma; ölçütler (çekinme, altın bağlamda susma, isabetsiz atıf, iz tutarlılığı) makalenin genel 6 ölçütünden daha dar ve görev-özgü; uzmanlık katmanlı (kullanıcı, hukuk öğrencisi, hukukçu hakem). Makale uzmanlık düzeyinin ve varyansın raporlanmasını ister; planımız bunu karşılıyor. Rapor edilecek: okuyucu başına dağılım ve uzmanlık katmanına göre uyum.
6. **Makale insan varyansını açıkça kabul eder** ("yüksek varyans ve kararsızlık"). Savunma: anlaşma istatistikleri (insan↔insan, insan↔hakem) zaten planlıdır; makaleden alınan ek cümle "insan yer-gerçeği de gürültülüdür, tek okuyucuya güvenme". Bu, ikinci okumanın gerekçesi olarak MODEL_CARD §6 ve Makale 2'de atıflanabilir.
7. **Atomik olgu ayrıştırma (FActScore) fikri, isabetsiz atıf için insan işini azaltabilir** (Sec. 3.1.5). Cevabı madde-atıf birimlerine bölüp her birini ayrı etiketlemek, hukukçunun "isabetsiz atıf anlaşmazlığı" kararlarını birim düzeyine indirir. Çıkarım: bizde atıf doğrulama zaten deterministik; yeni olan, anlam isabetini (atıf geçerli ama iddiayı desteklemiyor) birim düzeyinde etiketlemektir. Aşama: insan doğrulaması protokolü yazılırken (F0-F1).

### Raporlama

8. **Bulguları "ne iyi, ne kötü" ikilisi olarak sunmak** (Sec. 6.1). Makale her sonuca "yalnızca belirli kümelere bağlıdır" kaydını düşer; MODEL_CARD §6 Sınırlar ve Makale 2 için aynı dilin (sonuçlar bu küme, bu rejim, bu hakem paneliyle) kullanılması tutarlıdır. Mevcut belgelerde zaten var; yeni iş gerektirmez.
9. **Değerlendirmeden sonra iyileştirme analizi** (Sec. 7.7). Makalenin "yalnızca skor değil, analiz ve yön göster" ilkesi, bizim B1 (isabetsiz atıf) için hata-tipi dökümüyle örtüşür. Yeni iş değil, mevcut yönelimin gerekçesi.
10. **Mevcut alan-özgü İngilizce benchmark'ları atlama kararı (ADR-0016) için ek dayanak:** makale hukukta yalnızca CUAD (sözleşme inceleme) ve iki özetleme/vergi çalışması gösterir; Türk mevzuatı için karşılığı yoktur. Dış benchmark'ların hukuk kapsamı dar olduğundan bu karar savunulur (Sec. 4.2; Sec. 3.3).

## Aktarılamayanlar / çekinceler

- **Hukuk kapsamı çok dar ve 2023 öncesi.** Hukuk yalnızca Sec. 3.3'te iki çalışma (özetleme, vergi) ve CUAD ile temsil edilir. Mevzuat soru-cevap, atıf doğrulama, çekinme yoktur. Hukuka özgü ölçüt tasarımı için yararlı değildir.
- **RAG, temellendirme ve çekinme (abstention) yok.** Makalede "olgusallık" kapalı kitap bilgi ve özetleme tutarlılığıdır; kaynak verilmiş durumdaki sadakat/çekinme ayrımı ele alınmaz. M1-M4 ve M2/M2b/M3 ayrımı için bu makale dayanak olamaz.
- **LLM-as-judge bu makalede zayıf işlenir:** hakem-LLM yanlılığı, aile dışlama, κ eşikleri, kendini tercih konularında içerik yoktur. Hakem paneli kararlarımız için dayanak başka literatürdür.
- **Anlaşma ve istatistik rehberi yok:** insan değerlendirmesi için evaluatör sayısı, κ, güven aralığı verilmez; yalnızca faktörler listelenir. Örneklem boyutu kararları kendi hesabımızdadır (Yol Haritası §2.5.5).
- **Metrik formüllerinde küçük tutarsızlıklar** (ör. ASR formülünün paydası kaynakta gevşek yazılmış); formülü doğrudan kopyalamadan özgün kaynağa (Wang vd. 2023) dönmek gerekir.
- **Çok kipli, ajan, tıp, eğitim, kişilik testi bölümleri bizim kapsamımız dışıdır** ve okunup atlandı.
- **Anti-hedef M5 (kör/ezber)** için makalede doğrudan karşılık yoktur; yalnızca sızıntı/ezber uyarısı (Sec. 7.4) dolaylı ilişkilidir.
- **Bir araştırma sonucu değil bir anket:** makalenin iddiaları kendi deneyi değil, aktarılan çalışmalardır; sayısal bulgu alıntılanacaksa özgün kaynağa gidilmelidir.
