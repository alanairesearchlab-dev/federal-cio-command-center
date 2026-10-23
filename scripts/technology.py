#!/usr/bin/env python3
"""Public RSS technology coverage. Failed endpoints are reported, never bypassed."""
import datetime, html, json, pathlib, re, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
from urllib.parse import urlparse
ROOT=pathlib.Path(__file__).resolve().parents[1]/'data'
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
# Candidate endpoints: acceptance is determined by actual successful HTTPS retrieval.
SOURCES=[
('Ars Technica','Journalism','https://feeds.arstechnica.com/arstechnica/index'),
('The Register','Journalism','https://www.theregister.com/headlines.atom'),
('TechCrunch','Journalism','https://techcrunch.com/feed/'),
('WIRED','Journalism','https://www.wired.com/feed/rss'),
('ZDNET','Journalism','https://www.zdnet.com/news/rss.xml'),
('InfoWorld','Journalism','https://www.infoworld.com/feed/'),
('VentureBeat','Journalism','https://venturebeat.com/feed/'),
('IEEE Spectrum','Research','https://spectrum.ieee.org/feeds/feed.rss'),
('MIT Technology Review','Research','https://www.technologyreview.com/feed/'),
('Microsoft Azure','Vendor','https://azure.microsoft.com/en-us/blog/feed/'),
('Microsoft Security','Vendor','https://www.microsoft.com/en-us/security/blog/feed/'),
('AWS News','Vendor','https://aws.amazon.com/blogs/aws/feed/'),
('AWS Security','Vendor','https://aws.amazon.com/blogs/security/feed/'),
('Google Cloud','Vendor','https://cloud.google.com/blog/rss'),
('Google Security','Research','https://security.googleblog.com/feeds/posts/default'),
('Cloudflare','Vendor','https://blog.cloudflare.com/rss/'),
('GitHub Blog','Vendor','https://github.blog/feed/'),
('Red Hat','Vendor','https://www.redhat.com/en/rss/blog'),
('Cisco Blogs','Vendor','https://blogs.cisco.com/feed'),
('Cisco Talos','Research','https://blog.talosintelligence.com/rss/'),
('Palo Alto Unit 42','Research','https://unit42.paloaltonetworks.com/feed/'),
('SANS Internet Storm Center','Research','https://isc.sans.edu/rssfeed.xml'),
('Schneier on Security','Research','https://www.schneier.com/feed/atom/'),
('BleepingComputer','Journalism','https://www.bleepingcomputer.com/feed/'),
('Krebs on Security','Journalism','https://krebsonsecurity.com/feed/'),
('The Hacker News','Journalism','https://feeds.feedburner.com/TheHackersNews'),
('Dark Reading','Journalism','https://www.darkreading.com/rss.xml'),
('FedScoop','Federal IT','https://fedscoop.com/feed/'),
('Nextgov/FCW','Federal IT','https://www.nextgov.com/rss/'),
('Federal News Network','Federal IT','https://federalnewsnetwork.com/feed/'),
('MeriTalk','Federal IT','https://www.meritalk.com/feed/'),
('GSA Technology','Federal IT','https://www.gsa.gov/blog/feed'),
('NIST News','Federal IT','https://www.nist.gov/news-events/news/rss.xml'),
('CISA News','Federal IT','https://www.cisa.gov/news-events/news.xml'),
('OpenAI News','Vendor','https://openai.com/news/rss.xml'),
('Google DeepMind','Research','https://deepmind.google/blog/rss.xml'),
('Hugging Face','Vendor','https://huggingface.co/blog/feed.xml'),
('Linux Foundation','Research','https://www.linuxfoundation.org/blog/rss.xml'),
('CNCF','Research','https://www.cncf.io/feed/'),
('Kubernetes','Research','https://kubernetes.io/feed.xml'),
]
def read(name):
 try:return json.loads((ROOT/name).read_text())
 except (OSError,ValueError):return {}
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',s or ''))).strip()
def field(el,tag):
 node=el.find(tag)
 return ''.join(node.itertext()).strip() if node is not None else ''
def parse(payload):
 root=ET.fromstring(payload); out=[]
 if root.find('channel') is not None:
  for el in root.findall('./channel/item'):
   out.append((field(el,'title'),field(el,'link'),field(el,'pubDate'),clean(field(el,'description'))))
 else:
  ns='{http://www.w3.org/2005/Atom}'
  for el in root.findall(ns+'entry'):
   links=[x.get('href','') for x in el.findall(ns+'link') if x.get('rel','alternate') in ('alternate',None)]
   out.append((field(el,ns+'title'),links[0] if links else '',field(el,ns+'published') or field(el,ns+'updated'),clean(field(el,ns+'summary'))))
 return out[:25]
