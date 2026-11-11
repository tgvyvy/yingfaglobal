import json, re, html, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"news-feed.json"
queries={'en': ['Vietnam economy GDP growth inflation consumption 2026', 'Vietnam foreign direct investment FDI new projects 2026', 'Vietnam foreign investors market entry business environment reforms', 'Vietnam manufacturing factories industrial parks investment 2026', 'Vietnam exports imports trade agreements supply chains 2026', 'Vietnam logistics ports airports seaports infrastructure projects', 'Vietnam transport infrastructure expressways railways airports 2026', 'Vietnam renewable energy power grid solar wind investment', 'Vietnam digital economy technology semiconductor data center investment', 'Vietnam tourism international visitors hospitality investment 2026', 'Vietnam retail consumer market e-commerce growth 2026', 'Vietnam real estate industrial property office market investment', 'Vietnam tax policy investment law business regulations 2026', 'Vietnam public private partnership infrastructure projects 2026', 'Vietnam startup innovation venture capital investment', 'Vietnam agriculture food processing exports investment', 'Vietnam healthcare education services foreign investment', 'Vietnam banking finance capital market stock market foreign investors', 'Ho Chi Minh City investment FDI industrial zones 2026', 'Vietnam regional investment opportunities Da Nang Hai Phong Binh Duong Dong Nai'], 'vi': ['Việt Nam tăng trưởng GDP kinh tế tiêu dùng lạm phát 2026', 'Việt Nam thu hút vốn đầu tư trực tiếp nước ngoài FDI dự án mới 2026', 'Việt Nam cải cách môi trường đầu tư thủ tục gia nhập thị trường', 'Việt Nam khu công nghiệp nhà máy sản xuất dự án đầu tư 2026', 'Việt Nam xuất nhập khẩu thương mại hiệp định chuỗi cung ứng 2026', 'Việt Nam logistics cảng biển cảng hàng không hạ tầng 2026', 'Việt Nam cao tốc đường sắt sân bay dự án hạ tầng giao thông', 'Việt Nam năng lượng tái tạo điện gió điện mặt trời lưới điện đầu tư', 'Việt Nam kinh tế số công nghệ bán dẫn trung tâm dữ liệu đầu tư', 'Việt Nam du lịch khách quốc tế khách sạn đầu tư 2026', 'Việt Nam thị trường bán lẻ tiêu dùng thương mại điện tử 2026', 'Việt Nam bất động sản công nghiệp văn phòng thị trường đầu tư', 'Việt Nam chính sách thuế luật đầu tư quy định doanh nghiệp 2026', 'Việt Nam hợp tác công tư PPP dự án hạ tầng 2026', 'Việt Nam khởi nghiệp đổi mới sáng tạo vốn đầu tư', 'Việt Nam nông nghiệp chế biến thực phẩm xuất khẩu đầu tư', 'Việt Nam y tế giáo dục dịch vụ vốn đầu tư nước ngoài', 'Việt Nam ngân hàng tài chính thị trường chứng khoán nhà đầu tư nước ngoài', 'TP Hồ Chí Minh thu hút FDI đầu tư khu công nghiệp 2026', 'cơ hội đầu tư Việt Nam Đà Nẵng Hải Phòng Bình Dương Đồng Nai'], 'zh-cn': ['越南 经济 GDP 增长 消费 通胀 2026', '越南 外商直接投资 FDI 新项目 2026', '越南 投资环境 改革 外国投资者 市场准入', '越南 工业园区 工厂 制造业 投资项目 2026', '越南 进出口 贸易协定 供应链 2026', '越南 物流 港口 海港 机场 基础设施 2026', '越南 高速公路 铁路 机场 交通基础设施 项目', '越南 可再生能源 电网 风电 太阳能 投资', '越南 数字经济 科技 半导体 数据中心 投资', '越南 旅游 国际游客 酒店 投资 2026', '越南 零售 消费市场 电子商务 增长 2026', '越南 工业地产 办公楼 房地产 市场 投资', '越南 税务政策 投资法 企业法规 2026', '越南 公私合作 PPP 基础设施 项目 2026', '越南 初创企业 创新 风险投资', '越南 农业 食品加工 出口 投资', '越南 医疗 教育 服务业 外商投资', '越南 银行 金融 资本市场 外国投资者', '胡志明市 FDI 投资 工业园区 2026', '越南 岘港 海防 平阳 同奈 投资机会'], 'zh-tw': ['越南 經濟 GDP 成長 消費 通膨 2026', '越南 外商直接投資 FDI 新專案 2026', '越南 投資環境 改革 外國投資者 市場准入', '越南 工業區 工廠 製造業 投資專案 2026', '越南 進出口 貿易協定 供應鏈 2026', '越南 物流 港口 海港 機場 基礎建設 2026', '越南 高速公路 鐵路 機場 交通基礎建設 專案', '越南 再生能源 電網 風電 太陽能 投資', '越南 數位經濟 科技 半導體 資料中心 投資', '越南 觀光 國際旅客 飯店 投資 2026', '越南 零售 消費市場 電子商務 成長 2026', '越南 工業不動產 辦公大樓 房地產 市場 投資', '越南 稅務政策 投資法 企業法規 2026', '越南 公私協力 PPP 基礎建設 專案 2026', '越南 新創企業 創新 創投', '越南 農業 食品加工 出口 投資', '越南 醫療 教育 服務業 外商投資', '越南 銀行 金融 資本市場 外國投資者', '胡志明市 FDI 投資 工業區 2026', '越南 峴港 海防 平陽 同奈 投資機會']}
params={"en":("en-US","US","US:en"),"vi":("vi-VN","VN","VN:vi"),"zh-tw":("zh-TW","TW","TW:zh-Hant"),"zh-cn":("zh-CN","CN","CN:zh-Hans")}
def clean(s):
 s=html.unescape(re.sub(r"<[^>]+>"," ",s or "")); return re.sub(r"\s+"," ",s).strip()
