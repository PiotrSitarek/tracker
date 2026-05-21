import yfinance as yf
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

PORTFOLIO = [
    {"name": "Nutrien",                   "ticker": "NTR",          "currency": "USD"},
    {"name": "Kazatomprom",               "ticker": "KAP.L",        "currency": "GBp"},
    {"name": "Cameco",                    "ticker": "CCJ",          "currency": "USD"},
    {"name": "Energy Fuels",              "ticker": "UUUU",         "currency": "USD"},
    {"name": "Chevron",                   "ticker": "CVX",          "currency": "USD"},
    {"name": "Global Infrastructure ETF", "ticker": "IDIN.L",       "currency": "GBp"},
    {"name": "Equinor",                   "ticker": "EQNR",         "currency": "USD"},
    {"name": "Exxon Mobil",               "ticker": "XOM",          "currency": "USD"},
    {"name": "Dywidenda Plus ETF",        "ticker": "ETFBDIVPL.WA", "currency": "PLN"},
    {"name": "Enbridge",                  "ticker": "ENB",          "currency": "USD"},
    {"name": "S&P 500 Energy ETF",        "ticker": "IUES.L",       "currency": "GBp"},
    {"name": "MSCI World Energy ETF",     "ticker": "XDW0.DE",      "currency": "EUR"},
    {"name": "TC Energy",                 "ticker": "TRP",          "currency": "USD"},
    {"name": "Targa Resources",           "ticker": "TRGP",         "currency": "USD"},
    {"name": "Rio Tinto",                 "ticker": "RIO.L",        "currency": "GBp"},
    {"name": "BHP Group",                 "ticker": "BHP.L",        "currency": "GBp"},
    {"name": "Talen Energy",              "ticker": "TLN",          "currency": "USD"},
    {"name": "Vistra Energy",             "ticker": "VST",          "currency": "USD"},
    {"name": "Constellation Energy",      "ticker": "CEG",          "currency": "USD"},
    {"name": "ServiceNow",                "ticker": "NOW",          "currency": "USD"},
    {"name": "Freeport-McMoRan",          "ticker": "FCX",          "currency": "USD"},
]

def fetch_stock_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="6mo")

        if hist is None or hist.empty:
            return None

        current_price = hist["Close"].iloc[-1]
        prev_close    = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
        week_ago      = hist["Close"].iloc[-6]  if len(hist) > 5  else hist["Close"].iloc[0]
        month_ago     = hist["Close"].iloc[-22] if len(hist) > 21 else hist["Close"].iloc[0]
        high_52w      = hist["High"].max()
        low_52w       = hist["Low"].min()

        change_day   = ((current_price - prev_close) / prev_close) * 100
        change_week  = ((current_price - week_ago)   / week_ago)   * 100
        change_month = ((current_price - month_ago)  / month_ago)  * 100
        from_52h     = ((current_price - high_52w)   / high_52w)   * 100

        if len(hist) >= 50:
            sma20 = hist["Close"].tail(20).mean()
            sma50 = hist["Close"].tail(50).mean()
            if sma20 > sma50 * 1.02:
                trend, trend_class = "↑ Wzrostowy", "up"
            elif sma20 < sma50 * 0.98:
                trend, trend_class = "↓ Spadkowy", "down"
            else:
                trend, trend_class = "→ Boczny", "side"
        else:
            trend, trend_class = "— Brak danych", "side"

        closes = hist["Close"].tail(60).tolist()
        dates  = [str(d.date()) for d in hist.index.tail(60)]

        return {
            "price":        round(float(current_price), 2),
            "change_day":   round(float(change_day), 2),
            "change_week":  round(float(change_week), 2),
            "change_month": round(float(change_month), 2),
            "high_52w":     round(float(high_52w), 2),
            "low_52w":      round(float(low_52w), 2),
            "from_52h":     round(float(from_52h), 2),
            "trend":        trend,
            "trend_class":  trend_class,
            "chart_closes": closes,
            "chart_dates":  dates,
        }
    except Exception as e:
        print(f"  BŁĄD {ticker_symbol}: {e}")
        return None


