// Browser-level smoke test for the public static site.
// Run after: npm install --no-save playwright && npx playwright install chromium
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const assert = require('node:assert/strict');
const base = 'http://127.0.0.1:8765';
const server = spawn('python3', ['-m', 'http.server', '8765', '--bind', '127.0.0.1'], { stdio: 'ignore' });
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
  let browser;
  try {
    for (let i=0; i<40; i++) {
      try { const r=await fetch(base+'/index.html'); if(r.ok) break; } catch {}
      await sleep(250);
    }
    browser=await chromium.launch({headless:true});
    const page=await browser.newPage();
    const errors=[];
    page.on('pageerror', err => errors.push(err.message));
    for (const path of ['/', '/intelligence.html', '/about.html']) {
      await page.goto(base+path, {waitUntil:'networkidle', timeout:45000});
      assert(await page.locator('header').count(), path+' missing header');
      assert(await page.locator('a[href="index.html"]').count(), path+' missing dashboard link');
      assert(await page.locator('a[href="intelligence.html"]').count(), path+' missing intelligence link');
      assert(await page.locator('a[href="about.html"]').count(), path+' missing about link');
      if (path==='/') {
        await page.waitForTimeout(1500);
        const status=await page.locator('#v92-status').innerText();
        assert(!status.includes('Assessment unavailable'), 'Assessment failed: '+status);
        assert(await page.locator('#v92-assessments .v92-card').count()>0, 'No executive assessment cards rendered');
        assert((await page.locator('#v92-brief').innerText()).length>100, 'Executive brief did not populate');
        assert(await page.locator('#v92-copy').isEnabled(), 'Copy executive brief disabled');
      }
      if (path==='/intelligence.html') {
        const updated=await page.locator('#updated').innerText();
        assert(!updated.includes('unavailable'), 'Intelligence data failed: '+updated);
      }
      console.log('PASS '+path);
    }
    assert.deepEqual(errors, [], 'Uncaught browser errors: '+errors.join('; '));
    console.log('All browser smoke tests passed');
  } finally {
    if(browser) await browser.close();
    server.kill();
  }
})().catch(err=>{console.error(err);process.exitCode=1;server.kill();});
