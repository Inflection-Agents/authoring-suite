// Records the workflow UI while the driver runs a take. Copy to demo/capture/browser.ts and run it
// before the driver (run-take.sh does both):
//   TAKE=run-1 UI_ROUTE='http://localhost:<UI_PORT>/<route>/{id}' STEP=start demo/node_modules/.bin/tsx demo/capture/browser.ts
// It logs `recording-start` with the wall clock the moment recording begins, so build_props can trim
// the video to the take's window. It records at the three-pane centre slot's exact size, so the
// video is never scaled. Find the real UI_ROUTE in phase 07.
import {chromium} from 'playwright';
import {appendFileSync, existsSync, mkdirSync, readFileSync, renameSync} from 'node:fs';

const take = process.env.TAKE ?? 'run-1';
const route = process.env.UI_ROUTE ?? '';
const step = process.env.STEP ?? '';
const width = Number(process.env.WIDTH ?? 820);
const height = Number(process.env.HEIGHT ?? 1000);
const EVENTS = `demo/takes/${take}/events.jsonl`;
const OUT = `demo/remotion/public/takes/${take}/browser.webm`;
mkdirSync(`demo/takes/${take}`, {recursive: true});
mkdirSync(`demo/remotion/public/takes/${take}`, {recursive: true});
const read = () => (existsSync(EVENTS)
  ? readFileSync(EVENTS, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l)) : []);

const browser = await chromium.launch();
const context = await browser.newContext({viewport: {width, height},
  recordVideo: {dir: `demo/takes/${take}/.raw`, size: {width, height}}});
const page = await context.newPage();
appendFileSync(EVENTS, JSON.stringify({wall: Date.now() / 1000, take, kind: 'recording-start', surface: 'browser'}) + '\n');
await page.goto(route.includes('{id}') ? 'about:blank' : route || 'about:blank');

let navigated = false;
for (;;) {
  const events = read();
  const inv = events.find((e) => e.kind === 'invocation' && (!step || e.step === step));
  if (inv && !navigated && route.includes('{id}')) {
    await page.goto(route.replace('{id}', String(inv.id)));
    navigated = true;
  }
  if (events.some((e) => e.kind === 'capture-end')) break;
  await page.waitForTimeout(200);
}
await page.waitForTimeout(1000);
const video = page.video();
await context.close();
await browser.close();
if (video) renameSync(await video.path(), OUT);
console.log(`browser: ${OUT}`);
