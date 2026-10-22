#!/usr/bin/env python3
"""Collect PUBLIC federal intelligence. No credentials, no agency data."""
import json, pathlib, urllib.request, datetime, os
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data'; OUT.mkdir(exist_ok=True)
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
URLS={
 'kev':'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json',
 'register':'https://www.federalregister.gov/api/v1/documents.json?per_page=100&order=newest&conditions%5Bterm%5D=cybersecurity%20OR%20artificial%20intelligence%20OR%20information%20technology'
}
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'PublicCIOResearchDashboard/1.0 (public data; no auth)','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=35) as r: return json.load(r)
def read(name,default):
 try:return json.loads((OUT/name).read_text())
 except (OSError,ValueError):return default
def write(name,obj):
 (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
previous_status=read('status.json',{}).get('sources',{})
status={'updated_at':NOW,'sources':{}}
def record_source(name, ok, count=None, error=None):
    prior=previous_status.get(name,{})
    last_success = NOW if ok else (prior.get('last_success_at') or (prior.get('retrieved_at') if prior.get('ok') else None))
    entry={'ok':ok,'checked_at':NOW,'last_success_at':last_success}
    if count is not None:entry['count']=count
    if error is not None:entry['error']=str(error)
    status['sources'][name]=entry

try:
 raw=get(URLS['kev']); vulns=raw.get('vulnerabilities',[])
 if not isinstance(vulns,list) or not vulns:raise ValueError('No KEV records returned')
 items=[{'cve':str(v.get('cveID','')),'vendor':str(v.get('vendorProject','')),'product':str(v.get('product','')),'name':str(v.get('vulnerabilityName','')),'added':str(v.get('dateAdded','')),'due':str(v.get('dueDate','')),'ransomware':str(v.get('knownRansomwareCampaignUse','')),'action':str(v.get('requiredAction','')),'notes':str(v.get('notes',''))} for v in vulns]
 items.sort(key=lambda x:(x['added'],x['cve']),reverse=True)
 previous=read('kev.json',{}).get('items',[])
 previous_ids={x.get('cve') for x in previous}
 new_records=[x for x in items if x['cve'] not in previous_ids] if previous else []
 vendors=Counter(x['vendor'] for x in items)
 write('insights.json',{'retrieved_at':NOW,'comparison_available':bool(previous),'new_since_previous_collection':new_records[:100],'new_count':len(new_records),'top_vendors':[{'name':k,'count':v} for k,v in vendors.most_common(30)],'note':'New means first seen by this collector, not necessarily newly published or exploited.'})
 write('kev.json',{'retrieved_at':NOW,'source':URLS['kev'],'count':len(items),'items':items})
 history=read('kev-history.json',[])
 day=NOW[:10]; entry={'date':day,'count':len(items)}
 history=[h for h in history if h.get('date')!=day]+[entry]
 write('kev-history.json',history[-365:])
 record_source('kev',True,len(items))
except Exception as e:
 record_source('kev',False,error=e)
try:
 previous_register=read('federal-register.json',{}).get('items',[])
 raw=get(URLS['register']); docs=raw.get('results',[])
 if not isinstance(docs,list):raise ValueError('Invalid Federal Register response')
 items=[{'title':str(d.get('title','')),'date':str(d.get('publication_date','')),'url':str(d.get('html_url','')),'type':str(d.get('type','')),'agency':', '.join(a.get('name','') for a in d.get('agencies',[]) if isinstance(a,dict)),'abstract':str(d.get('abstract') or '')[:600]} for d in docs]
 write('federal-register.json',{'retrieved_at':NOW,'source':URLS['register'],'count':len(items),'items':items})
 record_source('register',True,len(items))
except Exception as e:
 record_source('register',False,error=e)
# Public Federal Register change detection. Do not compare stale data after a failed fetch.
try:
 if not status['sources']['register']['ok']:raise RuntimeError('Skipped policy comparison because Federal Register retrieval failed')
 current=read('federal-register.json',{}).get('items',[])
 # Compare stable document URLs against the prior successful snapshot saved separately.
 prior=read('register-seen.json',{}).get('urls',[])
 seen=set(prior)
 fresh=[d for d in current if d.get('url') and d['url'] not in seen] if prior else []
 write('policy-insights.json',{'retrieved_at':NOW,'comparison_available':bool(prior),'new_count':len(fresh),'new_documents':fresh[:35],'note':'New means first observed in the current matching search results, not necessarily new binding federal policy. Search results may include notices, proposed rules and unrelated documents.'})
 # Retain identifiers over time to avoid treating older search results as new.
 combined=list(dict.fromkeys(prior+[d['url'] for d in current if d.get('url')]))
 write('register-seen.json',{'retrieved_at':NOW,'urls':combined[-10000:]})
 record_source('policy_insights',True,len(fresh))
except Exception as e:
 record_source('policy_insights',False,error=e)

write('status.json',status)
print(json.dumps(status,indent=2))
if not (status['sources']['kev']['ok'] or status['sources']['register']['ok']):raise SystemExit('All public feeds failed; keeping previously collected data')
