// Browser-level smoke test for the public static site.
// Run after: npm install --no-save playwright && npx playwright install chromium
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const pathUtil = require('node:path');
const artifactDir = pathUtil.resolve('artifacts/browser');
fs.mkdirSync(artifactDir, { recursive: true });
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
    const page=await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    const errors=[];
    const desktopNavBoxes=[];
    page.on('pageerror', err => errors.push(err.message));
    for (const path of ['/', '/briefing.html', '/intelligence.html', '/about.html']) {
      await page.goto(base+path, {waitUntil:'networkidle', timeout:45000});
      assert(await page.locator('header').count(), path+' missing header');
      assert(await page.locator('nav a[href^="./index.html"]').count(), path+' missing dashboard link');
      assert(await page.locator('nav a[href^="./intelligence.html"]').count(), path+' missing intelligence link');
      assert(await page.locator('nav a[href^="./about.html"]').count(), path+' missing about link');
      assert(await page.locator('nav a[href="./briefing.html"]').count(), path+' missing briefing link');
      if (path==='/briefing.html') {
        assert(await page.locator('#v96-print').count(), 'Executive PDF export missing');
        await page.waitForTimeout(1500);
        assert(await page.locator('#v92-assessments .v92-card').count()>0, 'Briefing assessment cards missing');
        assert((await page.locator('#v92-brief').innerText()).length>100, 'Briefing text missing');
        assert(await page.locator('#v91-new-list').count(), 'Change review missing');
        assert(await page.locator('#v91-deadlines').count(), 'Action calendar missing');
        assert(await page.locator('.tabbar').count()===0, 'Dashboard tabs leaked into Executive Briefing');
        assert(await page.locator('[id^="view-"]').count()===0, 'Dashboard workspaces leaked into Executive Briefing');
      }
      if (path==='/') {
        assert(await page.locator('a[href="./briefing.html"]').count()>0, 'Dashboard briefing shortcut missing');
        await page.waitForTimeout(1500);
        const status=await page.locator('#v92-status').innerText();
        assert(!status.includes('Assessment unavailable'), 'Assessment failed: '+status);
        assert(await page.locator('#v92-assessments .v92-card').count()>0, 'No executive assessment cards rendered');
        assert((await page.locator('#v92-brief').innerText()).length>100, 'Executive brief did not populate');
        assert(await page.locator('#v92-copy').isEnabled(), 'Copy executive brief disabled');
        await page.locator('button[data-tab="policy"]').click();
        assert(await page.locator('#omb-memo-status').count(), 'OMB memorandum watch missing');
        assert(await page.locator('#eo-watch-status').count(), 'Executive Order watch missing');
        assert(await page.locator('#lifecycle-results').count(), 'Policy lifecycle panel missing');
        await page.locator('button[data-tab="cyber"]').click();
        assert(await page.locator('#correlation-results').count(), 'Cross-source correlation panel missing');
        await page.locator('button[data-tab="overview"]').click();
        assert(await page.locator('#collection-diagnostics').count(), 'Collection diagnostics panel missing');
        await page.locator('button[data-tab="policy"]').click();
        assert(await page.locator('#view-policy a[href="https://www.acquisition.gov/news"]').count(), 'Acquisition policy portal missing');
      }
      if (path==='/intelligence.html') {
        assert(await page.locator('button[data-view="technology"]').count(), 'Technology newsroom tab missing');
        await page.locator('button[data-view="technology"]').click();
        assert(await page.locator('#tech-topic').count(), 'Technology topic filter missing');
        assert(await page.locator('#tech-list').count(), 'Technology story list missing');
        assert(await page.locator('#tech-directory-toggle').count(), 'Publisher directory missing');
        const updated=await page.locator('#updated').innerText();
        assert(!updated.includes('unavailable'), 'Intelligence data failed: '+updated);
      }
      const slug=path==='/'?'dashboard':path.slice(1).replace('.html','');
      await page.screenshot({path:pathUtil.join(artifactDir,slug+'-desktop.png'),fullPage:true,animations:'disabled'});
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+3);
      assert(!overflow,path+' has horizontal overflow on desktop');
      const navigation=await page.locator('.global-navigation').boundingBox();
      desktopNavBoxes.push({path,top:navigation?.y,height:navigation?.height});
      assert(navigation && navigation.width>500,path+' navigation layout missing');
      console.log('PASS '+path);
    }
    // Structural visual regression: all four desktop pages must retain the same navigation geometry.
    const reference=desktopNavBoxes[0];
    for(const box of desktopNavBoxes){
      assert(Math.abs(box.top-reference.top)<=2,'Navigation vertical shift on '+box.path);
      assert(Math.abs(box.height-reference.height)<=2,'Navigation height shift on '+box.path);
    }
    // Repeat at mobile width. Screenshots are retained even when a layout assertion fails.
    await page.setViewportSize({width:390,height:844});
    for(const path of ['/', '/briefing.html', '/intelligence.html', '/about.html']){
      await page.goto(base+path,{waitUntil:'networkidle',timeout:45000});
      const slug=path==='/'?'dashboard':path.slice(1).replace('.html','');
      await page.screenshot({path:pathUtil.join(artifactDir,slug+'-mobile.png'),fullPage:true,animations:'disabled'});
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+3);
      assert(!overflow,path+' has horizontal overflow on mobile');
      assert(await page.locator('.global-navigation a').count()===4,path+' mobile primary navigation incomplete');
      console.log('PASS mobile '+path);
    }
    assert.deepEqual(errors, [], 'Uncaught browser errors: '+errors.join('; '));
    console.log('All browser smoke tests passed');
  } finally {
    if(browser) await browser.close();
    server.kill();
  }
})().catch(err=>{console.error(err);process.exitCode=1;server.kill();});
