#!/usr/bin/env python3
import datetime as dt, json, math, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data.json"
TICKERS = {
  "8031.T":"三井物産","6383.T":"ダイフク","6506.T":"安川電機",
  "8136.T":"サンリオ","7011.T":"三菱重工","6758.T":"ソニーG",
  "4042.T":"東ソー","1605.T":"INPEX","8593.T":"三菱HCキャピタル",
  "1615.T":"NF銀行業","221A.T":"日経半導体ETF","RXRX":"RXRX"
}

def f(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except: return None

def fetch(symbol,name):
    u=f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?range=1y&interval=1d"
    req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 Project-Y/1.4"})
    with urllib.request.urlopen(req,timeout=25) as r: d=json.load(r)
    x=d["chart"]["result"][0]; meta=x.get("meta",{})
    rows=[f(v) for v in x["indicators"]["quote"][0]["close"] if f(v) is not None]
    latest,prev=rows[-1],rows[-2]
    hi=max(rows[-260:]); lo=min(rows[-260:])
    return {"symbol":symbol,"name":name,"currency":meta.get("currency") or ("USD" if "." not in symbol else "JPY"),
      "price":round(latest,4),"change_pct":round((latest/prev-1)*100,2),
      "high_52w":round(hi,4),"low_52w":round(lo,4),
      "drawdown_from_52w_high_pct":round((latest/hi-1)*100,2),"status":"ok"}

old={}
if DATA_FILE.exists():
    try: old=json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except: pass
quotes=[]; errors=[]
for s,n in TICKERS.items():
    try: quotes.append(fetch(s,n))
    except Exception as e:
        prior=next((q for q in old.get("quotes",[]) if q.get("symbol")==s),None)
        if prior:
            prior=dict(prior); prior["status"]="stale"; quotes.append(prior)
        errors.append({"symbol":s,"error":str(e)})
    time.sleep(.7)
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec="minutes")
DATA_FILE.write_text(json.dumps({"version":"1.4","updated_at_jst":now,
 "source":"Yahoo Finance chart endpoint (unofficial)","quotes":quotes,"errors":errors},
 ensure_ascii=False,indent=2),encoding="utf-8")
