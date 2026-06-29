# GEREKSİNİM - TMC GMP-3 / GMP-4 Taksimetre Tarafı Uyum Gereksinimleri

Taksimatik taksimetre yazılımının, Gelir İdaresi Başkanlığı (GİB) **TMC GMP-3** ve **TMC GMP-4**
protokolleriyle uyumlu hale getirilmesi için hazırlanan gereksinim spesifikasyonudur. Amaç, bu
taksimetrenin harici bir **TMC** (Taksi Mali Cihazı, taksiye özel OKC) ile eşleşebilmesi ve yolculuk
verisini TMC'ye raporlayabilmesidir.

| | |
|---|---|
| Belge durumu | TASLAK v0.2 - Codex + Gemini + Claude incelemeleri uygulandı (2026-06-30); sorumlu onayı bekliyor |
| Kaynak | `docs-tests/okc-gmp/GMP3-TMC.docx` (TMC GMP-3 Spesifikasyonu, Sürüm 1.0, 15.06.2026) |
| | `docs-tests/okc-gmp/GMP4-TMC.docx` (TMC GMP-4 Spesifikasyonu, Sürüm 1.0, 15.06.2026) |
| | (düz metin çıktıları: `GMP3-TMC.extracted.txt`, `GMP4-TMC.extracted.txt`) |
| Rolümüz | **TAKSİMETRE** - eşleşmeyi başlatan, yolculuk mesajlarını gönderen taraf |
| Karşı taraf | **TMC** (Taksi Mali Cihazı) - derlenmiş GMP-3 kütüphanesini sağlar, mali belgeyi üretir |
| Hedef donanım/yazılım | Bu depo: v34 7-segment Taksimatik yazılımı |
| Hedef iletişim ortamı | Yalnızca **Bluetooth** (Ethernet / WiFi / RS232 / USB bu belgenin kapsamı dışında) |
| Belge türü | Uyum spesifikasyonu - test edilebilir ZORUNLU gereksinimler + belirsizlikler kaydı. "Ne", "nasıl" değil. |
| İnceleme | v0.1 için 3 bağımsız inceleme (Codex, Gemini, Claude), 2026-06-30: üçü de rolleri, tüm sayısal sabitleri ve hata-kodu/aksiyon tablosunun kaynağa sadık olduğunu doğruladı. Bulgular v0.2'ye işlendi (yeni OQ-23..OQ-34). |
| Çeviri incelemesi | Codex + Gemini bu Türkçe çeviriyi 2026-06-30'da bağımsız olarak inceledi: anlam sadakati "olağanüstü/tam sadık", kritik/büyük anlam kayması yok. Terim sadakati düzeltmeleri (regülatörün kendi ifadeleriyle hizalama) uygulandı; ör. PR-13 "Pre-Master Key", TR-06 "Onay/Red Mesajı", PR-08 "eliptik eğri noktası", a/b "geçici özel anahtar". İngilizce ana belgede 3 bölüm referans hatası (TR-09, PR-09, LIB notu) bulunup düzeltildi. |

---

## 0. Bu belge nasıl okunur

### 0.1 Gereksinim anahtar kelimeleri (RFC 2119 tarzı)

İngilizce ana belgedeki anahtar kelimelerin bu çevirideki karşılıkları:

| Türkçe (bu belge) | Anlamı |
|-------------------|--------|
|**zorunludur** / **-meli/-malı** ; **yasaktır** / **-memeli/-mamalı** | Protokol uyumu için mutlak, zorunlu gereksinim. |
| **önerilir** / **önerilmez** | Tavsiye edilir; sapma için belgelenmiş bir gerekçe gerekir. |
| **-ebilir** (opsiyonel) | İsteğe bağlı / izin verilen davranış. |
|(kaynaktaki kesin değer) | Kaynak sabit bir değer (zaman aşımı, aralık, sabit) verdiğinde bu belge o kesin değeri taşır; sapma bir uyum hatasıdır. |

### 0.2 Gereksinim kimlikleri

Her gereksinimin sabit bir kimliği vardır: `ÖNEK-NN`. Önekler:

| Önek | Alan |
|------|------|
| `SCOPE` | Kapsam, rol, uygunluk |
| `TR`   | İletişim ve fiziksel çerçeveleme (Bluetooth) |
| `PR`   | GMP-3 eşleşme akışı (INIT / KEYREQ / CLOSE / ECHO) |
| `LIB`  | TMC üreticisinin derlenmiş GMP-3 kütüphanesi |
| `KR`   | Kriptografi ve anahtar türetme |
| `CV`   | PTMC sertifika doğrulaması |
| `SEQ`  | İşlem sıra numarası, tekrar (replay), yinelenen mesaj yönetimi |
| `SES`  | Oturum ve eşleşme yaşam döngüsü |
| `MSG`  | GMP-4 mesaj zarfı ve ortak başlık |
| `TS`   | TRIP_START / TRIP_START_ACK |
| `HB`   | HEARTBEAT / HEARTBEAT_ACK |
| `TE`   | TRIP_END / TRIP_END_ACK |
| `ER`   | ERROR mesajı ve hata kodları |
| `DF`   | Veri biçimleri (GPS, mesafe, seri no, ücret) |
| `TO`   | Zaman aşımı ve tekrar gönderim |

### 0.3 İzlenebilirlik

Her gereksinim kaynağını `[GMP-3: <bölüm adı>]` veya `[GMP-4: <bölüm adı>, s.<sayfa>]` biçiminde
gösterir. Bölüm adları kaynaktaki Türkçe başlıklardır; sayfa numaraları kaynak belgenin alt bilgi
sayfasıdır. Toplu izlenebilirlik matrisi §16'dadır.

### 0.4 Açık sorular

Kaynağın belirsiz bıraktığı, kendi içinde çelişen veya eksik tanımladığı her husus **burada sessizce
çözülmemiştir**. Bunlar Açık Sorular Kaydında (§15) bir `OQ-NN` kimliğiyle kayda geçirilir ve metin
içinde `(bkz. OQ-NN)` şeklinde anılır. Bu hususlar, ilgili gereksinim dondurulmadan önce GİB ve/veya
TMC kütüphane üreticisinden bir yanıt gerektirir.

---

## 1. Kapsam, rol ve uygunluk

- **SCOPE-01** - Yazılım, TMC GMP-3 ve TMC GMP-4'ün **taksimetre (TAKSİMETRE)** rolünü uygulamalıdır.
  TMC (mali cihaz) rolünü uygulaması zorunlu değildir. [GMP-3: Genel; GMP-4: Genel]

- **SCOPE-02** - Yazılım, harici bir TMC ile **Bluetooth** fiziksel bağlantısı üzerinden eşleşmeyi ve
  yolculuk mesajlaşmasını desteklemelidir. Ethernet, WiFi, RS232 ve USB iletişim ortamları bu belgenin
  kapsamı dışındadır. (Protokol beşini de destekler; burada yalnızca Bluetooth hedeflenmektedir.)
  [GMP-3: 4.4 Fiziksel İletişim Katmanı]

- **SCOPE-03** - Yazılım, TMC'yi mali veri için **güven kökü / kayıt sistemi** olarak kabul etmelidir:
  taksimetrenin açılma/kapanma (yolculuk başlatma/sonlandırma) işlemleri TMC'ye yansıtılır ve mali
  belge taksimetre tarafından değil TMC tarafından üretilir. [GMP-3: 4.2 Kapsam]

- **SCOPE-04** - GMP-3 güvenli oturumu başarıyla kurulmadan, GMP-4 yolculuk mesajları gönderilmemeli
  ve TMC'den kabul edilmemelidir. [GMP-4: Genel; GMP-4: Güvenlik İlkeleri]

- **SCOPE-05** - Yazılım, GMP-4'e marka/modelden bağımsız bir standart olarak uymalıdır: alan adları,
  veri tipleri, zorunluluk kuralları, uzunluklar, biçimler, aralıklar ve mesaj yapısı bu cihaz için
  değiştirilmemelidir. [GMP-4: Genel - "marka, model ... farklılığına neden olamaz"]

- **SCOPE-06** (geriye dönük bozmama) - Bu uyum çalışması eklemeli (additive) olmalıdır. Mevcut
  taksimetre-mobil uygulama BLE GATT sözleşmesini (RSA-2048 / AES) ya da bu v34 7-segment donanım
  varyantı üzerindeki mevcut yazılımın (FIRMWARE_VERSION 41 sahada, v42 geliştirmede) sahadaki diğer
  davranışlarını değiştirmemelidir. TMC'ye giden GMP-3/GMP-4 Bluetooth bağlantısı, mevcut uygulama
  bağlantısından **ayrı** bir Bluetooth işlevidir. (bkz. OQ-13 - BLE bir arada çalışması)

- **SCOPE-07** - Taksimetre yalnızca **aynı taksi** içinde fiziksel olarak kurulu olan TMC ile entegre
  çalışmalıdır; uzak veya paylaşımlı bir TMC ile değil. [GMP-3: 4.3 Taksimetre Entegrasyon Yöntemleri -
  "Taksimetrelerin sadece taksi içerisinde bulunan TMC'ler ile entegre çalışması gerekmektedir"]

---

## 2. Tanımlar

| Terim | Anlamı |
|-------|--------|
| TMC | Taksi Mali Cihazı - karşı taraftaki mali cihaz. |
| Taksimetre | Bu cihaz (Taksimatik). TMC'nin bakış açısından "harici sistem". |
| PTMC | TMC'nin ECDSA sertifikası / açık anahtarı; imza doğrulaması için taksimetreye gönderilir. |
| STMC | TMC'nin özel imzalama anahtarı (TMC'den hiç çıkmaz). ECDHE değeri A'yı imzalar. |
| ECDHE | Geçici (ephemeral) Eliptik Eğri Diffie-Hellman anahtar anlaşması (eğri secp384r1 / NIST P-384). |
| a, A | TMC'nin geçici özel anahtarı (skalar) `a` ve açık noktası `A = a × G`. |
| b, B | Taksimetrenin geçici özel anahtarı (skalar) `b` ve açık noktası `B = b × G`. |
| G | secp384r1 eğrisinin taban (base) noktası (kaynakta "EC Taban Noktası (G)"). |
| Z / PRM | Ortak gizli `Z = a×B = b×A`; Pre-Master Key (PRM) olarak kullanılır. |
| Master Secret | PRM'den TLS 1.2 PRF ile türetilen 32 baytlık gizli değer. |
| KENC | Master Secret'tan türetilen AES-256 veri şifreleme anahtarı. |
| KHMAC | Master Secret'tan türetilen HMAC-SHA-256 anahtarı. |
| IV | Anahtar türetme sırasında üretilen AES-CBC başlangıç vektörü (128 bit). |
| INIT / KEYREQ / CLOSE / ECHO | GMP-3 (şifresiz) eşleşme mesaj tipleri. |
| TRIP_START / HEARTBEAT / TRIP_END | GMP-4 (şifreli) uygulama mesaj tipleri. |
| ESHS | Elektronik Sertifika Hizmet Sağlayıcısı - PTMC/STMC sertifikasını veren makam. |
| Oturum ("session") | Canlı, güvenli bir GMP-3 kanalı; işlem sıra numarasının tükenmesi, heartbeat zaman aşımı veya açık sonlandırma ile sınırlıdır. (Güç kesintisi/yeniden başlatma ile ilişkisi belirsizdir - bkz. OQ-09.) |

