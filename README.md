# Library-Management-System
# KÜTÜPHANE YÖNETİM SİSTEMİ PROJE RAPORU

Bu proje, bir kütüphanenin kitap stoklarını, üye kayıtlarını ve ödünç alma süreçlerini dijital ortamda yönetmek amacıyla Python ve SQLite kullanılarak geliştirilmiş ilişkisel bir veri tabanı yönetim sistemidir.

---

## 1. Veri Tabanı Mimarisi: 3-Şema Mimarisi (3-Schema Architecture)

Projede kullanılan SQLite veri tabanı mimarisi, verilerin soyutlanması ve bağımsızlığı için ANSI-SPARC 3-Şema Mimarisi standartlarına uygun olarak tasarlanmıştır.

* **Dış Şema (External Schema / View Level):** Kullanıcının terminal ekranında gördüğü arayüzdür. Kullanıcı arka plandaki karmaşık veri yapılarını görmez; sadece önüne gelen `1 - Kitap Ekle`, `2 - Kitapları Listele` gibi menü seçenekleriyle etkileşime girer.
* **Kavramsal Şema (Conceptual Schema / Logical Level):** Veri tabanında hangi verilerin hangi kurallarla tutulduğunu belirleyen mantıksal katmandır. Projede tasarlanan `Kitaplar`, `Uyeler` ve `OduncAlma` tabloları, bu tabloların veri tipleri ve kısıtlamaları (Constraints) kavramsal şemayı oluşturur.
* **İç Şema (Internal Schema / Physical Level):** Verilerin bilgisayar hafızasında fiziksel olarak nasıl saklandığını belirler. SQLite yapısı sayesinde, tüm veri tabanı mimarisi disk üzerinde tek bir fiziksel dosyada binary (ikili) formatta sıkıştırılarak saklanır.

---

## 2. İlişkisel Veri Modeli ve Tablo Tasarımları

Proje kapsamında birbiriyle ilişkili 3 temel tablo kurulmuştur:

### A. Kitaplar Tablosu (`Kitaplar`)
Kütüphanede bulunan kitapların bilgilerini ve anlık stok durumlarını tutar.
* `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Her kitabın benzersiz kimlik numarası.
* `baslik` (TEXT, NOT NULL): Kitabın adı (Boş bırakılamaz).
* `yazar` (TEXT): Kitabın yazarı.
* `yayin_yili` (INTEGER): Kitabın basım yılı.
* `stok_adedi` (INTEGER): Kitabın kütüphanedeki güncel stok miktarı.

### B. Üyeler Tablosu (`Uyeler`)
Kütüphaneye kayıt yaptırarak kitap ödünç alan kişilerin bilgilerini saklar.
* `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Her üyenin benzersiz üye numarası.
* `ad` (TEXT) & `soyad` (TEXT): Üyenin isim bilgileri.
* `eposta` (TEXT, UNIQUE): Üyenin iletişim adresi. Veri tutarlılığı için `UNIQUE` kısıtlaması eklenmiştir; aynı e-posta ile ikinci bir üye kaydedilemez.
* `kayit_tarihi` (TEXT): Üyenin sisteme dahil olduğu anlık tarih bilgisi.

### C. Ödünç Alma Tablosu (`OduncAlma`)
Kitaplar ve Üyeler tablolarını birbirine bağlayan, kütüphane hareketlerinin tutulduğu **ilişki (junction) tablosudur**.
* `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): İşlem takip numarası.
* `kitap_id` (INTEGER, FOREIGN KEY): Ödünç alınan kitabın ID'si. `Kitaplar(id)` tablosuna bağlıdır.
* `uye_id` (INTEGER, FOREIGN KEY): Kitabı alan üyenin ID'si. `Uyeler(id)` tablosuna bağlıdır.
* `odunc_tarihi` (TEXT): Kitabın teslim alındığı tarih.
* `teslim_tarihi` (TEXT): Kitap iade edildiğinde doldurulur. Kitap henüz üyedeyse bu alan `NULL` (boş) kalır.

---

## 3. Gelişmiş SQL Sorguları ve Fonksiyonel Mantık

### A. İlişkisel Birleştirme (JOIN) Sorgusu
Sistemde aktif olarak hangi kitabın hangi üye tarafından ödünç alındığını listelemek için `OduncAlma` tablosu merkez alınarak `Kitaplar` ve `Uyeler` tabloları **INNER JOIN** ile birleştirilmiştir. Ayrıca metin birleştirme (`||`) operatörü kullanılarak ad ve soyad tek bir kolon haline getirilmiştir:
---

## 4. Test Durumları (Test Cases)

Sistemdeki fonksiyonların veri tutarlılığını ve iş mantığını doğru şekilde yürüttüğünü doğrulamak amacıyla aşağıdaki test senaryoları CLI (Komut Satırı) üzerinden simüle edilmiştir:

| Test ID | Test Edilen Fonksiyon / Senaryo | Girdi (Input) | Beklenen Sonuç (Expected Output) | Durum (Status) |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Yeni Benzersiz Üye Kaydı | `ad="Rümeysa"`, `soyad="Görmez"`, `eposta="rumeysa@mail.com"` | Üye başarıyla eklendi uyarısı ve yeni bir ID üretilmesi. | **BAŞARILI** |
| **TC-02** | Mükerrer E-posta Kontrolü (UNIQUE Constraint) | Aynı e-posta adresiyle (`rumeysa@mail.com`) ikinci bir üye kaydı denemesi. | `IntegrityError: UNIQUE constraint failed` uyarısının yakalanması ve kaydın reddedilmesi. | **BAŞARILI** |
| **TC-03** | Geçerli Kitap Ödünç Verme & Stok Azaltma | Stok adedi `> 0` olan bir kitabın bir üyeye ödünç verilmesi. | `OduncAlma` tablosuna kayıt eklenmesi ve ilgili kitabın stok adedinin `1` azaltılması. | **BAŞARILI** |
| **TC-04** | Stokta Olmayan Kitabın Ödünç Verilmesi | Stok adedi `0` olan bir kitabın ödünç verilmeye çalışılması. | Sistem tarafından "Bu kitap stokta yok" uyarısının basılması ve işlemin iptal edilmesi. | **BAŞARILI** |
| **TC-05** | Kitap İade Etme (Teslim Tarihi Güncelleme) | Ödünç alınan bir kitabın geri getirilmesi. | `OduncAlma` tablosundaki `teslim_tarihi` alanının güncellenmesi ve kitap stoğunun `1` artırılması. | **BAŞARILI** |

```sql
SELECT o.id, k.baslik, (u.ad || ' ' || u.soyad) AS uye_ad_soyad, o.odunc_tarihi 
FROM OduncAlma o 
JOIN Kitaplar k ON o.kitap_id = k.id 
JOIN Uyeler u ON o.uye_id = u.id 
WHERE o.teslim_tarihi IS NULL;
