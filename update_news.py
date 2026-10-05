import json, re, html, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"news-feed.json"

queries={
"en":["Vietnam foreign investment business regulation site:chinhphu.vn OR site:reuters.com","Vietnam trade market investment foreign investors site:reuters.com"],
"vi":["Việt Nam đầu tư nước ngoài doanh nghiệp chính sách site:chinhphu.vn","Việt Nam thương mại xuất nhập khẩu FDI site:chinhphu.vn OR site:reuters.com"],
"zh-tw":["越南 外國投資 企業 政策","越南 貿易 市場 投資"],
"zh-cn":["越南 外商投资 企业 政策","越南 贸易 市场 投资"],
}
params={"en":("en-US","US","US:en"),"vi":("vi-VN","VN","VN:vi"),"zh-tw":("zh-TW","TW","TW:zh-Hant"),"zh-cn":("zh-CN","CN","CN:zh-Hans")}

def rss_url(q,loc):
    hl,gl,ceid=params[loc]
    return "https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q+" when:14d","hl":hl,"gl":gl,"ceid":ceid})

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 YingFaGlobalNewsBot/1.0"})
    with urllib.request.urlopen(req,timeout=25) as r:return r.read()

def clean(s):
    s=html.unescape(re.sub(r"<[^>]+>"," ",s or ""))
    return re.sub(r"\s+"," ",s).strip()

def parse(xml):
    root=ET.fromstring(xml);out=[]
    for it in root.findall('.//item'):
        title=clean(it.findtext('title'))
        link=it.findtext('link') or ''
        desc=clean(it.findtext('description'))
        pub=it.findtext('pubDate') or ''
        source_el=it.find('source'); source=clean(source_el.text if source_el is not None else '')
        try: dt=datetime.strptime(pub,'%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
        except Exception: dt=datetime.now(timezone.utc)
        if title: out.append({"date":dt.strftime('%d %b %Y'),"title":title,"summary":desc[:320],"source":source or 'News source',"url":link,"_dt":dt.isoformat()})
    return out

data=json.loads(OUT.read_text(encoding='utf-8'))
for loc,qs in queries.items():
    merged=[]
    for q in qs:
        try: merged.extend(parse(fetch(rss_url(q,loc))))
        except Exception: pass
    seen=set();fresh=[]
    for x in sorted(merged,key=lambda z:z['_dt'],reverse=True):
        key=re.sub(r'\W+',' ',x['title'].lower()).strip()
        if key in seen:continue
        seen.add(key);x.pop('_dt',None);fresh.append(x)
    if fresh:
        # Keep the 20 newest fetched items. Preserve existing feed metadata.
        data[loc]['items']=fresh[:20]
        data[loc]['auto']={"en":"News is refreshed automatically when new items are published.","vi":"Tin mới được tự động cập nhật khi có nội dung mới.","zh-tw":"有新內容發布時，新聞將自動更新。","zh-cn":"有新内容发布时，新闻将自动更新。"}[loc]
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
