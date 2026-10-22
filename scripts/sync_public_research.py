#!/usr/bin/env python3
"""Publish verifiable research-index updates from Crossref, not ChatGPT task output."""
import argparse
import datetime as dt
import json
import os
import pathlib
import urllib.parse
import urllib.request

DATA=pathlib.Path("data/reports.json")
QUERIES=[
    "arts based education reflection",
    "social emotional learning arts education",
    "reflective practice developmental psychology",
]
def fetch(query):
    params=urllib.parse.urlencode({"query.bibliographic":query,"rows":"8","sort":"published","order":"desc",
                                   "filter":"from-pub-date:"+((dt.date.today()-dt.timedelta(days=60)).isoformat())})
    req=urllib.request.Request("https://api.crossref.org/works?"+params,headers={
        "User-Agent":"SABRDF-GlobalResearch/1.0 (public research metadata; github.com/awarewaveai-pei/art-reflection-framework)",
        "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        return json.load(resp)["message"]["items"]
def date_of(item):
    for key in ("published","published-print","published-online","issued"):
        parts=item.get(key,{}).get("date-parts",[])
        if parts and parts[0]:
            ymd=(parts[0]+[1,1])[:3]
            try:return dt.date(*ymd).isoformat()
            except (ValueError,TypeError):pass
    return "unknown"
def load():
    if not DATA.exists():return {"schema_version":1,"updated_at":None,"items":[]}
    return json.loads(DATA.read_text(encoding="utf-8"))
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--period",choices=["daily","weekly","monthly"],required=True)
    args=parser.parse_args()
    now=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    today=now.date().isoformat()
    data=load()
    if args.period=="daily":
        papers={}
        for query in QUERIES:
            try:
                results=fetch(query)
            except Exception as exc:
                print("Crossref query unavailable:",query,repr(exc))
                continue
            for p in results:
                doi=p.get("DOI")
                if not doi or p.get("type") not in ("journal-article","proceedings-article"):
                    continue
                paper_date=date_of(p)
                if paper_date=="unknown" or paper_date>today:continue
                title=(p.get("title") or [""])[0].strip()
                if not title:continue
                papers[doi]={"title":title,"date":paper_date,"url":"https://doi.org/"+urllib.parse.quote(doi,safe="/"),"venue":(p.get("container-title") or [""])[0]}
        selected=sorted(papers.values(),key=lambda p:p["date"],reverse=True)[:5]
        if not selected:
            print("No verifiable records, leaving data unchanged.")
            return
        bullets="；".join(f'{p["date"]}｜{p["title"]}（{p["venue"] or "出版來源待核對"}）' for p in selected)
        record={"id":"crossref-daily-"+today,"type":"daily","date":today,
                "title":"SABRDF 公開研究索引｜Crossref 文獻動態",
                "summary":"索引範圍：藝術本位教育、反思實踐、SEL 與發展心理學。以下為 Crossref 收錄的相關文獻，不代表其研究結果已被完整審查，也不能視為 SABRDF 有效性證據。"+bullets,
                "source_url":selected[0]["url"],"origin":"crossref"}
    else:
        lookback=7 if args.period=="weekly" else 31
        cutoff=today
        since=(now.date()-dt.timedelta(days=lookback)).isoformat()
        existing=[x for x in data.get("items",[]) if x.get("origin")=="crossref" and x.get("type")=="daily"
                  and since<=x.get("date","")<=cutoff]
        if not existing:
            print("No indexed daily updates, leaving data unchanged.")
            return
        kind="每週" if args.period=="weekly" else "每月"
        record={"id":"crossref-"+args.period+"-"+today,"type":args.period,"date":today,
                "title":f"SABRDF {kind}公開文獻索引回顧",
                "summary":f"統整最近 {lookback} 天網站已收錄的 {len(existing)} 次 Crossref 公開文獻索引更新。此為來源監測回顧，不是 ChatGPT 原始研究決策報告，未對研究品質或 SABRDF 成效進行獨立學術驗證。",
                "source_url":"https://api.crossref.org/works","origin":"crossref"}
    data["items"]=[x for x in data.get("items",[]) if x.get("id")!=record["id"]]+[record]
    data["items"].sort(key=lambda x:x.get("date",""),reverse=True)
    data["updated_at"]=now.isoformat()
    DATA.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Updated",record["id"])
if __name__=="__main__":
    main()
