import sqlite3
from datetime import datetime

DB_NAME = "kutuphane.db"

def baglanti_kur():
    """Veri tabanina baglanir ve baglanti nesnesini doner."""
    return sqlite3.connect(DB_NAME)

def tablolari_olustur():
    """Uygulama ilk calistiginda gerekli 3 temel tabloyu otomatik olusturur."""
    conn = baglanti_kur()
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS Kitaplar (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT NOT NULL, yazar TEXT, yayin_yili INTEGER, stok_adedi INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Uyeler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, soyad TEXT, eposta TEXT UNIQUE, kayit_tarihi TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS OduncAlma (id INTEGER PRIMARY KEY AUTOINCREMENT, kitap_id INTEGER, uye_id INTEGER, odunc_tarihi TEXT, teslim_tarihi TEXT, FOREIGN KEY (kitap_id) REFERENCES Kitaplar(id), FOREIGN KEY (uye_id) REFERENCES Uyeler(id))")
    
    conn.commit()
    conn.close()

# ==========================================
# 1. KITAP CRUD ISLEMLERI
# ==========================================

def kitap_ekle(baslik, yazar, yayin_yili, stok_adedi):
    conn = baglanti_kur()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Kitaplar (baslik, yazar, yayin_yili, stok_adedi) VALUES (?, ?, ?, ?)", (baslik, yazar, yayin_yili, stok_adedi))
        conn.commit()
        print(f"\n[BASARILI] '{baslik}' kitabi sisteme eklendi.")
    except Exception as e:
        print(f"\nHata: {e}")
    finally:
        conn.close()

def kitaplari_listele():
    conn = baglanti_kur()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Kitaplar")
    kitaplar = cursor.fetchall()
    conn.close()
    return kitaplar

# ==========================================
# 2. UYE CRUD ISLEMLERI
# ==========================================

def uye_ekle(ad, soyad, eposta):
    conn = baglanti_kur()
    cursor = conn.cursor()
    kayit_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("INSERT INTO Uyeler (ad, soyad, eposta, kayit_tarihi) VALUES (?, ?, ?, ?)", (ad, soyad, eposta, kayit_tarihi))
        conn.commit()
        print(f"\n[BASARILI] Uye '{ad} {soyad}' sisteme kaydedildi.")
    except sqlite3.IntegrityError:
        print(f"\nHata: '{eposta}' e-posta adresi zaten baska bir uyeye ait!")
    except Exception as e:
        print(f"\nHata: {e}")
    finally:
        conn.close()

def uyeleri_listele():
    conn = baglanti_kur()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Uyeler")
    uyeler = cursor.fetchall()
    conn.close()
    return uyeler

# ==========================================
# 3. ODUNC ALMA VE IADE ISLEMLERI
# ==========================================

def kitap_odunc_ver(kitap_id, uye_id):
    conn = baglanti_kur()
    cursor = conn.cursor()
    
    cursor.execute("SELECT baslik, stok_adedi FROM Kitaplar WHERE id = ?", (kitap_id,))
    kitap = cursor.fetchone()
    
    if not kitap:
        print("\nHata: Belirtilen ID'ye sahip bir kitap bulunamadi!")
        conn.close()
        return
        
    kitap_adi, mevcut_stok = kitap[0], kitap[1]
    
    if mevcut_stok <= 0:
        print(f"\nHata: '{kitap_adi}' su an stokta yok, odunc verilemez!")
        conn.close()
        return
        
    odunc_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("INSERT INTO OduncAlma (kitap_id, uye_id, odunc_tarihi, teslim_tarihi) VALUES (?, ?, ?, NULL)", (kitap_id, uye_id, odunc_tarihi))
        cursor.execute("UPDATE Kitaplar SET stok_adedi = stok_adedi - 1 WHERE id = ?", (kitap_id,))
        conn.commit()
        print(f"\n[BASARILI] '{kitap_adi}' odunc verildi. Kalan Stok: {mevcut_stok - 1}")
    except Exception as e:
        print(f"\nHata: {e}")
    finally:
        conn.close()

def kitap_iade_al(odunc_id):
    conn = baglanti_kur()
    cursor = conn.cursor()
    
    cursor.execute("SELECT kitap_id, teslim_tarihi FROM OduncAlma WHERE id = ?", (odunc_id,))
    kayit = cursor.fetchone()
    
    if not kayit:
        print("\nHata: Boyle bir odunc alma kaydi bulunamadi!")
        conn.close()
        return
        
    kitap_id, teslim_tarihi = kayit[0], kayit[1]
    
    if teslim_tarihi is not None:
        print("\nHata: Bu kitap zaten daha once iade edilmis!")
        conn.close()
        return
        
    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("UPDATE OduncAlma SET teslim_tarihi = ? WHERE id = ?", (su_an, odunc_id))
        cursor.execute("UPDATE Kitaplar SET stok_adedi = stok_adedi + 1 WHERE id = ?", (kitap_id,))
        conn.commit()
        print("\n[BASARILI] Kitap iade alindi ve stok guncellendi.")
    except Exception as e:
        print(f"\nHata: {e}")
    finally:
        conn.close()

def aktif_odunc_listele():
    conn = baglanti_kur()
    cursor = conn.cursor()
    query = "SELECT o.id, k.baslik, (u.ad || ' ' || u.soyad), o.odunc_tarihi FROM OduncAlma o JOIN Kitaplar k ON o.kitap_id = k.id JOIN Uyeler u ON o.uye_id = u.id WHERE o.teslim_tarihi IS NULL"
    cursor.execute(query)
    sonuclar = cursor.fetchall()
    conn.close()
    return sonuclar

# ==========================================
# 4. KULLANICI ARAYUZU (KONSOL MENUSU)
# ==========================================

def ana_menu():
    tablolari_olustur()
    
    while True:
        print("\n" + "="*40)
        print("    KUTUPHANE YONETIM SISTEMI MENUSU    ")
        print("="*40)
        print("1 - Yeni Kitap Ekle")
        print("2 - Kitaplari Listele")
        print("3 - Yeni Uye Kaydet")
        print("4 - Uyeleri Listele")
        print("5 - Kitap Odunc Ver")
        print("6 - Kitap Iade Al")
        print("7 - Aktif Odunc Listesi")
        print("0 - Cikis")
        print("="*40)
        
        secim = input("Lutfen bir islem seciniz (0-7): ")
        
        if secim == "1":
            baslik = input("Kitap Adi: ")
            yazar = input("Yazar: ")
            yayin_yili = int(input("Yayin Yili: "))
            stok = int(input("Stok Adedi: "))
            kitap_ekle(baslik, yazar, yayin_yili, stok)
            
        elif secim == "2":
            print("\n--- KITAP LISTESI ---")
            kitaplar = kitaplari_listele()
            for k in kitaplar:
                print(f"ID: {k[0]} | Kitap: {k[1]} | Yazar: {k[2]} | Yil: {k[3]} | Stok: {k[4]}")
                
        elif secim == "3":
            ad = input("Uye Adi: ")
            soyad = input("Uye Soyadi: ")
            eposta = input("E-posta Adresi: ")
            uye_add = uye_ekle(ad, soyad, eposta)
            
        elif secim == "4":
            print("\n--- UYE LISTESI ---")
            uyeler = uyeleri_listele()
            for u in uyeler:
                print(f"ID: {u[0]} | Isim: {u[1]} {u[2]} | E-posta: {u[3]} | Kayit Tarihi: {u[4]}")
                
        elif secim == "5":
            print("\n--- KITAP ODUNC VERME ---")
            kitap_id = int(input("Odunc verilecek Kitap ID: "))
            uye_id = int(input("Odunc alacak Uye ID: "))
            kitap_odunc_ver(kitap_id, uye_id)
            
        elif secim == "6":
            print("\n--- KITAP IADE ALMA ---")
            odunc_id = int(input("Iade edilecek Odunc ID: "))
            kitap_iade_al(odunc_id)
            
        elif secim == "7":
            print("\n--- AKTIF ODUNC ALINAN KITAPLAR ---")
            aktifler = aktif_odunc_listele()
            for o in aktifler:
                print(f"Odunc ID: {o[0]} | Kitap: {o[1]} | Uye: {o[2]} | Odunc Tarihi: {o[3]}")
                
        elif secim == "0":
            print("\nSistemden cikiliyor... Iyi gunler!")
            break
        else:
            print("\nGecersiz bir secim yaptiniz. Lutfen tekrar deneyin.")

if __name__ == "__main__":
    ana_menu()