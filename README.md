# BIST F/K (P/E) Hesaplayıcı

Bu proje, Borsa İstanbul (BIST) hisseleri için Fiyat / Kazanç (F/K veya P/E) oranını hesaplamak için iki örnek uygulama içerir:
- CLI: `pe_calculator.py`
- Web arayüzü (Streamlit): `streamlit_app.py`

Not: Veriler Yahoo Finance (yfinance) üzerinden alınır. BIST hisseleri için Yahoo sembolleri genelde `.IS` sonekli kullanılır (ör. `GARAN.IS`, `AKBNK.IS`).

## Kurulum
1. Python 3.8+ kurulu olduğundan emin olun.
2. Sanal ortam oluşturup aktif edin (opsiyonel):
   - python -m venv venv
   - source venv/bin/activate  (Windows: venv\Scripts\activate)
3. Gerekli paketleri yükleyin:
   - pip install -r requirements.txt

## CLI kullanım
Tek bir veya birden fazla ticker ile:
```
python pe_calculator.py --tickers GARAN.IS AKBNK.IS
```

Dosyadan oku:
```
python pe_calculator.py --file tickers.txt --output results.csv
```
CSV'den oku (CSV içinde ticker sütunu varsa):
```
python pe_calculator.py --csv input.csv --ticker-col symbol --output results.csv
```

Çıktı CSV'ye kaydedilmezse sonuç konsola yazdırılır.

## Streamlit arayüzü
Çalıştır:
```
streamlit run streamlit_app.py
```
Tarayıcıda açılan arayüzde tickers kutusuna virgülle ayrılmış ticker listesi girin (örn: `GARAN.IS, AKBNK.IS`) ve Hesapla'ya tıklayın.

## Önemli notlar / kısıtlar
- Yahoo Finance verileri eksik veya gecikmeli olabilir. Kurumsal/ayrıntılı finansal tablolar için KAP (Kamuyu Aydınlatma Platformu) veya yetkili veri sağlayıcıları kullanılmalıdır.
- EPS bazen 0 veya negatif olabilir; bu durumlarda P/E anlamsız olacaktır (script not alanına bunu yazar).
- API çağrılarında throttling olabileceği için `--sleep` parametresi ile isteklere bekleme eklenebilir.
- Hisseleri Yahoo'da doğru sembolle girin: BIST için genelde `.IS` ekleyin.

İsterseniz:
- Doğrudan KAP veya hisse bazlı mali tablolardan TTM EPS çekme (daha kesin) ekleyebilirim.
- Excel/Google Sheets ile entegrasyon veya otomatik günlük raporlama script'i oluşturabilirim.
