import streamlit as st
import pandas as pd
import yfinance as yf
import time

# Sayfa yapılandırmasını ayarla (Bu, betikteki ilk Streamlit komutu olmalı)
st.set_page_config(
    page_title="BIST F/K (P/E) Oranı Hesaplayıcı",
    page_icon="📊",
    layout="wide"
)

def fetch_pe(ticker):
    """Belirtilen hisse senedi için F/K ve diğer ilgili verileri çeker."""
    out = {
        "Hisse": ticker, "Fiyat": None, "Trailing EPS": None, "Trailing F/K": None,
        "Forward EPS": None, "Forward F/K": None, "Notlar": ""
    }
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}

        price = info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            hist = t.history(period="5d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]

        out["Fiyat"] = price
        out["Trailing EPS"] = info.get("trailingEps")
        out["Forward EPS"] = info.get("forwardEps")
        out["Trailing F/K"] = info.get("trailingPE")
        out["Forward F/K"] = info.get("forwardPE")

        # F/K oranlarını manuel olarak hesapla (eğer yfinance'den gelmezse)
        if out["Trailing F/K"] is None and price and out["Trailing EPS"]:
            if out["Trailing EPS"] != 0:
                out["Trailing F/K"] = price / out["Trailing EPS"]

        if out["Forward F/K"] is None and price and out["Forward EPS"]:
            if out["Forward EPS"] != 0:
                out["Forward F/K"] = price / out["Forward EPS"]

        if not out["Trailing EPS"]:
            out["Notlar"] += "Trailing EPS verisi yok/0. "
        if not out["Forward EPS"]:
            out["Notlar"] += "Forward EPS verisi yok/0. "

    except Exception as e:
        out["Notlar"] = f"Veri alınırken hata oluştu: {str(e)}"
    return out

# --- ARAYÜZ ---

# Kenar Çubuğu (Sidebar)
st.sidebar.header("Ayarlar")
tickers_input = st.sidebar.text_area(
    "Hisse Kodları (Virgülle ayırarak girin)",
    "GARAN.IS, AKBNK.IS, TUPRS.IS, EREGL.IS"
)
sleep = st.sidebar.number_input(
    "İstekler Arası Bekleme (saniye)",
    value=0.5, min_value=0.0, max_value=5.0, step=0.1,
    help="Yahoo Finance'a aşırı yüklenmeyi önlemek için istekler arasına küçük bir gecikme ekler."
)

# Ana Sayfa
st.title("📊 BIST Fiyat/Kazanç (F/K) Oranı Hesaplayıcı")
st.markdown("---")

if st.sidebar.button("Hesapla", type="primary"):
    if not tickers_input.strip():
        st.error("Lütfen en az bir hisse kodu girin.")
    else:
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

        with st.spinner(f"{len(tickers)} adet hisse için veriler çekiliyor, lütfen bekleyin..."):
            results = []
            for t in tickers:
                results.append(fetch_pe(t))
                time.sleep(sleep)

            df = pd.DataFrame(results)

        st.success("Hesaplama tamamlandı!")

        # Sonuçları göster
        st.subheader("Hesaplama Sonuçları")

        # Sayısal sütunları formatla
        df_display = df.style.format({
            "Fiyat": "{:,.2f} ₺",
            "Trailing EPS": "{:,.2f}",
            "Trailing F/K": "{:,.2f}",
            "Forward EPS": "{:,.2f}",
            "Forward F/K": "{:,.2f}"
        }, na_rep="-") # NaN değerler için "-" göster

        st.dataframe(df_display) # `use_container_width` artık varsayılan davranış, ancak `column_config` ile daha fazla özelleştirilebilir

        # CSV indirme butonu
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Sonuçları CSV Olarak İndir",
            data=csv,
            file_name="fk_sonuclari.csv",
            mime="text/csv",
        )
else:
    st.info("Hesaplamak istediğiniz hisse kodlarını soldaki menüye girip 'Hesapla' butonuna tıklayın.")

st.markdown("---")
st.caption("Veriler Yahoo Finance üzerinden sağlanmaktadır ve gecikmeli olabilir. Bu uygulama yatırım tavsiyesi niteliği taşımaz.")