def fetch_news(company_name, ticker_symbol):
    query = f"{company_name} stock".replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            tree = ET.parse(resp)
            root = tree.getroot()
            channel = root.find("channel")
            if channel is None:
                return items
            for item in channel.findall("item")[:3]:
                title = item.findtext("title", "")
                link  = item.findtext("link", "#")
                pub   = item.findtext("pubDate", "")
                try:
                    dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z")
                    pub_fmt = dt.strftime("%d.%m.%Y")
                except:
                    pub_fmt = pub[:16] if pub else ""
                items.append({"title": title, "link": link, "date": pub_fmt})
    except Exception as e:
        print(f"  Newsy {company_name}: {e}")
    return items


def generate_html(portfolio_data):
    generated_at = datetime.utcnow().strftime("%d.%m.%Y %H:%M UTC")

    def color(val):
        if val > 0: return "positive"
        if val < 0: return "negative"
        return "neutral"

    def arrow(val):
        if val > 0: return "▲"
        if val < 0: return "▼"
        return "–"

    cards_html = ""
    for item in portfolio_data:
        d   = item["data"]
        n   = item["name"]
        t   = item["ticker"]
        cur = item["currency"]
        news = item["news"]

        if d is None:
            cards_html += f"""
            <div class="card error">
                <div class="card-header">
                    <span class="name">{n}</span>
                    <span class="ticker">{t}</span>
                </div>
                <p class="err-msg">⚠️ Brak danych — ticker niedostępny</p>
            </div>"""
            continue

        closes = d["chart_closes"]
        if closes and len(closes) > 1:
            mn, mx = min(closes), max(closes)
            rng = mx - mn if mx != mn else 1
            pts = []
            w, h = 200, 50
            for i, c in enumerate(closes):
                x = int(i / (len(closes) - 1) * w)
                y = int(h - ((c - mn) / rng) * (h - 4) - 2)
                pts.append(f"{x},{y}")
            polyline = " ".join(pts)
            tc = "#22c55e" if d["trend_class"] == "up" else ("#ef4444" if d["trend_class"] == "down" else "#94a3b8")
            sparkline = f'<svg class="sparkline" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><polyline points="{polyline}" fill="none" stroke="{tc}" stroke-width="2"/></svg>'
        else:
            sparkline = ""

        news_html = ""
        for nw in news:
            news_html += f'<a href="{nw["link"]}" target="_blank" class="news-item"><span class="news-date">{nw["date"]}</span> {nw["title"]}</a>'
        if not news_html:
            news_html = '<span class="no-news">Brak newsów</span>'

        cd, cw, cm, f52 = d["change_day"], d["change_week"], d["change_month"], d["from_52h"]

        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="name">{n}</span>
                    <span class="ticker">{t}</span>
                </div>
                <div class="price-block">
                    <span class="price">{d['price']:,.2f} <small>{cur}</small></span>
                    <span class="badge {color(cd)}">{arrow(cd)} {abs(cd):.2f}% dziś</span>
                </div>
            </div>
            {sparkline}
            <div class="stats-row">
                <div class="stat"><label>Tydzień</label><span class="{color(cw)}">{arrow(cw)} {abs(cw):.2f}%</span></div>
                <div class="stat"><label>Miesiąc</label><span class="{color(cm)}">{arrow(cm)} {abs(cm):.2f}%</span></div>
                <div class="stat"><label>Od 52W max</label><span class="{color(f52)}">{f52:.2f}%</span></div>
                <div class="stat"><label>52W zakres</label><span class="neutral">{d['low_52w']:,.2f} – {d['high_52w']:,.2f}</span></div>
            </div>
            <div class="trend-row">Trend: <span class="trend {d['trend_class']}">{d['trend']}</span></div>
            <div class="news-block">
                <div class="news-title">📰 Newsy</div>
                {news_html}
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Portfolio Tracker</title>
<style>
  :root {{
    --bg:#0f172a; --surface:#1e293b; --border:#334155; --text:#e2e8f0;
    --muted:#94a3b8; --positive:#22c55e; --negative:#ef4444; --neutral:#94a3b8; --accent:#38bdf8;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;padding:1rem}}
  header{{text-align:center;padding:1.5rem 0 1rem}}
  header h1{{font-size:1.6rem;color:var(--accent)}}
  header p{{color:var(--muted);font-size:.85rem;margin-top:.3rem}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1rem;max-width:1400px;margin:0 auto}}
  .card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;display:flex;flex-direction:column;gap:.7rem}}
  .card.error{{border-color:var(--negative);opacity:.7}}
  .card-header{{display:flex;justify-content:space-between;align-items:flex-start;gap:.5rem}}
  .name{{font-size:1rem;font-weight:600}}
  .ticker{{display:inline-block;background:#0f172a;color:var(--accent);border-radius:6px;padding:2px 7px;font-size:.75rem;margin-top:3px}}
  .price{{font-size:1.25rem;font-weight:700}}
  .price small{{font-size:.7rem;color:var(--muted)}}
  .price-block{{text-align:right}}
  .badge{{display:inline-block;padding:2px 8px;border-radius:6px;font-size:.8rem;font-weight:600;margin-top:4px}}
  .badge.positive{{background:rgba(34,197,94,.15);color:var(--positive)}}
  .badge.negative{{background:rgba(239,68,68,.15);color:var(--negative)}}
  .badge.neutral{{background:rgba(148,163,184,.15);color:var(--neutral)}}
  .sparkline{{width:100%;height:50px;display:block}}
  .stats-row{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:.5rem}}
  .stat{{background:#0f172a;border-radius:8px;padding:.4rem .5rem;text-align:center}}
  .stat label{{display:block;font-size:.65rem;color:var(--muted);margin-bottom:2px}}
  .stat span{{font-size:.85rem;font-weight:600}}
  .positive{{color:var(--positive)}} .negative{{color:var(--negative)}} .neutral{{color:var(--neutral)}}
  .trend-row{{font-size:.85rem;color:var(--muted)}}
  .trend{{font-weight:600}}
  .trend.up{{color:var(--positive)}} .trend.down{{color:var(--negative)}} .trend.side{{color:var(--neutral)}}
  .news-block{{border-top:1px solid var(--border);padding-top:.6rem}}
  .news-title{{font-size:.75rem;color:var(--muted);margin-bottom:.4rem}}
  .news-item{{display:block;font-size:.78rem;color:var(--text);text-decoration:none;padding:3px 0;border-bottom:1px solid #1e293b;line-height:1.4}}
  .news-item:hover{{color:var(--accent)}}
  .news-date{{color:var(--muted);font-size:.7rem;margin-right:4px}}
  .no-news{{font-size:.78rem;color:var(--muted)}}
  .err-msg{{color:var(--negative);font-size:.85rem}}
  footer{{text-align:center;padding:2rem 0 1rem;color:var(--muted);font-size:.8rem}}
  @media(max-width:500px){{.stats-row{{grid-template-columns:1fr 1fr}}}}
</style>
</head>
<body>
<header>
  <h1>📊 Portfolio Tracker</h1>
  <p>Ostatnia aktualizacja: {generated_at} &nbsp;|&nbsp; {len(portfolio_data)} pozycji</p>
</header>
<div class="grid">{cards_html}</div>
<footer>Dane z Yahoo Finance &amp; Google News · Aktualizacja co niedziela (GitHub Actions)</footer>
</body>
</html>"""


def main():
    print(f"Start: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    portfolio_data = []

    for pos in PORTFOLIO:
        name   = pos["name"]
        ticker = pos["ticker"]
        print(f"→ {name} ({ticker})")
        data = fetch_stock_data(ticker)
        news = fetch_news(name, ticker)
        print(f"  Cena: {data['price'] if data else 'BŁĄD'} | Newsów: {len(news)}")
        portfolio_data.append({
            "name":     name,
            "ticker":   ticker,
            "currency": pos["currency"],
            "data":     data,
            "news":     news,
        })

    html = generate_html(portfolio_data)
    out_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ Wygenerowano index.html ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
