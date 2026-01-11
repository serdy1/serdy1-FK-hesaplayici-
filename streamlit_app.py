import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.title("BIST Hisseleri için F/K (P/E) Hesaplayıcı")

tickers_input = st.text_input("Tickers (virgülle ayrılmış, örn: GARAN.IS, AKBNK.IS):")
sleep = st.number_input("İstekler arası bekleme (saniye)", value=0.5, min_value=0.0, step=0.1)

def fetch_pe(ticker):
    out = {"ticker": ticker, "price": None, "trailingEps": None, "trailingPE": None,
           "forwardEps": None, "forwardPE": None, "notes": ""}
    try:
        t = yf.Ticker(ticker)
        try:
            info = t.info or {}
        except Exception:
            try:
                info = t.get_info() or {}
            except Exception:
                info = {}
        price = info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            hist = t.history(period="5d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]
        out["price"] = float(price) if price is not None else None
        out["trailingEps"] = info.get("trailingEps")
        out["forwardEps"] = info.get("forwardEps")
        out["trailingPE"] = info.get("trailingPE")
        out["forwardPE"] = info.get("forwardPE")
        if out["trailingPE"] is None and out["price"] is not None and out["trailingEps"]:
            try:
                eps = float(out["trailingEps"])
                if eps != 0:
                    out["trailingPE"] = round(out["price"] / eps, 6)
            except Exception:
                pass
        if out["forwardPE"] is None and out["price"] is not None and out["forwardEps"]:
            try:
                eps = float(out["forwardEps"])
                if eps != 0:
                    out["forwardPE"] = round(out["price"] / eps, 6)
            except Exception:
                pass
        if (out["trailingEps"] in (None, 0)) and (out["trailingPE"] in (None,)):
            out["notes"] += "Trailing EPS yok/0; "
        if (out["forwardEps"] in (None, 0)) and (out["forwardPE"] in (None,)):
            out["notes"] += "Forward EPS yok/0; "
    except Exception as e:
        out["notes"] = str(e)
    return out

if st.button("Hesapla"):
    if not tickers_input.strip():
        st.error("Lütfen en az bir ticker girin.")
    else:
        tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
        results = []
        progress = st.progress(0)
        for i, t in enumerate(tickers, 1):
            progress.progress(int(i/len(tickers)*100))
            results.append(fetch_pe(t))
            time.sleep(sleep)
        df = pd.DataFrame(results)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Sonuçları CSV indir", csv, "pe_results.csv", "text/csv")
