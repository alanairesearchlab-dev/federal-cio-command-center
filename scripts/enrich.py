#!/usr/bin/env python3
"""Derive conservative public-source policy lifecycle cues and CVE correlations."""
import json, pathlib, re, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]/'data'
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def read(name):
 try:return json.loads((ROOT/name).read_text())
 except (OSError,ValueError):return {}
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
eo=read('executive-orders.json');omb=read('omb-memoranda.json');fr=read('federal-register.json');kev=read('kev.json');feeds=read('security-feeds.json')
policies=[]
for item in eo.get('items',[]):
 policies.append({'id':'EO-'+str(item.get('executive_order_number') or item.get('document_number')),'title':item.get('title',''),'url':item.get('url',''),'date':item.get('publication_date'),'source':'Federal Register','document_type':'Executive Order','status':'Published; current legal status unverified','change_type':'publication'})
for item in omb.get('items',[]):
 policies.append({'id':item.get('number'),'title':item.get('title',''),'url':item.get('url',''),'date':None,'source':'OMB','document_type':'Memorandum','status':'Indexed; current status unverified','change_type':'index observation'})
# Relationship cues are not determinations of amendment, rescission, or supersession.
pattern=re.compile(r'\b(amend(?:s|ing|ment)?|revok(?:e|es|ing|ation)|rescind(?:s|ed|ing)?|supersed(?:e|es|ed|ing))\b',re.I)
for item in policies:
 hit=pattern.search(item['title'])
 item['relationship_cue']=hit.group(0).lower() if hit else None
 item['requires_document_review']=bool(hit)
write('policy-lifecycle.json',{'retrieved_at':NOW,'items':policies[:120],'count':len(policies),'eo_available':bool(eo.get('items')),'omb_available':bool(omb.get('items')),'note':'Titles provide relationship cues only. Never infer actual amendment, revocation, supersession, legal effect, or applicability without reading authoritative documents.'})
# Correlate by exact CVE identifier. Avoid fuzzy vendor-only matches.
by_cve={}
for article in feeds.get('items',[]):
 text=' '.join([article.get('title',''),article.get('summary','')])
 for cve in set(re.findall(r'\bCVE-\d{4}-\d{4,}\b',text,re.I)):
  if article.get('url','').startswith('https://'):
   by_cve.setdefault(cve.upper(),[]).append({'title':article.get('title','')[:220],'url':article['url'],'source':article.get('source'),'kind':article.get('kind')})
matches=[]
for vuln in kev.get('items',[]):
 cve=vuln.get('cve','').upper()
 if cve in by_cve:
  refs=list({r['url']:r for r in by_cve[cve]}.values())[:8]
  matches.append({'cve':cve,'vendor':vuln.get('vendor'),'product':vuln.get('product'),'date_added':vuln.get('added'),'sources':refs,'source_count':len(set(r.get('source') for r in refs)),'note':'Exact CVE reference correlation, not independent confirmation of claims or agency exposure.'})
write('correlations.json',{'retrieved_at':NOW,'items':matches[:60],'count':len(matches),'note':'Exact CVE matching only. Multiple reports about one CVE do not represent multiple vulnerabilities.'})
print('Policy records:',len(policies),'CVE correlations:',len(matches))