def topic(text):
 t=text.lower()
 rules=[('Cybersecurity',r'vulnerab|security|breach|ransomware|exploit|malware|patch|zero.day|threat'),('AI & Emerging Tech',r'artificial intelligence|\bai\b|machine learning|llm|model|agentic|quantum'),('Cloud & Infrastructure',r'cloud|azure|aws|kubernetes|container|datacenter|data center|network|storage'),('Federal IT & Policy',r'federal|government|agency|omb|nist|cisa|procurement|acquisition'),('Enterprise Technology',r'microsoft|enterprise|identity|software|database|linux|developer|platform')]
 for name,pattern in rules:
  if re.search(pattern,t):return name
 return 'Emerging Technology'
def score(item):
 t=(item['title']+' '+item['summary']).lower()
 points=0
 for pattern,value in [(r'federal|government|cisa|nist|omb',4),(r'enterprise|identity|zero trust|cloud|cybersecurity|vulnerab|security',3),(r'azure|aws|kubernetes|supply chain|acquisition|infrastructure',2),(r'\bai\b|artificial intelligence|quantum|open source',1)]:
  if re.search(pattern,t):points+=value
 if re.search(r'iphone|smartphone|gaming|celebrity|streaming|consumer gadget',t):points-=4
 return points
old=read('technology-news.json'); prior=old.get('items',[])
last={x['name']:x for x in read('technology-sources.json').get('sources',[])}
articles=[]; sources=[]
for name,kind,url in SOURCES:
 prior_meta=last.get(name,{})
 entry={'name':name,'category':kind,'url':url,'checked_at':NOW,'last_success_at':prior_meta.get('last_success_at'),'ok':False,'count':0}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'FederalCIOCommandCenter/1.3 (+https://github.com/alanairesearchlab-dev/federal-cio-command-center)','Accept':'application/rss+xml, application/atom+xml, application/xml'})
  with urllib.request.urlopen(req,timeout=12) as response:
   payload=response.read(1_500_001)
  if len(payload)>1_500_000:raise ValueError('Feed exceeds size limit')
  records=parse(payload)
  for title,link,date,summary in records:
   if not title or urlparse(link).scheme!='https':continue
   articles.append({'title':clean(title)[:230],'url':link,'published':date[:90],'summary':summary[:350],'source':name,'source_category':kind,'topic':topic(title+' '+summary),'score':score({'title':title,'summary':summary})})
  if not records:raise ValueError('No feed entries')
  entry.update(ok=True,count=len(records),last_success_at=NOW)
 except Exception as exc:
  entry['error']=str(exc)[:180]
  # Retain stale articles for a failed publisher, clearly flagged in metadata.
  articles.extend(x for x in prior if x.get('source')==name)
 sources.append(entry)
# Collapse exact URL duplicates, and near-identical titles from multiple outlets.
articles=sorted({a['url'].split('?')[0]:a for a in articles}.values(),key=lambda a:(a['score'],a['published']),reverse=True)
clusters=[]
def words(t):return set(re.findall(r'[a-z0-9]{4,}',t.lower()))-{'about','after','their','these','those','with','from','that','this','have','more','will'}
for a in articles:
 w=words(a['title']); match=None
 for c in clusters:
  v=words(c['title'])
  if len(w&v)>=4 and len(w&v)/max(1,min(len(w),len(v)))>=.65:
   match=c;break
 if match:
  if not any(x['url']==a['url'] for x in match['sources']):
   match['sources'].append({'name':a['source'],'url':a['url']})
 else:
  clusters.append({**a,'sources':[{'name':a['source'],'url':a['url']}]})
# Source diversity: keep up to 3 clusters per leading publisher in first 60.
selected=[]; counts={}
for c in clusters:
 name=c['source']
 if counts.get(name,0)>=3:continue
 selected.append(c);counts[name]=counts.get(name,0)+1
 if len(selected)>=90:break
save('technology-news.json',{'retrieved_at':NOW,'candidate_sources':len(SOURCES),'successful_sources':sum(x['ok'] for x in sources),'collected_articles':len(articles),'items':selected,'note':'Automated topic/ranking and approximate title clustering. No source or report is an endorsement; verify original reporting.'})
save('technology-sources.json',{'retrieved_at':NOW,'sources':sources,'note':'Candidate RSS endpoints are validated on each collection. Failures remain visible; no bypassing publisher access controls.'})
print('Technology sources:',sum(x['ok'] for x in sources),'/',len(SOURCES),'clusters:',len(selected))
