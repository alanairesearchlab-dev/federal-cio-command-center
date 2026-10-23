#!/usr/bin/env python3
"""Prevent accidental disclosure of agency, staff or credential details in tracked text."""
import pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','ls-files','--cached'],cwd=ROOT,text=True).splitlines()
patterns={
 'agency identifier':re.compile(r'\bselective\s+service\s+system\b|\bsss\.gov\b',re.I),
 'employee name':re.compile(r'\b(?:ali\s+tilave|steve\s+panich|jonathan\s+kimball|tahreem\s+choudhary)\b',re.I),
 'credential':re.compile(r'(?i)(?:api[_-]?key|access[_-]?token|secret[_-]?key)\s*[:=]\s*[\x22\x27][A-Za-z0-9_\-]{18,}'),
 'private key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
}
fails=[]
for name in paths:
 p=ROOT/name
 if not p.is_file() or p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.zip','.pdf'}:continue
 try:s=p.read_text(encoding='utf-8')
 except (UnicodeError,OSError):continue
 for label,pattern in patterns.items():
  if pattern.search(s):fails.append((name,label))
if fails:
 for path,label in fails:print(f'REVIEW REQUIRED: {path}: {label}')
 sys.exit(1)
print(f'Public repository privacy scan passed for {len(paths)} tracked paths')