def fetch(q,loc):
 hl,gl,ceid=params[loc]; url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q+" when:90d","hl":hl,"gl":gl,"ceid":ceid})
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 YingFaGlobalNewsBot/1.0"})
 with urllib.request.urlopen(req,timeout=25) as r: root=ET.fromstring(r.read())
 out=[]
 for it in root.findall(".//item"):
  title=clean(it.findtext("title")); link=it.findtext("link") or ""; desc=clean(it.findtext("description")); pub=it.findtext("pubDate") or ""; se=it.find("source"); source=clean(se.text if se is not None else "")
  try: dt=datetime.strptime(pub,"%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
  except Exception: dt=datetime.now(timezone.utc)
  if title and link: out.append({"date":dt.isoformat(),"title":title,"summary":desc[:420],"source":source or "News source","url":link,"_dt":dt.isoformat()})
 return out
data=json.loads(OUT.read_text(encoding="utf-8"))
for loc,qs in queries.items():
 merged=[]
 for q in qs:
  try: merged.extend(fetch(q,loc))
  except Exception: pass
 seen=set(); fresh=[]
 for x in sorted(merged,key=lambda z:z["_dt"],reverse=True):
  key=(x["url"].split("?")[0].rstrip("/").lower() or re.sub(r"\W+"," ",x["title"].lower()).strip())
  if key in seen: continue
  seen.add(key); x.pop("_dt",None); fresh.append(x)
 if fresh: data[loc]["items"]=fresh[:100]
 data[loc]["auto"]={"en":"News is refreshed automatically from multiple Vietnam business and investment topics.","vi":"Tin tức được tự động cập nhật từ nhiều chủ đề kinh doanh và đầu tư tại Việt Nam.","zh-tw":"新聞將從多個越南商業與投資主題自動更新。","zh-cn":"新闻将从多个越南商业与投资主题自动更新。"}[loc]
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
