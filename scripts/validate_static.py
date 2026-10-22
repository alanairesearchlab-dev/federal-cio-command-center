#!/usr/bin/env python3
"""Validate static HTML JavaScript syntax and key navigation/assessment contracts.

Requires Python 3.12+ and Node.js 20+. No external Python packages.
"""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "briefing.html", "intelligence.html", "about.html")

class ScriptExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.scripts = []
        self.current = []
        self.external = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
            self.external = any(k == "src" for k, _ in attrs)
            self.current = []

    def handle_data(self, data):
        if self.in_script:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_script:
            if not self.external:
                script = "".join(self.current).strip()
                if script:
                    self.scripts.append(script)
            self.in_script = False

def main():
    failures = []
    with tempfile.TemporaryDirectory() as directory:
        for page in PAGES:
            path = ROOT / page
            html = path.read_text(encoding="utf-8")
            if 'class="global-navigation"' not in html:
                failures.append(f"{page}: primary navigation missing")
            for destination in ("index.html", "briefing.html", "intelligence.html", "about.html"):
                if destination not in html:
                    failures.append(f"{page}: link to {destination} missing")
            parser = ScriptExtractor()
            parser.feed(html)
            for i, script in enumerate(parser.scripts, 1):
                target = Path(directory) / f"{page}.{i}.js"
                target.write_text(script, encoding="utf-8")
                result = subprocess.run(
                    ["node", "--check", str(target)],
                    capture_output=True, text=True, check=False,
                )
                if result.returncode:
                    failures.append(f"{page}: inline script {i} syntax error:\n{result.stderr}")
            print(f"{page}: {len(parser.scripts)} inline scripts checked")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("Static HTML and JavaScript checks passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