---

## 3. İletişim ve fiziksel çerçeveleme (Bluetooth) - `TR`

Hedef iletişim ortamı Bluetooth olduğu için geçerlidir. [GMP-3: 4.4 Fiziksel İletişim Katmanı; 4.4.1.2
Bluetooth, USB ve RS232 iletişimi]

- **TR-01** - Bluetooth üzerinden gönderilen her GMP-3/GMP-4 **istek / veri** paketi, şu fiziksel
  çerçeveye sarılmalıdır: `STX (1 bayt) | paket uzunluğu (2 bayt) | veri bloğu | CRC (2 bayt) | ETX
  (1 bayt)`; veri bloğu, değiştirilmemiş GMP-3/GMP-4 paketidir. Fiziksel **ACK/NAK cevapları** (TR-06)
  bu 5 parçalı sarmalı değil, **ayrı ve daha kısa** bir çerçeve yapısını kullanır; bu yapının tam bayt
  düzeni kaynak çıktısında belirsizdir (bkz. OQ-26). [GMP-3: 4.4 tablosu - "İstek Bloğu" ile "Cevap
  (ONAY)" / "Cevap (RED)" ayrımı]

- **TR-02** - `STX` ikili (binary) `0x02` değeri olmalıdır. `ETX` ikili `0x03` değeri olmalıdır.
  [GMP-3: 4.4 tablosu]

- **TR-03** - 2 baytlık paket uzunluğu alanı **big-endian** (ağ bayt sırası) kodlanmalıdır. Fiziksel
  çerçevedeki tüm çok baytlı alanlar big-endian olmalıdır. [GMP-3: 4.4 - "ağ (big-endian) sıralaması"]
  (Uzunluğun tam olarak neyi saydığı - yalnızca veri mi, veri+CRC mi, STX/ETX dahil mi - açıkça
  belirtilmemiştir; bkz. OQ-01.)

- **TR-04** - 2 baytlık bütünlük alanı **CRC-16-CCITT** olmalıdır ve STX ile ETX arasındaki alan
  üzerinden hesaplanmalıdır. [GMP-3: 4.4; 4.4.1.2] (İKİ husus belirtilmemiştir - bkz. OQ-02: (a) kesin
  CRC-16-CCITT varyantı - polinom 0x1021, başlangıç 0xFFFF mı 0x0000 mı, refin/refout, xorout; ve
  (b) CRC'nin kapsadığı kesin bayt **aralığı** - yalnızca veri mi, yoksa uzunluk+veri mi, yani 2 baytlık
  uzunluk alanı dahil mi.)

- **TR-05** - CRC **yalnızca** fiziksel iletim hatalarını tespit etmek için kullanılmalıdır.
  Kriptografik bütünlük için CRC'ye güvenilmemelidir; kriptografik bütünlük GMP-3 şifreleme katmanı
  tarafından sağlanır. [GMP-3: 4.4; 5.2.1]

- **TR-06** - Tam ve doğru bir çerçeve alındığında alıcı **Onay Mesajı ACK** (ikili `0x06`) ile cevap
  vermelidir. Bir hata tespit edildiğinde **Red Mesajı NAK/NACK** (ikili `0x15`) ile cevap vermelidir.
  [GMP-3: 4.4 tablosu; 4.4.1.2 - "Onay Mesajı ACK ... Red Mesajı NAK"]

- **TR-07** - Bir istek bloğu gönderildikten sonra gönderici, cevap bloğunu **3000 ms zaman aşımı** ile
  beklemeli ve fiziksel alışverişi başarısız saymadan önce en fazla **3 deneme** yapmalıdır. [GMP-3: 4.4
  - "Bekleme Zaman Aşımı: 3000 ms ve Deneme Sayısı: 3"] ("Deneme Sayısı: 3" ifadesinin toplam 3 mü
  yoksa 1+3 mü olduğu açık değildir; bkz. OQ-03.)

- **TR-08** - Bu fiziksel ACK/NAK + CRC + STX/ETX çerçevelemesi Bluetooth'a uygulanmalıdır.
  Ethernet/WiFi bağlantılarına uygulanmamalıdır. (Bütünlük için belirtilmiştir; BT dışı bağlantılar
  kapsam dışıdır.) [GMP-3: 4.4.1.3]

- **TR-09** - Veri bloğunda taşınan GMP-3 yükü (şifreli GMP-4 mesajı), tekrar ataklarının (replay
  attack) engellenmesi için işlem sıra numarasını içermeli ve cihaz bunu kontrol etmelidir. [GMP-3: 4.4 - "işlem sıra
  numarasının kullanılması ve kontrol edilmesi ... zorunludur"]. (§8 `SEQ` ile gerçeklenir.)

---

## 4. GMP-3 eşleşme akışı - `PR`

Eşleşme ("eşleşme ve güvenli anahtar paylaşımı"), karşılıklı kimlik doğrulamayı ve oturum anahtarlarını
kurar. GMP-3 eşleşme mesajları **şifresizdir**. [GMP-3: 5.3 Mesaj Tipleri - "Şifresiz olarak gönderilir
ve cevaplanır"]

### 4.1 Eşleşme ön koşulları [GMP-3: 5.1.1 Eşleşme Ön Koşulları]

- **PR-01** - Taksimetre, eşleşmeye yalnızca şu koşullarda başlamalıdır: cihaz çalışır ve hazır
  durumda, iletişim ayarları yapılandırılmış ve tüm taksimetre kurulum/parametre ayarları tamamlanmış
  olmalıdır. [GMP-3: 5.1.1]

- **PR-01b** - Eşleşme, eşleşme anında TMC'nin **malileştirilmiş** olmasını ve tüm TMC tarafı eşleşme
  parametrelerinin ayarlanmış olmasını varsayar. Bu, taksimetrenin doğrudan doğrulayamayacağı bir TMC
  tarafı ön koşuldur; bütünlük için burada kayda geçirilmiştir. [GMP-3: 5.1.1 - "TMC eşleştirme anında
  malileştirilmiş olmalı ve eşleştirmeye ait tüm parametreler TMC'de ayarlanmış olmalı"]

- **PR-02** - Eşleşme **çevrimdışı / yerel** olarak yapılmalıdır: taksimetre ile TMC arasında seçilen
  fiziksel bağlantı üzerinden doğrudan; ara sunucu, üçüncü taraf servis veya çevrimiçi TMC-MYS bağlantısı
  olmadan. [GMP-3: 5.1.1 - "çevrimdışı (offline) ... doğrudan fiziksel iletişim katmanı üzerinden"]

- **PR-03** - Ortadaki adam (MITM) direnci şu mekanizmaların birleşimiyle sağlanmalıdır: doğrudan yerel
  Bluetooth bağlantısı (PR-02, PR-06), çevrimdışı eşleşme (PR-02), PTMC sertifika zinciri doğrulaması
  (CV-01..08) ve ECDHE değeri A'nın STMC-imza doğrulaması (PR-12). ("Güvenli olmalı" gibi genel bir
  ifade yerine somut, test edilebilir mekanizmalar olarak yeniden yazılmıştır.) [GMP-3: 5.1.1]

- **PR-04** - Eşleşme, **parola/yetki korumalı bir eşleşme menüsünden** başlatılmalıdır. Eşleşme
  menüsüne giriş yetkili bir kişi gerektirmelidir. [GMP-3: 5.2 Tablo 1, adım 1-2]

- **PR-05** - Eşleşmeden önce hem taksimetre hem de TMC **aynı bağlantı tipine** ayarlanmalıdır. Bu
  cihaz için bağlantı tipi Bluetooth olmalıdır. [GMP-3: 5.2 Tablo 1, adım 2-3]

- **PR-06** - Bluetooth için, **ilk mesajı gönderen** (INIT) taraf taksimetre olmalı; ilk mesajı
  dinleyen/alan taraf TMC olmalıdır. [GMP-3: 5.2 Tablo 1, adım 3 - "Bluetooth, RS232 ve USB
  seçimlerinde de Taksimetre ilk mesajı gönderen taraf olacaktır"]

### 4.2 Eşleşme mesaj dizisi [GMP-3: 5.2 Tablo 1; 5.3 Mesaj Tipleri]

- **PR-07** - Taksimetre, TMC'ye şunları içeren bir **INIT isteği** göndermelidir: taksimetre seri
  numarası ve 16 baytlık bir rassal değer ("İstek Mesajı Harici Sistem Rassal Sayısı"); §5.3 adım 1 bu
  değeri **"IV oluşturmak için"** olarak tanımlar. [GMP-3: 5.3 adım 1; 5.2 Tablo 1 adım 5] (Bu rassal
  değerle ilgili çözülmemiş iki çelişki: boyutu - §5.3'e göre 16 bayt, Tablo 2'ye göre 384 bit, bkz.
  OQ-04; ve rolü - §5.3'e göre IV kaynağı, KR-10'a göre master-secret PRF tohumu (seed), KR-11'e göre
  PRF zinciri IV'si, bkz. OQ-25.)

- **PR-08** - Taksimetre, TMC'den şunları içeren bir **INIT cevabı** kabul etmelidir: 16 baytlık bir
  rassal değer ("Cevap Mesajı TMC Rassal Numarası"), PTMC sertifikası ve desteklenen eliptik eğri
  noktası G. [GMP-3: 5.3 adım 2 - "desteklenen eliptik eğri noktası G yer alır"; 5.2 Tablo 1 adım 6]

- **PR-09** - INIT cevabı alındığında taksimetre, devam etmeden önce PTMC sertifikasını §7 (`CV`
  gereksinimleri) uyarınca **çevrimdışı** doğrulamalıdır. Doğrulama başarısız olursa taksimetre eşleşmeyi
  başarısız saymalı ve KEYREQ'e geçmemelidir. [GMP-3: 5.3 adım 3; 5.2 Tablo 1 adım 6 - "Doğrulama
  başarısız ise olumsuz cevap döner"]

- **PR-10** - Sertifika doğrulaması başarılı olduktan sonra taksimetre, geçici bir özel anahtar (skalar)
  `b` üretmeli, `B = b × G` hesaplamalı ve `B` değerini taşıyan bir **KEYREQ isteği** TMC'ye
  göndermelidir.
  [GMP-3: 5.3 adım 4; 5.2 Tablo 1 adım 6-7]

- **PR-11** - Taksimetre, TMC'den `A = a × G` değerini ve A üzerindeki STMC imzasını, yani
  `STMC( SHA-384( A || ExtSysRandom || TMCRandom ) )` değerini taşıyan bir **KEYREQ cevabı** kabul
  etmelidir. [GMP-3: 5.3 adım 5; 5.2 Tablo 1 adım 7] (İmzalanan mesajın kesin bayt düzeni/kodlaması
  belirtilmemiştir; bkz. OQ-05.)

- **PR-12** - Taksimetre, STMC imzasını PTMC kullanarak doğrulamalıdır. İmza geçersizse eşleşme
  başarısız olmalıdır. [GMP-3: 5.2 Tablo 1 adım 7 - "PTMC ile imzayı doğrular"]

- **PR-13** - İmza geçerliyse taksimetre, ortak gizli `Z = b × A` değerini hesaplamalı, `Z`'yi
  Pre-Master Key (PRM) olarak kabul etmeli ve oturum anahtarlarını §6 (`KR`) uyarınca türetmelidir.
  [GMP-3: 5.2 Tablo 1 adım 7]

- **PR-14** - Taksimetre, anahtar doğrulama verisini taşıyan bir **CLOSE isteği** göndermelidir: 32
  baytlık `0xFF…FF` sabitinin KENC ile AES-CBC kipinde şifrelenmiş hali. [GMP-3: 5.3 "CLOSE" adımı; 5.2
  Tablo 1 adım 8 - "32 byte FF'lerden oluşan veri KENC anahtarı ile şifrelenerek doğrulama verisi"]

- **PR-15** - Taksimetre, TMC tarafı anahtar doğrulamasının başarısını/başarısızlığını bildiren bir
  **CLOSE cevabı** kabul etmelidir. Olumlu bir CLOSE cevabında güvenli oturum kurulmuş sayılmalı ve
  sonraki tüm GMP-4 trafiğinin gizlilik ve bütünlüğü için KENC/KHMAC kullanılmalıdır. [GMP-3: 5.2 Tablo 1
  adım 8 - "TMC'den olumlu cevap gelmesi durumunda ..."]

- **PR-16** - TMC, eşleşme ve güvenli anahtar paylaşımı tamamlanmadan hiçbir GMP mesajına cevap
  vermemelidir; taksimetre, başarılı bir CLOSE öncesinde GMP-4 cevabı beklememelidir. [GMP-3: 5.2 -
  "TMC, eşleşme ve güvenli anahtar paylaşım işlemleri tamamlanmadan hiçbir TMC GMP mesajına cevap
  vermeyecektir"]

- **PR-17** - Taksimetrenin desteklemesi gereken GMP-3 mesaj kümesi tam olarak şudur: **INIT, KEYREQ,
  CLOSE, ECHO**. Bunlar **şifresiz** gönderilmeli ve cevaplanmalıdır. [GMP-3: 5.3 - "INIT, KEYREQ, CLOSE
  ve ECHO"] (ECHO mesajı adlandırılmış ancak içeriği/amacı hem GMP-3'te hem GMP-4'te tanımsızdır; bkz.
  OQ-06.)

- **PR-18** - TMC, başarısız saydığı bir isteğe yalnızca hata kodu taşıyan bir cevap **gönderebilir**.
  Taksimetre, bu yalnızca-hata içeren eşleşme cevaplarını işleyebilmelidir. [GMP-3: 5.3 adım 8 -
  "Opsiyonel olarak ... sadece hata kodunu içeren cevap mesajı gönderilebilir"]

---

## 5. TMC üreticisinin derlenmiş GMP-3 kütüphanesi - `LIB`

- **LIB-01** - Taksimetre, GMP-3 güvenli iletişim mekanizmasının tamamını, **TMC üreticisi tarafından
  sağlanan derlenmiş (kaynak kodu paylaşılmayan) TMC GMP-3 iletişim kütüphanesi** üzerinden
  yürütmelidir. Güvenli kripto bağımsız olarak yeniden yazılmamalıdır. [GMP-3: 5.2.3 - "derlenmiş (kaynak
  kodu paylaşılmayan) TMC GMP-3 iletişim kütüphanesini kullanacaktır ... Güvenli iletişim mekanizmasının
  tamamı TMC GMP-3 iletişim kütüphanesi üzerinden sağlanmalıdır"]

- **LIB-02** - Bu kütüphane en az şunları sağlamalıdır: sertifika doğrulama, geçici ECDHE anahtar
  değişimi, master-secret + oturum anahtarı türetme, şifreleme + bütünlük, tekrar (replay) koruması ve
  oturum yönetimi, oturum zaman aşımı kontrolü. [GMP-3: 5.2.3]

- **LIB-03** - GMP-3 kütüphanesinin güncellemeleri TMC üreticisinin kontrolünde olmalıdır. Kütüphane
  güncellemesi *gerektiren* bir taksimetre-uygulaması güncellemesi, TMC üreticisi ile koordine
  edilmelidir. [GMP-3: 5.2.5 - "TMC firmasının kontrolünde olmalıdır"]

- **LIB-04** (normatif olmayan fizibilite kapısı - bir GİB ZORUNLULUĞU DEĞİLDİR) - `KR`/`CV`/`PR` kripto
  gereksinimlerinin karşılanması, bu cihazın araç zinciri ve mimarisi (ESP32 Xtensa / ESP-IDF) için
  derlenmiş bir GMP-3 kütüphanesinin var olmasına bağlıdır. Bu MCU için kullanılabilirliği teyit
  edilmemiştir; bkz. OQ-07 - bu, tüm çabanın en büyük dış bağımlılığı ve baskın fizibilite riskidir.

> Not: `KR` (§6) ve `CV` (§7) kripto/sertifika gereksinimleri, kütüphanenin (§5) sunması gereken
> *gözlemlenebilir davranışı* uyum gereksinimi olarak tanımlar. Kütüphanenin bir davranışı sağladığı
> yerde, taksimetrenin yükümlülüğü bunu doğru sürmektir (mesaj sırası, girdiler, kalıcılık) - yeniden
> yazmak değil.

---

## 6. Kriptografi ve anahtar türetme - `KR`

### 6.1 Algoritma parametreleri [GMP-3: 5.2.1 Algoritma Parametreleri]

- **KR-01** - Anahtar anlaşması, **secp384r1 (NIST P-384)** eğrisinde ECDHE olmalıdır. Geçici özel
  anahtarlar (skalarlar) `a`, `b` 384 bitlik RSÜ (rassal sayı üreteci) çıktıları olmalıdır. [GMP-3:
  5.2.1 - "Geçici Özel Anahtar (a, b) Boyu | 384 bit (RSÜ çıktısı)"; RFC 5246/4492/8422]

- **KR-02** - Geçici açık anahtarlar (A, B), **sıkıştırılmamış (uncompressed)** biçimde EC noktaları
  olmalıdır. [GMP-3: 5.2.1]

- **KR-03** - İmzalar, secp384r1 üzerinde **SHA-384** özeti ile **ECDSA** olmalıdır. Doğrulayan açık
  anahtar (Q), PTMC sertifikasından alınmalıdır. [GMP-3: 5.2.1 - SEC2 / NIST SP800-56A / RFC 5480 / RFC
  5758 / FIPS 186-4]

- **KR-04** - Toplu veri şifrelemesi **AES-256 CBC kipinde** olmalıdır (NIST SP800-38A, "CBC.AES256").
  [GMP-3: 5.2.1; 5.2 - "çalışma modu NIST SP800-38A CBC.AES256"]

- **KR-05** - AES-CBC IV değeri **tahmin edilemez** olmalıdır. [GMP-3: 5.2 - "başlangıç değerleri (IV)
  tahmin edilemez olacak şekilde üretilecektir"]

- **KR-06** - AES-CBC için dolgu (padding), **TLS 1.2 padding** yöntemi olmalıdır. [GMP-3: 5.2 - "TLS
  1.2'de tanımlı olan padding yöntemi"]

- **KR-07** - Anahtarlı MAC, 256 bitlik bir anahtar (KHMAC) ile **HMAC-SHA-256** olmalıdır. [GMP-3:
  5.2.1 - FIPS 198-1]

- **KR-08** - Anahtar türetme fonksiyonu, SHA-256 (ve/veya SHA-384) özetiyle **TLS 1.2 PRF** (RFC 5246)
  olmalıdır. [GMP-3: 5.2.1 - TLS-PRF; SHA çıktısı 256 bit] (PRF tablosu "SHA-256 / SHA-384" listeler;
  hangi türetme adımında hangi özetin kullanılacağı sabitlenmemiştir; bkz. OQ-08.)

### 6.2 Anahtar türetme sırası [GMP-3: 5.2 - TLS 1.2 PRF türetmesi]

- **KR-09** - `PRM`, ECDHE ortak gizli `Z` olmalıdır (taksimetre tarafında `= b × A`). [GMP-3: 5.2
  Tablo 2]

- **KR-10** - `Master Secret = PRF(PRM, label="TMC GMP-3 istek", seed = ExtSysRandom || TMCRandom)`;
  çıktı uzunluğu **32 bayt**. [GMP-3: 5.2 - "Master secret değerinin boyu 32-byte olacaktır"]
  - `ExtSysRandom` = "İstek Mesajı Harici Sistem Rassal Numarası" (taksimetrenin INIT rassal değeri).
  - `TMCRandom` = "Cevap Mesajı TMC Rassal Numarası" (TMC'nin INIT-cevabı rassal değeri).

- **KR-11** - Kalan anahtarlar, `label = "TMC GMP-3 anahtarlar"` ve aynı `seed` ile zincirleme
  türetilmelidir:
  - `KHMAC = PRF(Master Secret, label, seed)`
  - `IV    = PRF(KHMAC, label, seed)`
  - `KENC  = PRF(IV, label, seed)`
  [GMP-3: 5.2 - KHMAC/IV/KENC PRF zinciri; Tablo 1 adım 8 ile teyit edilir: "Master Secret -> KHMAC ->
  IV -> KENC"] (Tablo 2'ye göre KENC 256 bit, IV 128 bit olmalı; oysa üçü de aynı PRF zincirinden gelir;
  her adımdaki çıktı uzunluğunun nasıl ele alınacağı açık değildir - bkz. OQ-08.)

- **KR-12** - Etiketin (label) kesin bayt kodlaması (UTF-8, sonlandırıcılı/sonlandırıcısız) ve tohum
  (seed) birleştirme sırası, TMC uygulamasıyla birebir aynı olmalıdır; çünkü herhangi bir uyumsuzluk
  CLOSE anahtar doğrulamasını bozar. Taksimetre, belirtildiği gibi `ExtSysRandom || TMCRandom` sırasını
  kullanmalıdır. [GMP-3: 5.2] (Etiket kodlama ayrıntısı; bkz. OQ-08.)

### 6.3 Anahtar doğrulama [GMP-3: 5.2 Tablo 1 adım 8; 5.3 CLOSE]

- **KR-13** - Taksimetre, anahtar doğrulama verisini, 32 baytlık `0xFFFFFFFF…FF` sabitini KENC ile
  AES-CBC altında şifreleyerek üretmeli ve CLOSE isteğinde göndermelidir. [GMP-3: 5.2 Tablo 1 adım 8]
  (KR-11'deki 128 bitlik IV'nin burada kullanılıp kullanılmadığı ve 32 baytlık düz metnin dolgusu açık
  değildir; bkz. OQ-08.)

- **KR-14** - Taksimetre, oturum anahtarlarını yalnızca TMC'nin CLOSE cevabı olumlu olduğunda (TMC aynı
  doğrulama verisini yeniden hesapladığında) karşılıklı doğrulanmış saymalıdır. [GMP-3: 5.2 Tablo 1 adım
  8]

### 6.4 Anahtar saklama [GMP-3: 5.2 Tablo 2 - "Saklama Yeri"]

- **KR-15** - Uzun ömürlü sertifika/anahtar materyali ve türetilen oturum anahtarları cihazın **güvenli
  alanında** tutulmalıdır. Geçici rassal değerler (`ExtSysRandom`, `TMCRandom`) yalnızca anlık
  tutulmalıdır ("anlık saklanır"). [GMP-3: 5.2 Tablo 2] (Bu cihazda GMP anahtar materyali için "güvenli
  alan" ile mevcut şifreli flash bölümleri arasındaki ilişki bir donanım-güvenliği tasarım sorusudur;
  bkz. OQ-10.)

---

## 7. PTMC sertifika doğrulaması - `CV`

Taksimetre, PTMC sertifikasını kullanmadan önce, aşağıdaki kontrollerin tümünü yaparak doğrulamalıdır.
Herhangi bir başarısızlık bir hata cevabı üretmeli ve eşleşmeyi sonlandırmalıdır. [GMP-3: 5.2.4 PTMC
Sertifikasının Doğrulanması]

- **CV-01** - Sertifika **biçimi** kontrol edilmelidir; bozuksa -> hata. [GMP-3: 5.2.4 #1]
- **CV-02** - Sertifika **tipi** kontrol edilmelidir; desteklenmeyen tipse -> hata. [GMP-3: 5.2.4 #2]
- **CV-03** - Sertifika **yayıncısı** kontrol edilmelidir; bilinmeyen yayıncıysa -> hata. [GMP-3:
  5.2.4 #3]
- **CV-04** - **Key Usage** alanı kontrol edilerek açık anahtarın amacına uygun kullanılıp
  kullanılmadığı doğrulanmalıdır. [GMP-3: 5.2.4 #4]
- **CV-05** - Sertifikanın **geçerlilik süresi** kontrol edilmelidir; süresi dolmuşsa -> hata. [GMP-3:
  5.2.4 #5] (Güvenilir bir güncel saat gerektirir; bkz. OQ-11.)
- **CV-06** - Sertifika **imzası**, yayıncının açık anahtarı kullanılarak doğrulanmalıdır. [GMP-3:
  5.2.4 #6]
- **CV-07** - Doğrulama, kök sertifikadan TMC sertifikasına kadar **tüm sertifika zinciri** için
  yapılmalıdır. [GMP-3: 5.2.4 #7] (Güvenilir kök/ara sertifikaların cihaza yüklenmesi gerekir; bkz.
  OQ-12.)
- **CV-08** - Sertifikanın `subject` alanındaki TMC **Cihaz sicil numarası** kontrol edilmelidir;
  başarısızlıkta -> hata. [GMP-3: 5.2.4 #8]

---

## 8. İşlem sıra numarası, tekrar (replay) ve yinelenenler - `SEQ`

Hem GMP-3 (`işlem sıra numarası`) hem de GMP-4 (`sequenceNumber`) seviyelerinde geçerlidir; bunlar aynı
mantıksal sayaçtır. [GMP-3: 5.2.5.1; GMP-4: İşlem Sıra Numarası Kullanımı, s.9]

> **Sayaç modeli.** GMP-3 §5.2.5.1, *simetrik* iki-sayaçlı bir model tanımlar: TMC taksimetre için bir
> sayaç `S`, taksimetre TMC için bir sayaç `T` tutar; ayrıca her taraf diğerinden aldığı son istek sıra
> numarasını saklar. Ancak GMP-4, **TMC->taksimetre yönünde hiçbir istek mesajı** tanımlamaz (TMC yalnızca
> `*_ACK` / `ERROR` *cevapları* gönderir, bkz. MSG-12); dolayısıyla taksimetrenin "gelen istek"
> yükümlülüklerinin (SEQ-07) uygulanacağı bir GMP-4 mesajı yoktur. Bu gerilim OQ-27 olarak kayda
> geçirilmiştir. Aşağıdaki gereksinimler taksimetrenin kendi giden-istek sayacı `T`'yi (iyi tanımlı)
> belirtir ve gelen-taraf ifadesini kaynaktan birebir taşır (muhtemelen işlevsiz/kalıntı).

- **SEQ-01** - Taksimetre, eşleştiği TMC için kendi giden-istek sayacı `T`'yi tutmalıdır. [GMP-3:
  5.2.5.1]
- **SEQ-02** - Her (yeniden) eşleşmede / yeni oturumda sayaç sıfırlanmalıdır (`T = 0`); böylece ilk
  istek 1 sıra numarasını taşır. Şifresiz GMP-3 eşleşme mesajları (INIT/KEYREQ/CLOSE), bu 1-999 GMP-4
  sayacının **dışında** kabul edilir; çünkü örneklerde üç eşleşme mesajı önce gelmesine rağmen ilk GMP-4
  mesajı (TRIP_START) = 1'dir (bkz. OQ-28). [GMP-3: 5.2.5.1; GMP-4 s.9 - "1 değerinden başlatılır"]
- **SEQ-03** - Her yeni istek mesajı sayacı tam olarak 1 artırmalıdır (`T = T + 1`). [GMP-3: 5.2.5.1]
- **SEQ-04** - Her cevap, cevapladığı isteğin **aynı** sıra numarasını taşımalıdır. [GMP-3: 5.2.5.1;
  GMP-4 s.9]
- **SEQ-05** - Geçerli sıra numarası aralığı **1-999** olmalıdır. [GMP-3: 5.2.5.1; GMP-4 s.9]
- **SEQ-06** - Sıra numarası **999**'a ulaştığında mevcut güvenli oturum sonlandırılmalı ve sonraki
  GMP-4 mesajlarından önce yeni bir GMP-3 eşleşme / anahtar paylaşımı yapılmalıdır. [GMP-3: 5.2.5.1;
  GMP-4 s.9-10]
- **SEQ-07** - Taksimetre, TMC'den gelen son isteğin sıra numarasını saklamalıdır. [GMP-3: 5.2.5.1 -
  "Taksimetre, TMC'den gelen son istek mesajının sıra numarasını saklayacaktır"] (NOT: GMP-4,
  TMC->taksimetre yönünde *istek* mesajı tanımlamaz, yalnızca ACK/ERROR cevapları - bu nedenle bu
  gereksinim yazıldığı haliyle işlevsiz/test edilemez olabilir; bkz. OQ-27.)
- **SEQ-08** - Cevaplanmamış bir isteğin tekrar gönderiminde `messageId` ve `sequenceNumber`
  değişmemelidir; yalnızca `uid` yeniden üretilebilir. [GMP-4: 9.4 Retry ve Duplicate Yönetimi]
- **SEQ-09** - Yinelenen/tekrar tespiti `messageId` **ve** `sequenceNumber` birlikte kullanılarak
  yapılmalıdır; `uid` kullanılmamalıdır. [GMP-4: 9.4; 9 giriş]
- **SEQ-10** - `INVALID_SEQUENCE` bir **TMC tarafı** kontrolüdür: TMC, sıra numarası beklenen sıraya
  uymayan, eski, atlanmış veya mevcut oturum dışında kalan bir taksimetre *isteğini* reddeder.
  Taksimetre bu hatanın alıcısıdır ve onu `ER` uyarınca işlemelidir (`INVALID_SEQUENCE` hatasını kendisi
  **üretmez**). [GMP-4: s.9 - "Beklenen sıraya uymayan ... INVALID_SEQUENCE hatası ile reddedilir"]
- **SEQ-10b** (türetilmiş - doğrudan kaynak yok) - Taksimetrenin, `sequenceNumber` ve `correlationId`
  değerleri bekleyen bir istekle eşleşmeyen herhangi bir TMC *cevabını* reddetmesi/yok sayması önerilir.
  (GMP-3 eşleştirme kuralının yazar tarafından türetilmiş taksimetre-tarafı uyarlaması; correlationId
  eşleştirme beklentisi teyit edilmelidir.)
- **SEQ-11** - Taksimetre, TMC'nin daha önce işlediği bir isteği tekrar gönderirse, TMC'nin yeniden
  gönderdiği önceki cevabı kabul etmelidir (TMC yeniden işlemez). [GMP-4: 9.4; GMP-3: 5.2.5.1]

---

## 9. Oturum ve eşleşme yaşam döngüsü - `SES`

### 9.1 Yeniden eşleşmenin GEREKLİ olduğu durumlar [GMP-3: 5.2.5 Eşleşme ve Güvenli Anahtar Paylaşım Periyodu]

- **SES-01** - Taksimetre, şu durumlarda tam bir yeniden eşleşmeyi (eşleşme + anahtar paylaşımı)
  tetiklemelidir: (a) taksimetre ve/veya TMC ilk kez kuruluyorsa; (b) taksimetre veya TMC'den biri
  değişmişse; (c) bankacılık/güvenli iletişim anahtarları herhangi bir nedenle silinmişse (onarım,
  saldırı algılama vb.); (d) bir cihaz kimlik doğrulama/eşleşme anahtarlarını kaybetmişse; (e) TMC
  üreticisi GMP-3 kütüphanesi güncellenmişse. [GMP-3: 5.2.5]

### 9.2 Yeniden eşleşmenin GEREKMEDİĞİ durumlar [GMP-3: 5.2.5]

- **SES-02** - Yalnızca şu nedenlerle yeniden eşleşme gerekmemelidir: (a) taksimetre ile TMC arasındaki
  fiziksel bağlantı kesilmiş/çıkarılmışsa; (b) cihazlardan biri veya ikisi kapatılmış/yeniden
  başlatılmışsa; (c) GMP-3 kütüphane güncellemesi gerektirmeyen bir taksimetre-uygulaması güncellemesi
  olmuşsa. [GMP-3: 5.2.5] ("Yeniden başlatmadan sonra yeniden eşleşme yok" ile "oturum anahtarları/sıra
  her oturumda sıfırlanır" arasındaki gerilim çözülmemiştir; bkz. OQ-09.)

### 9.3 Oturum sonlandırma ve yeniden kurma [GMP-4: 9.3; 9.5; 16]

- **SES-03** - Bir TRIP_START, azami tekrar sayısından sonra geçerli bir cevap almazsa taksimetre,
  yolculuk başlatmayı TMC tarafından **onaylanmamış** saymalı, mevcut GMP-4 mesajlaşmasını
  sonlandırmalı ve GMP-3 güvenli oturumunu yeniden kurmalıdır. [GMP-4: 9.3 Zaman Aşımı Sonrası Davranış]

- **SES-04** - `ERROR.action = TERMINATE_SESSION` geldiğinde taksimetre, mevcut GMP-3 güvenli oturumunu
  sonlandırmalı ve GMP-4 mesajlaşmasına devam etmeden önce yeni bir güvenli oturum kurmalıdır. [GMP-4:
  9.5]

- **SES-05** - Taksimetre, yolculuk aktifken **60000 ms** varsayılan periyotla HEARTBEAT göndermelidir;
  TMC, **180000 ms** boyunca HEARTBEAT almazsa GMP-3 oturumunu sonlandıracaktır. [GMP-4: 16 -
  "Varsayılan heartbeat periyodu 60000 ms ... 180000 ms boyunca HEARTBEAT alamazsa ... oturumu
  sonlandırır"]

- **SES-06** - Bir yolculuk tamamlanmadan oturum herhangi bir nedenle sonlandığında, yeniden
  bağlanıldığında taksimetre o yolculuğa ait GMP-4 yükümlülüğünü sürdürebilmelidir (ör. TRIP_END'i
  özgün `messageId` + `sequenceNumber` ile tekrar göndermek). [GMP-4: 9.3] ("Oturum sıfırlama ->
  sequenceNumber 1'e döner" ile "TRIP_END'i aynı sequenceNumber ile tekrar gönder" arasındaki etkileşim
  çelişkilidir; bkz. OQ-14.)

---

## 10. GMP-4 mesaj zarfı ve ortak başlık - `MSG`

[GMP-4: Genel Mesaj Zarfı, s.8; Ortak Header Alanları, s.9]

- **MSG-01** - Her GMP-4 mesajı, iki üst-düzey nesneli (`header` ve `body`) **UTF-8 JSON** olmalıdır.
  [GMP-4: Genel; Genel Mesaj Zarfı]
- **MSG-02** - Tüm alan adları **camelCase** kullanmalıdır. [GMP-4: Genel - "camelCase yazım kuralı"]
- **MSG-03** - GMP-4 kendi bütünlük mekanizmasını tanımlamamalıdır (GMP-4 seviyesinde
  HMAC/MAC/payload-hash/imza yok); gizlilik, bütünlük, taşıma ve tekrar koruması GMP-3 katmanı
  tarafından sağlanır. [GMP-4: Güvenlik İlkeleri]
- **MSG-04** - Canonical JSON zorunlu olmamalıdır. [GMP-4: Güvenlik İlkeleri - "canonical JSON
  zorunluluğu bulunmamaktadır"]
- **MSG-05** - `header.protocolVersion` mevcut olmalı ve `"1.0"` dizgisi olmalıdır. [GMP-4: tüm mesaj
  örnekleri; `INVALID_PROTOCOLVERSION` hatası] (protocolVersion her örnekte yer alır ve özel bir hata
  koduna sahiptir, ancak ortak başlık alan tablosunda yoktur; bkz. OQ-15.)
- **MSG-06** - `header.uid`, **her iletim denemesi** için (tekrarlar dahil) yeniden üretilen bir UUID
  v4 (36 karakter) olmalıdır. [GMP-4: Ortak Header Alanları, s.9; 9.4]
- **MSG-07** - `header.messageId`, iş mesajını tanımlayan bir UUID v4 (36 karakter) olmalı ve o mesajın
  tekrar gönderimlerinde sabit kalmalıdır. [GMP-4: Ortak Header, s.9; 9.4]
- **MSG-08** - `header.correlationId`, istek mesajlarında `null` olmalı; cevap mesajlarında ise
  cevaplanan isteğin `messageId` değerine eşit olmalıdır. [GMP-4: Ortak Header, s.9]
- **MSG-09** - `header.sequenceNumber`, 1-999 aralığında bir tam sayı olmalıdır (§8 `SEQ` uyarınca).
  [GMP-4: Ortak Header, s.9; İşlem Sıra Numarası]
- **MSG-10** - `header.messageType`, tam olarak şunlardan biri olmalıdır: `TRIP_START`,
  `TRIP_START_ACK`, `HEARTBEAT`, `HEARTBEAT_ACK`, `TRIP_END`, `TRIP_END_ACK`, `ERROR`. [GMP-4: Mesaj
  Tipleri, s.7-8]
- **MSG-11** - `header.messageTime`, ISO-8601 UTC zaman damgası olmalıdır (ör.
  `2026-06-20T10:15:30Z`). [GMP-4: Ortak Header, s.9]
- **MSG-12** - Taksimetre yalnızca üç istek tipini (`TRIP_START`, `HEARTBEAT`, `TRIP_END`)
  üretmelidir; `*_ACK` ve `ERROR` TMC->taksimetre yönündedir ve yalnızca tüketilmelidir. [GMP-4: Mesaj
  Tipleri tablosu]

---

## 11. Uygulama mesajları - `TS` / `HB` / `TE` / `AK`

### 11.1 TRIP_START [GMP-4: TRIP_START Mesajı, s.18-20]

- **TS-01** - Yolculuk başladığında taksimetre, TMC'ye bir `TRIP_START` (oturumun ilk GMP-4 uygulama
  mesajı) göndermelidir. [GMP-4: 15; 15.1]
- **TS-02** - `TRIP_START.body` şunları içermelidir: `tripId` (UUID v4, 36 karakter),
  `taximeterSerialNumber` (`DF` uyarınca 12 karakter), `tripStartTime` (ISO-8601 UTC), `distanceInfo`
  (`DF` uyarınca nesne), `gps` (`DF` uyarınca nesne). Beşi de zorunludur ("Evet"). [GMP-4: 15.1]
- **TS-03** - Taksimetre, daha önce kabul edilmiş bir yolculuğun `tripId` değerini yeniden
  kullanmamalıdır; tekrar kullanılan tripId'ye TMC `TRIP_ALREADY_STARTED` ile cevap verir. [GMP-4: 15 -
  "Aynı tripId ... yeni bir TRIP_START mesajı kabul edilmez"]
- **TS-04** - Başarılı cevap, `body.tripId` (kabul edilen yolculuk) ve `body.result = "ACCEPTED"`
  içeren bir `TRIP_START_ACK` olmalıdır. [GMP-4: 15.3-15.4; 14]
- **TS-05** - Taksimetre, bir önceki yolculuğa ait mali belgenin düzenlendiği bilgisi kendisine
  iletilmeden (yani önceki bir `TRIP_END` tamamlanmadan) **yeni** bir yolculuk başlatmamalıdır. [GMP-4:
  9.1 notu - "Mali Belgenin düzenlendiği bilgisi taksimetreye iletilmeden taksimetre yeni yolculuk
  başlatamaz"]

### 11.2 HEARTBEAT [GMP-4: HEARTBEAT Mesajı, s.20-22]

- **HB-01** - Yolculuk aktifken taksimetre, periyodik olarak (varsayılan her 60000 ms) `HEARTBEAT`
  göndermelidir. [GMP-4: 16; 5]
- **HB-02** - `HEARTBEAT.body`, `tripId` (UUID v4, 36 karakter) ve `heartbeatTime` (ISO-8601 UTC)
  içermelidir. İkisi de zorunludur. [GMP-4: 16.1]
- **HB-03** - Başarılı cevap, `body.tripId` ve `body.result = "ALIVE"` içeren bir `HEARTBEAT_ACK`
  olmalıdır. [GMP-4: 16.3-16.4; 14]
- **HB-04** - Taksimetre, HEARTBEAT'in yalnızca aktif, kabul edilmiş ve henüz bitmemiş bir `tripId`
  için geçerli olduğunu dikkate almalıdır; geçersiz/bilinmeyen/aktif olmayan bir tripId için TMC ne
  `HEARTBEAT_ACK` ne de `ERROR` döner. Taksimetre, cevapsız durumu `TO` uyarınca işlemelidir. [GMP-4:
  16; 14; 18]
- **HB-05** - Taksimetre, bir HEARTBEAT'e cevaben `ERROR` beklememelidir (HEARTBEAT için ERROR
  gönderilmez). [GMP-4: 9; 14; 18]

### 11.3 TRIP_END [GMP-4: TRIP_END Mesajı, s.22-24]

- **TE-01** - Yolculuk bittiğinde taksimetre, TMC'ye `TRIP_END` göndermelidir. [GMP-4: 17]
- **TE-02** - `TRIP_END.body` şunları içermelidir: `tripId` (UUID v4), `tripEndTime` (ISO-8601 UTC),
  `distanceInfo` (nesne), `gps` (nesne), `fare` (nesne). Hepsi zorunludur. [GMP-4: 17.1]
- **TE-03** - Taksimetre, hiç başlatılmamış bir `tripId` için `TRIP_END` göndermemelidir; TMC
  `TRIP_NOT_STARTED` ile cevap verir. [GMP-4: 17 - "TRIP_START mesajı alınmadan ... TRIP_END ... kabul
  edilmez"]
- **TE-04** - Başarılı cevap, `body.tripId` ve `body.result = "COMPLETED"` içeren bir `TRIP_END_ACK`
  olmalıdır; bu, yalnızca TMC mali belgeyi ürettikten **sonra** gönderilir. [GMP-4: 17.4; 5 - "mali
  belgeyi üretip çıktısını verdikten sonra ... TRIP_END_ACK"]
- **TE-05** - Zaten tamamlanmış bir `tripId` için yeni bir `TRIP_END` kabul edilmemelidir; yalnızca
  yinelenen/tekrar gönderimler (aynı `messageId` + `sequenceNumber`) için önceki `TRIP_END_ACK` yeniden
  gönderilir. [GMP-4: 17]
- **TE-06** - Taksimetre, yinelenen bir `TRIP_END` için TMC'nin ikinci bir mali belge / finansal işlem
  üretmeyeceğine güvenmelidir. Taksimetrenin yinelemeye-güvenli davranışı, değişmeyen `messageId` +
  `sequenceNumber` ile tekrar göndermektir. [GMP-4: 9.4 - "aynı yolculuk için ikinci kez mali belge
  üretmez"]

### 11.4 ACK kuralları [GMP-4: ACK Mesajları İçin Genel Kural, s.17]

- **AK-01** - `*_ACK` mesajları **yalnızca başarı** olarak yorumlanmalıdır. [GMP-4: 14]
- **AK-02** - Taksimetre, sabit `result` değerlerini kabul etmelidir: `TRIP_START_ACK -> "ACCEPTED"`,
  `HEARTBEAT_ACK -> "ALIVE"`, `TRIP_END_ACK -> "COMPLETED"`. [GMP-4: 14 tablosu]
- **AK-03** - `*_ACK` gövdeleri `errorCode` içermemelidir; `errorCode` yalnızca `ERROR` içinde yer
  alır. [GMP-4: 14]

---

## 12. ERROR yönetimi ve hata kodları - `ER`

[GMP-4: ERROR Mesajı, s.25-28; Standart Hata Kodları, s.27-28]

- **ER-01** - `ERROR` tek yönlüdür (yalnızca TMC -> taksimetre); taksimetre onu yalnızca tüketmelidir.
  [GMP-4: 18]
- **ER-02** - Bir isteğe karşılık `ERROR` döndüğünde, o istek cevaplanmış sayılmalı ve taksimetre
  `ERROR.action` uyarınca davranmalıdır. [GMP-4: 9.5; 18]
- **ER-03** - `ERROR.body` şunları içermelidir: `tripId` (UUID v4 veya `null`), `errorCode` (enum),
  `action` (enum). Hata mesajının `header.correlationId` değeri, hataya konu isteğin `messageId`
  değeri olmalıdır. [GMP-4: 18; 18.1]
- **ER-04** - Hataya konu istekten okunabilir, geçerli bir `tripId` varsa `ERROR.tripId` onu taşır;
  aksi halde `null`. Taksimetre ikisini de kabul etmelidir. [GMP-4: 18.1]
- **ER-05** - Taksimetre şu `ERROR.action` davranışlarını uygulamalıdır [GMP-4: 9.5; 18.2]:
  - `RETRY` -> mesaj, aynı `messageId` + `sequenceNumber` ile tekrar gönderilebilir.
  - `PREVIOUS_RESPONSE` -> mesaj daha önce işlenmiş kabul edilir; önceki cevap esas alınır.
  - `RETRY_NOT_ALLOWED` -> mesaj tekrar gönderilmemelidir.
  - `TERMINATE_SESSION` -> GMP-3 oturumu sonlandırılmalı ve devam etmeden önce yeniden kurulmalıdır.
  - `IGNORE` -> mesaj yok sayılabilir. (NOT: `IGNORE`, action enum'unda tanımlıdır ancak §12'deki
    standart hata kodları tablosunun hiçbir satırında kullanılmaz; bkz. OQ-33.)

- **ER-06** - Taksimetre, aşağıdaki standart hata kodlarını ve varsayılan aksiyonlarını tanımalıdır.
  [GMP-4: Standart Hata Kodları, s.27-28] **(Aksiyon sütunu, bozulmuş bir tablo çıktısından yeniden
  oluşturulmuştur. Üç inceleyici de - Codex, Gemini, Claude - bu eşlemeyi bağımsız olarak yeniden
  türetip doğruladı; yine de OQ-16'daki orijinal DOCX'e karşı son kontrol, dondurmadan önce yerinde
  kalmaktadır.)**

  | errorCode | Anlamı | Aksiyon (doğrulanacak) |
  |-----------|--------|------------------------|
  | `INVALID_FORMAT` | JSON biçimi geçersiz | RETRY |
  | `UNKNOWN_MESSAGE_TYPE` | Mesaj tipi bilinmiyor | TERMINATE_SESSION |
  | `MISSING_REQUIRED_FIELD` | Zorunlu alan eksik | RETRY |
  | `INVALID_FIELD_TYPE` | Alan tipi hatalı | RETRY |
  | `INVALID_SEQUENCE` | sequenceNumber geçersiz | TERMINATE_SESSION |
  | `DUPLICATE_MESSAGE` | Mesaj daha önce işlendi | PREVIOUS_RESPONSE |
  | `REPLAY_DETECTED` | Replay şüphesi tespit edildi | TERMINATE_SESSION |
  | `SESSION_NOT_ACTIVE` | GMP-3 oturumu aktif değil | TERMINATE_SESSION |
  | `SESSION_EXPIRED` | GMP-3 oturum süresi doldu | TERMINATE_SESSION |
  | `TRIP_ALREADY_STARTED` | Aynı tripId ile yolculuk zaten başlatıldı | RETRY_NOT_ALLOWED |
  | `TRIP_NOT_STARTED` | TRIP_START olmadan TRIP_END | RETRY_NOT_ALLOWED |
  | `TRIP_NOT_FOUND` | tripId bulunamadı | RETRY_NOT_ALLOWED |
  | `INVALID_TRIP_STATE` | Yolculuk durumu mesaj için uygun değil | RETRY_NOT_ALLOWED |
  | `INVALID_DISTANCE` | Mesafe bilgisi geçersiz | RETRY |
  | `INVALID_FARE` | Ücret geçersiz | RETRY |
  | `INVALID_GPS` | GPS biçimi geçersiz | RETRY |
  | `HEARTBEAT_TIMEOUT` | Heartbeat zaman aşımı oluştu | TERMINATE_SESSION (iletim kanalı belirsiz - bkz. OQ-34) |
  | `INTERNAL_ERROR` | Dahili hata | RETRY |
  | `INVALID_PROTOCOLVERSION` | Protokol versiyonu geçersiz | TERMINATE_SESSION |

- **ER-07** - Hata anlamı standart `errorCode` (ve kod tablosu) üzerinden türetilmelidir, serbest
  metinden değil. Hata mesajları serbest metin açıklama taşımamalıdır. [GMP-4: 18 - "Hata açıklaması
  serbest metin olarak taşınmaz"]

---

## 13. Veri biçimleri - `DF`

### 13.1 GPS [GMP-4: GPS Veri Formatı, s.12-14]

- **DF-01** - GPS verisi **opsiyoneldir**. GPS sağlayamayan bir taksimetre `gps.available = false`
  göndermeli ve başka hiçbir gps alanı eklememelidir. [GMP-4: 10; 10.3]
- **DF-02** - `gps.available = true` ise `latitude` ve `longitude` mevcut olmalıdır. [GMP-4: 10.4]
- **DF-03** - `latitude`/`longitude`, WGS84 decimal degree (ondalık derece) değerinin 1.000.000 ile
  çarpımına eşit **tam sayılar** olmalıdır. Nokta veya virgül içermemeli ve negatif olmamalıdır. [GMP-4: 10; 10.4]
- **DF-04** - `latitude`, `35000000`-`42500000` arasında; `longitude`, `25500000`-`45000000` arasında
  olmalıdır (Türkiye koordinat aralığı). [GMP-4: 10.1; 10.4]
- **DF-05** - `accuracyMeters` opsiyoneldir; gönderilirse sıfır veya pozitif bir tam sayı (metre)
  olmalıdır. [GMP-4: 10.1; 10.4] (Alan-adı inceliği: metin `accuracyMeters` kullanır, bir tablo hücresi
  `accuracyMeter` gösterir; kanonik olarak `accuracyMeters` esas alınmalıdır - bkz. OQ-17.)
- **DF-06** - Bu kurallara uymayan GPS verisi TMC tarafından `INVALID_GPS` olarak reddedilebilir;
  taksimetre, ürettiği GPS verisinin uygun olmasını sağlamalıdır. [GMP-4: 10.4]

### 13.2 Mesafe [GMP-4: Mesafe Bilgisi Formatı, s.14-16]

- **DF-07** - `distanceInfo` şunları içermelidir: `counterDate` (dizgi `YYYY-MM-DD`),
  `occupiedDistanceMeters` (tam sayı >=0), `freeDistanceMeters` (tam sayı >=0), `totalDistanceMeters`
  (tam sayı >=0). Hepsi zorunludur; tüm mesafeler **metre cinsinden tam sayı** olmalıdır (ondalık km
  yok). [GMP-4: 11.1]
- **DF-08** - `counterDate`, taksimetrenin **yerel takvim günü** olmalıdır; bu, `messageTime` içindeki
  UTC tarihinden farklı olabilir. [GMP-4: 11.4]
- **DF-09** - `occupiedDistanceMeters` ve `freeDistanceMeters`, yerel `00:00:00`'da sıfırlanan
  **günlük** sayaçlardır. [GMP-4: 11]
- **DF-10** - `totalDistanceMeters`, **sıfırlanmayan, monoton artan** bir sayaç olmalıdır
  (toplam/odometer karşılığı). Geriye gitmemelidir. [GMP-4: 11; 11.3]
- **DF-11** - `TRIP_END.distanceInfo.totalDistanceMeters`, `TRIP_START.distanceInfo.totalDistanceMeters`
  değerinden küçük olmamalıdır. [GMP-4: 11.3]
- **DF-12** - Yerel gece yarısını geçişte, bir TRIP_END günlük sayacı, TRIP_START günlük sayacından
  küçük olabilir (bu tek başına hata değildir); **aynı `counterDate` içinde** geriye gidiş TMC
  tarafından `INVALID_DISTANCE` olarak değerlendirilebilir. Taksimetre, sayaçları bu kurallarla tutarlı
  raporlamalıdır. [GMP-4: 11.4]

### 13.3 Taksimetre seri numarası [GMP-4: Taksimetre Seri Numarası Formatı, s.16]

- **DF-13** - `taximeterSerialNumber` **tam 12 karakter** olmalıdır. Daha kısa değerler, **soluna `0`
  eklenerek 12 karaktere tamamlanmalıdır**. 12 karakterden uzun değerler kullanılmamalıdır. [GMP-4: 12 -
  "değer sola doğru 0 karakteri ile pad'lenerek 12 karaktere tamamlanır"]

### 13.4 Ücret [GMP-4: Ücret Bilgisi Formatı, s.17]

- **DF-14** - `fare.fareAmount`, **kuruş** (1/100 TL) cinsinden bir tam sayı, >= 0 olmalıdır. [GMP-4:
  13]
- **DF-15** - `fare`, **yalnızca taksimetrede yazan yolculuk ücretini** taşımalıdır. Otoyol, köprü,
  geçiş, ek ücret, servis bedeli vb. dahil edilmemelidir. [GMP-4: 13 - "otoyol, köprü, geçiş, ek ücret,
  servis bedeli vb gibi bilgiler gönderilemez"]

---

## 14. Zaman aşımı ve tekrar gönderim - `TO`

[GMP-4: Zaman Aşımı ve Tekrar Gönderim Kuralları, s.10-12]

- **TO-01** - `TRIP_START`: beklenen cevap `TRIP_START_ACK` **veya** `ERROR`; deneme başına zaman
  aşımı **1000 ms**; **azami 2 tekrar** (toplam <=3 gönderim); tekrar aralığı **1000 ms**. [GMP-4: 9.1
  tablosu; 9.2]
- **TO-02** - `TRIP_END`: beklenen cevap `TRIP_END_ACK` **veya** `ERROR`; deneme başına zaman aşımı
  **120000 ms**; tekrar aralığı **10000 ms**; tabloda azami tekrar sayısı belirtilmemiştir ("-").
  [GMP-4: 9.1 tablosu] (Belirtilmemiş azami tekrar ile §9.3'teki "aynı messageId/seq ile tekrarı
  bırak" çelişir - bkz. OQ-18.)
- **TO-03** - `HEARTBEAT`: beklenen cevap `HEARTBEAT_ACK`; deneme başına zaman aşımı **5000 ms**;
  tablo **azami 1 tekrar** listeler, §9.3 ise "tekrar deneme yapılmaz" der. [GMP-4: 9.1 tablosu; 9.3]
  (Doğrudan çelişki - bkz. OQ-19.)
- **TO-04** - "Azami tekrar sayısı N", ilk gönderimden sonra yapılabilecek N tekrar anlamına gelmelidir
  (yani toplam gönderim <= N+1). [GMP-4: 9.2]
- **TO-05** - Bir istek, beklenen ACK ya da aynı `correlationId` ile dönen bir `ERROR` alındığında
  tamamlanmış sayılmalıdır. [GMP-4: 9; 9.5]
- **TO-06** - `TRIP_START`: azami tekrardan sonra geçerli cevap yoksa -> yolculuk başlatma onaylanmamış
  sayılır, GMP-4 mesajlaşması biter, GMP-3 oturumu yeniden kurulur (SES-03 uyarınca). [GMP-4: 9.3]
- **TO-07** - `TRIP_END`: azami tekrardan sonra geçerli cevap yoksa -> aynı `messageId`/`sequenceNumber`
  ile tekrar denemeyi bırak; yolculuk bitiş işleminin durumu "belirsiz" sayılır; yeniden bağlanıldığında
  aynı `TRIP_END` (aynı `messageId`/`sequenceNumber`) tekrar gönderilebilir. [GMP-4: 9.3]
- **TO-08** - `HEARTBEAT`: zaman aşımı süresince cevap yoksa heartbeat başarısız sayılır (tekrar
  çelişkisi için bkz. TO-03). [GMP-4: 9.3]
- **TO-09** - Zaman aşımı/tekrar değerleri marka/modelden bağımsız olarak standart ve aynı olmalıdır;
  taksimetre bunları değiştirmemelidir. [GMP-4: 9 giriş]

---

## 15. Açık sorular kaydı (dondurmadan önce çözülmelidir)

> Bunlar, GMP-3/GMP-4 kaynağındaki gerçek belirsizlikler, çelişkiler veya eksik tanımlamalar ya da dış
> bağımlılıklardır. Hiçbiri yukarıda sessizce çözülmemiştir. Her biri, GİB ve/veya TMC kütüphane
> üreticisinden bir yanıt gerektirir.

| Kimlik | Soru | Etki | Belirsizliğin kaynağı |
|--------|------|------|-----------------------|
| OQ-01 | 2 baytlık fiziksel uzunluk alanı neyi kapsar (yalnızca veri, veri+CRC, STX/ETX dahil/hariç)? | Yanlışsa çerçeveleyici birlikte çalışmaz. | [GMP-3: 4.4] tablosu konumsal, tanımlı değil. |
| OQ-02 | Hangi CRC-16-CCITT varyantı (poli/başlangıç/refin/refout/xorout)? VE CRC tam olarak hangi bayt aralığını kapsar - yalnızca veri mi, uzunluk+veri mi (2 baytlık uzunluk dahil mi)? | Uyumsuzsa her çerçeve reddedilir. | [GMP-3: 4.4; 4.4.1.2] yalnızca "CRC-16-CCITT" / "STX-ETX arası" der. |
| OQ-03 | "Deneme Sayısı: 3" = toplam 3 gönderim mi, 1 + 3 tekrar mı? | Tekrar gönderim mantığında bir-eksik (off-by-one). | [GMP-3: 4.4] |
| OQ-04 | INIT rassal değerleri: 16 bayt (§5.3 / Tablo 1) mı, 384 bit (Tablo 2) mı? Hangisi normatif? | Yanlış PRF tohumu -> CLOSE doğrulaması başarısız. | [GMP-3: 5.3 vs 5.2 Tablo 2] çelişki. |
| OQ-05 | STMC-imzalı değerin `SHA-384(A‖ExtR‖TMCR)` kesin bayt düzeni/kodlaması (birleştirme sırası, nokta kodlaması). AYRICA: §5.3 adım 5 sade `STMC(A)` yazar, Tablo 1 adım 7 ise özetlenmiş `SHA-384(A‖ExtR‖TMCR)` imzalar - hangisi normatif? | İmza doğrulaması başarısız. | [GMP-3: 5.2 Tablo 1 adım 7 vs 5.3 adım 5] |
| OQ-06 | ECHO mesajı: yapısı, amacı, ne zaman gönderildiği, şifreli mi değil mi. | ECHO uygulanamaz. | [GMP-3: 5.3] adlandırır ama tanımlamaz. |
| OQ-07 | ESP32 Xtensa / ESP-IDF için derlenmiş bir GMP-3 kütüphanesi var mı? Kim sağlar, hangi ABI? | Tüm kripto gereksinimleri için kesin engel (LIB-04). | [GMP-3: 5.2.3] |
| OQ-08 | PRF ayrıntıları: adım başına hangi özet (SHA-256 vs 384), adım başına çıktı uzunlukları, etiket bayt kodlaması, CLOSE şifrelemesinde IV kullanımı, 32 baytlık düz metnin dolgusu. | TMC ile uyum kopar. | [GMP-3: 5.2; 5.2.1] |
| OQ-09 | Güç kesintisi yeniden eşleşme gerektirmiyorsa, oturum anahtarları + sayaç yeniden başlatmada korunur mu, yoksa yeniden bağlanmada (tam eşleşme değil) yeni bir ECDHE mi çalışır? Bir "oturum" ne zaman başlar? | IV/anahtar tekrar kullanımı + replay riski, ya da gereksiz yeniden el sıkışma. | [GMP-3: 5.2.5 vs 5.2.5.1] gerilim. |
| OQ-10 | Bu ESP32'de GMP anahtar materyali için, mevcut şifreli flash bölümlerinden ayrı "güvenli alan" nedir? | Güvenlik duruşu / sertifikasyon. | [GMP-3: 5.2 Tablo 2] |
| OQ-11 | Sertifika geçerliliği (CV-05) ve ISO-8601 zaman damgaları için güvenilir saat kaynağı - RTC mi ağ mı. | Saat hatalıysa sertifika kontrolleri / zaman damgaları yanlış olur. | [GMP-3: 5.2.4 #5; GMP-4 başlık] |
| OQ-12 | Hangi güvenilir kök/ara CA sertifikaları yüklenmeli ve nasıl iletilir/güncellenir? | Kök/ara sertifikalar olmadan zincir doğrulaması (CV-07) imkânsız. | [GMP-3: 5.2.4 #7] |
| OQ-13 | Mevcut uygulamaya bakan BLE yığını ile TMC'ye giden yeni GMP-3 Bluetooth bağlantısı, bu tek ESP32 BLE radyosunda bir arada çalışabilir mi? Classic SPP mi BLE mi? | Mevcut donanımda mimari fizibilite. | Cihaz donanımı; spesifikasyonda ele alınmamış. |
| OQ-14 | Oturum sıfırlama sequenceNumber'ı -> 1 yapar, ancak TRIP_END tekrarı özgün sequenceNumber'ı korumalıdır. Oturumlar-arası bir TRIP_END tekrarının sequenceNumber'ı nasıl geçerli olur? | Yeniden bağlanma boyunca TRIP_END eşgüdümü (idempotency). | [GMP-4: 9.3 vs s.9] çelişki. |
| OQ-15 | `protocolVersion` her örnekte var ve bir hata koduna sahip, ancak başlık alan tablosunda yok. Zorunlu mu? Kesin kuralları? | Başlık şeması bütünlüğü. | [GMP-4: başlık tablosu vs örnekler] |
| OQ-16 | Standart hata-kodu -> aksiyon eşlemesi (ER-06) bozuk bir tablo çıktısından yeniden oluşturuldu. Her satır orijinal DOCX'e karşı teyit edilmeli. | Hata sonrası yanlış davranış. | [GMP-4: s.27-28] çıktı bozulması. |
| OQ-17 | GPS doğruluk alan adı: `accuracyMeters` (metin/örnekler) vs `accuracyMeter` (bir tablo hücresi). | Ad yanlışsa alan reddedilir. | [GMP-4: 10.1 vs 10.2] |
| OQ-18 | TRIP_END azami tekrar sayısı "-"; sınırlı mı sınırsız mı? 120000 ms zaman aşımı + 10000 ms aralık ile etkileşimi. | Tekrar döngüsü sınırları. | [GMP-4: 9.1 vs 9.3] |
| OQ-19 | HEARTBEAT tekrarı: tablo "azami 1 tekrar" der, §9.3 "tekrar yok" der. Hangisi geçerli? | Heartbeat tekrar gönderim mantığı. | [GMP-4: 9.1 vs 9.3] çelişki. |
| OQ-20 | Bluetooth profili: STX/uzunluk/CRC/ETX çerçevelemesi için BLE GATT mı Bluetooth Classic SPP mi? MTU/parçalama kuralları? | İletişim ortamının gerçeklenmesi. | [GMP-3: 4.4] "Bluetooth" der, profil yok. |
| OQ-21 | `tripId`/`messageId` UUID'lerini kim üretir ve cihazda hangi RSÜ kalitesi gerekir? | Tekillik/çakışma garantileri. | [GMP-4] UUID v4 varlığını varsayar. |
| OQ-22 | Bu cihazın ücret modelinin (PCNT darbeleri, tarifeler, dahili işlenen geçiş ücretleri) tek `fareAmount` "yalnızca taksimetre ücreti" alanına eşlenmesi - tam olarak ne hariç tutulur? | Mali tutar doğruluğu. | [GMP-4: 13] iş kuralı. |
| OQ-23 | **KHMAC nerede/nasıl uygulanır?** Anahtar türetilir (KR-07/KR-11) ama kaynak MAC adımını hiç belirtmez: encrypt-then-MAC mı MAC-then-encrypt mi, MAC nereye konur, sequenceNumber'ı doğrular mı. GMP-3 §5.2'nin hem "kripto bütünlük sağlar, CRC yalnızca fiziksel" hem de "mesaj bütünlük kontrolü için CRC kullanılır" demesiyle (GMP3:461 öz-çelişki) birleşir. | **KRİTİK** - kütüphane üreticileri arasında uyum kopuşunu garanti eder; bu olmadan yük bütünlüğü modeli tanımsızdır. | [GMP-3: 5.2; 5.2.1] (3 inceleyicinin tamamı) |
| OQ-24 | GMP3:460, PTMC'yi TMC'nin **"özel anahtarı"** olarak adlandırır; bu, diğer tüm referanslarla çelişir (PTMC = TMC sertifikası / açık anahtar). PTMC'nin yalnızca sertifika/açık anahtar olduğu, asla özel materyal içermediği teyit edilmeli. | Kripto-güven doğruluğu; literal okuma bir özel anahtar sızdırır/bekler. | [GMP-3: 5.2 satır 460 vs 253/490] (Codex, Claude) |
| OQ-25 | **AES-CBC IV kaynağı.** IV, 16 baytlık INIT rassal değeri mi (§5.3 adım 1, "IV oluşturmak için") yoksa PRF zinciri çıktısı mı (KR-11 / Tablo 1 adım 8)? Ve bu INIT rassal değeri IV kaynağı mı, master-secret PRF tohumu mu (KR-10), ikisi birden mi? | **KRİTİK/uyum** - taksimetre ile TMC farklı IV kaynağı seçerse tüm GMP-4 şifreli metni çözülemez ve CLOSE doğrulaması başarısız olur. | [GMP-3: 5.3 adım 1 vs 5.2 PRF zinciri / Tablo 1 adım 8] (Claude) |
| OQ-26 | Fiziksel **ACK/NAK cevap** çerçevesinin kesin bayt düzeni (yalnızca ACK/NAK baytı mı? yoksa `ACK/NAK | CRC | ETX` mi?). GMP-3 tablosu istek bloklarını ACK/NAK cevaplarından ayırır ama çıktı, cevap düzenini bozar. | Yanlış çerçevelenirse fiziksel el sıkışma bozulur. | [GMP-3: 4.4 tablosu] (Gemini) |
| OQ-27 | GMP-3 §5.2.5.1, **TMC'nin istek gönderdiğini ima eden simetrik S/T sayaç modeline** sahiptir, ancak GMP-4 yalnızca taksimetre-kaynaklı istekler tanımlar (TMC -> yalnızca ACK/ERROR). Herhangi bir TMC->taksimetre isteği var mı (ECHO?)? SEQ-07 kalıntı mı? | Sıra/replay modeli doğruluğu; değilse işlevsiz gereksinim. | [GMP-3: 5.2.5.1 vs GMP-4 Mesaj Tipleri] (3 inceleyicinin tamamı) |
| OQ-28 | Şifresiz INIT/KEYREQ/CLOSE eşleşme mesajları 1-999 sıra sayacını tüketir/artırır mı, yoksa eşleşmeden sonra sayaç 0 mıdır ve ilk GMP-4 isteği (TRIP_START) = 1 midir (örneklerin gösterdiği gibi)? | Oturum başında sıra doğrulamasında N-kayma. | [GMP-4: s.9 vs örnekler; GMP-3: 5.2.5.1] (Claude) |
| OQ-29 | Fiziksel **3000 ms / 3-deneme** tekrar gönderimi (TR-07), GMP-4 mesaj-başı zaman aşımlarıyla (özellikle TRIP_START 1000 ms, TO-01) nasıl birleşir? Fiziksel bekleme uygulama zaman aşımını aşar, bu yüzden uygulama zamanlayıcısı, bağlantı katmanı tekrarlarını bitirmeden dolabilir. Bağımsız katmanlar mı? Uygulama zaman aşımı fizikseli kapsar mı? | Çift iletim / erken "onaylanmadı". | [GMP-3: 4.4 vs GMP-4: 9.1] (Gemini, Claude) |
| OQ-30 | **GMP-3 eşleşme aşaması hata cevaplarının** (PR-18, §5.3 adım 8) şifresiz hata kodları için tanımlı biçimi, uzunluğu veya enum değerleri yoktur. Tanımlanmalı. | Eşleşme-hata yönetimi uygulanamaz. | [GMP-3: 5.3 adım 8] (Gemini) |
| OQ-31 | GMP-3 Tablo 2, A, B ve PTMC sertifikasını **"384 bit"** olarak listeler; bu bayt-boyutu olarak imkânsızdır (sıkıştırılmamış P-384 noktası ~97 bayt; X.509 sertifikası çok daha büyük). A, B, PTMC için gerçek azami bayt boyutları teyit edilmeli. | Bellekte yetersiz tahsis / kesilme (kısıtlı MCU'da). | [GMP-3: 5.2 Tablo 2] (Gemini) |
| OQ-32 | `G`, sabit bir değer yerine INIT cevabında; `A` ise KEYREQ'te iletilir. Taksimetre (veya kütüphane, LIB-02), `G`'nin standart secp384r1 taban noktasına eşit ve `A`'nın eğri üzerinde geçerli bir nokta olduğunu teyit etmeli mi? | **BÜYÜK güvenlik** - körü körüne kabul edilirse geçersiz-eğri / küçük-altgrup saldırı yüzeyi. | [GMP-3: 5.3 adım 2,5; PR-08/PR-11] (Claude) |
| OQ-33 | `IGNORE` ERROR.action enum'da tanımlı ama standart hata-kodu tablosunun hiçbir satırında kullanılmaz. Ne zaman döner, yoksa ileride kullanım için mi ayrılmış? | Ölü dal / işlenmeyen durum. | [GMP-4: 18.2 vs Standart Hata Kodları] (Gemini) |
| OQ-34 | `HEARTBEAT_TIMEOUT` hata-kodu tablosunda yer alır (-> TERMINATE_SESSION), ancak HEARTBEAT hiç ERROR almaz (HB-05/ER-01). HEARTBEAT_TIMEOUT taksimetreye hangi kanaldan / ne zaman iletilir (TMC oturumu kapattıktan sonraki ilk istekte mi)? | Heartbeat-hata yönetimi tanımsız. | [GMP-4: 16; 14; 18; Standart Hata Kodları] (Claude) |

---

## 16. İzlenebilirlik matrisi (gereksinim -> kaynak)

| Gereksinim Kimlikleri | GMP-3 kaynağı | GMP-4 kaynağı |
|-----------------------|---------------|---------------|
| SCOPE-01..07 | Genel; Kapsam (4.2); Entegrasyon Yöntemleri (4.3) | Genel; Güvenlik İlkeleri |
| TR-01..09 | 4.4; 4.4.1.2; 4.4.1.3 | - |
| PR-01..18 (PR-01b dahil) | 5.1.1; 5.2 Tablo 1; 5.3 | - |
| LIB-01..04 | 5.2.3; 5.2.5 | - |
| KR-01..15 | 5.2; 5.2.1; Tablo 2; Tablo 1 adım 7-8 | - |
| CV-01..08 | 5.2.4 | - |
| SEQ-01..11 | 5.2.5.1 | İşlem Sıra Numarası (s.9); 9.4 |
| SES-01..06 | 5.2.5 | 9.3; 9.5; 16 |
| MSG-01..12 | - | Genel; Genel Mesaj Zarfı; Ortak Header (s.8-9); Mesaj Tipleri (s.7-8) |
| TS-01..05 | - | 15; 15.1-15.4; 9.1 notu; 14 |
| HB-01..05 | - | 16; 16.1-16.4; 14 |
| TE-01..06 | - | 17; 17.1-17.4; 5; 9.4 |
| AK-01..03 | - | 14 |
| ER-01..07 | - | 18; 18.1-18.5; Standart Hata Kodları (s.27-28); 9.5 |
| DF-01..15 | - | 10; 11; 12; 13 |
| TO-01..09 | 4.4 (yalnızca fiziksel) | 9.1-9.3 |

---

## 17. Kapsam dışı (bu belge)

- TMC (mali cihaz) tarafı gereksinimleri.
- Ethernet / WiFi / RS232 / USB iletişim ortamları ve çerçevelemeleri.
- Uygulama tasarımı, bileşen ayrıştırması, görev planı veya mevcut yazılıma karşı boşluk (gap) analizi.
  (Bu belge, üzerinde anlaşılan türe göre saf bir uyum spesifikasyonudur.)
- TMC'nin dahili mali belge üretimi, e-belge biçimleri ve TMC-MYS sunucu iletişimi.
- Mevcut taksimetre-mobil uygulama BLE GATT / RSA / AES sözleşmesinde değişiklikler.

---

*REQ-tmc-gmp-taximeter-compliance.tr.md sonu (TASLAK v0.2). İngilizce ana belge:
REQ-tmc-gmp-taximeter-compliance.md*
