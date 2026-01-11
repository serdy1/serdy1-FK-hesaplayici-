#!/usr/bin/env python3
"""
pe_calculator.py
Basit CLI: BIST hisseleri için F/K (P/E) hesaplar.
Kullanım örnekleri:
  python pe_calculator.py --tickers GARAN.IS AKBNK.IS
  python pe_calculator.py --file tickers.txt --output results.csv
  python pe_calculator.py --csv input.csv --ticker-col symbol --output results.csv
"""
import argparse
import sys
from typing import List, Dict, Any
import pandas as pd
import yfinance as yf
import time

def fetch_pe_for_ticker(ticker: str) -> Dict[str, Any]:
    """Bir ticker için fiyat, EPS ve P/E değerlerini alır (mümkün olduğunca güvenli)."""
    result = {"ticker": ticker, "price": None, "trailingEps": None, "forwardEps": None,
              "trailingPE": None, "forwardPE": None, "notes": ""}
    try:
        t = yf.Ticker(ticker)
        info = {}
        # Bazı yfinance versiyonları .info yavaş olabilir; .get_info() veya .fast_info alternatif olabilir
        try:
            info = t.info or {}
        except Exception:
            try:
                info = t.get_info() or {}
            except Exception:
                info = {}
        # Price: öncelikle info içinden, yoksa history ile al
        price = info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            hist = t.history(period="5d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]
        result["price"] = float(price) if price is not None else None

        result["trailingEps"] = info.get("trailingEps")
        result["forwardEps"] = info.get("forwardEps")
        result["trailingPE"] = info.get("trailingPE")
        result["forwardPE"] = info.get("forwardPE")

        # Hesapla (info'da yoksa) — EPS varsa price / eps
        if result["trailingPE"] is None and result["price"] is not None and result["trailingEps"]:
            try:
                eps = float(result["trailingEps"])
                if eps != 0:
                    result["trailingPE"] = round(result["price"] / eps, 6)
            except Exception:
                pass
        if result["forwardPE"] is None and result["price"] is not None and result["forwardEps"]:
            try:
                eps = float(result["forwardEps"])
                if eps != 0:
                    result["forwardPE"] = round(result["price"] / eps, 6)
            except Exception:
                pass

        # Not: EPS 0 veya None durumları
        if (result["trailingEps"] in (None, 0)) and (result["trailingPE"] in (None,)):
            result["notes"] += "Trailing EPS yok/0; "
        if (result["forwardEps"] in (None, 0)) and (result["forwardPE"] in (None,)):
            result["notes"] += "Forward EPS yok/0; "
    except Exception as e:
        result["notes"] = f"Error: {e}"
    return result

def load_tickers_from_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    # Satırlarda virgülle ayrılmış de olabilir
    tickers = []
    for l in lines:
        parts = [p.strip() for p in l.split(",") if p.strip()]
        tickers.extend(parts)
    return tickers

def main(argv=None):
    parser = argparse.ArgumentParser(description="BIST hisseleri için F/K (P/E) hesaplayıcı")
    parser.add_argument("--tickers", nargs="+", help="Ticker listesi (ör. GARAN.IS AKBNK.IS)")
    parser.add_argument("--file", help="Her satırda bir ticker olan dosya")
    parser.add_argument("--csv", help="CSV dosyası (ticker sütunu belirtin)")
    parser.add_argument("--ticker-col", default="ticker", help="CSV içindeki ticker sütun ismi (varsayılan: ticker)")
    parser.add_argument("--output", help="Çıktı CSV dosyası (opsiyonel)")
    parser.add_argument("--sleep", type=float, default=0.5, help="Her istek arasında bekleme (saniye) — API throttling için")
    args = parser.parse_args(argv)

    tickers = []
    if args.tickers:
        tickers.extend(args.tickers)
    if args.file:
        tickers.extend(load_tickers_from_file(args.file))
    if args.csv:
        df_in = pd.read_csv(args.csv)
        if args.ticker_col not in df_in.columns:
            print(f"CSV içinde '{args.ticker_col}' sütunu bulunamadı.", file=sys.stderr)
            sys.exit(1)
        tickers.extend(df_in[args.ticker_col].astype(str).tolist())

    if not tickers:
        print("Hiç ticker sağlanmadı. --tickers ya da --file ya da --csv kullanın.", file=sys.stderr)
        sys.exit(1)

    # Temizle ve benzersiz yap
    tickers = [t.strip() for t in tickers if t and t.strip()]
    tickers = list(dict.fromkeys(tickers))  # sırayı koruyarak unique

    results = []
    for i, tk in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] İndiriliyor: {tk} ...")
        res = fetch_pe_for_ticker(tk)
        results.append(res)
        time.sleep(args.sleep)

    df = pd.DataFrame(results)
    # Düzenli sütun sırası
    cols = ["ticker", "price", "trailingEps", "trailingPE", "forwardEps", "forwardPE", "notes"]
    df = df[cols]

    if args.output:
        df.to_csv(args.output, index=False, encoding="utf-8-sig")
        print(f"Sonuçlar kaydedildi: {args.output}")
    else:
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()
