// The demo driver: runs the scenario as a list of steps and logs every event to the take's file.
// Copy to demo/driver/driver.ts, fill STEPS in phase 09, and run from the repository root:
//   TAKE=run-1 [SCENARIO=run-1] demo/node_modules/.bin/tsx demo/driver/driver.ts
// Every event carries `t` (seconds since this process started) and `wall` (Unix seconds); the
// recorders log only `wall`, and build_props lines the clocks up through `capture-start`.
import {appendFileSync, mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {execSync} from 'node:child_process';
import {performance} from 'node:perf_hooks';

const take = process.env.TAKE ?? 'run-1';
const dir = `demo/takes/${take}`;
const EVENTS = `${dir}/events.jsonl`;
const BASE = process.env.DEMO_BASE_URL ?? 'http://localhost:8080';
mkdirSync(dir, {recursive: true});

const t0 = performance.now();
const emit = (e: Record<string, unknown> & {kind: string}) => appendFileSync(EVENTS, JSON.stringify({
  t: Math.round(performance.now() - t0) / 1000, wall: Date.now() / 1000, take, ...e}) + '\n');
export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** An HTTP call to the system under demo. Logs the request and the response. */
export async function call(step: string, method: string, path: string, body?: unknown) {
  emit({kind: 'request', step, method, path, body});
  const res = await fetch(BASE + path, {method, headers: {'content-type': 'application/json'},
    body: body === undefined ? undefined : JSON.stringify(body)});
  const json = (await res.json().catch(() => ({}))) as Record<string, unknown>;
  emit({kind: 'response', step, status: res.status, body: json});
  return json;
}

/** A shell command, such as a build. Its output becomes terminal lines; a failure is logged, not thrown. */
export function command(step: string, cmd: string) {
  let out = '';
  let exit = 0;
  try {
    out = execSync(cmd, {encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe']});
  } catch (err) {
    const e = err as {status?: number; stdout?: string; stderr?: string};
    exit = e.status ?? 1;
    out = `${e.stdout ?? ''}${e.stderr ?? ''}`;
  }
  emit({kind: 'command', step, cmd, exit, out: out.trim()});
  return {exit, out};
}

/** Replace the text of one line in a file, and log it so the code pane can retype it. */
export function edit(step: string, file: string, line: number, after: string) {
  const lines = readFileSync(file, 'utf8').split('\n');
  const before = lines[line - 1];
  lines[line - 1] = after;
  writeFileSync(file, lines.join('\n'));
  emit({kind: 'edit', step, file, line, before, after});
}

export const invocation = (step: string, id: string) => emit({kind: 'invocation', step, id});
export const fact = (name: string, value: unknown) => emit({kind: 'fact', name, value});
export const outcome = (name: string, value: unknown) => emit({kind: 'outcome', name, value});
/** A dependency replaced by a stub for the demo. Every shot of this take shows a "stub" badge. */
export const stub = (name: string) => emit({kind: 'stub', name});
/** A named moment, used as a shot's `in`/`out` or as the timer's `timer-start`/`timer-stop`. */
export const mark = (name: string) => emit({kind: 'mark', name});

type Step = {name: string; pauseMs?: number; run: () => Promise<void> | void};

// Fill in phase 09: one list of steps per scenario, each step doing its calls and logging what the
// video should show. SCENARIO picks the list and defaults to the take's name, so the two proof takes
// of one scenario can have names of their own.
const SCENARIOS: Record<string, Step[]> = {};

const scenario = process.env.SCENARIO ?? take;
const STEPS = SCENARIOS[scenario];
if (!STEPS) throw new Error(`no scenario ${scenario}; known: ${Object.keys(SCENARIOS).join(', ')}`);
emit({kind: 'capture-start'});
for (const s of STEPS) {
  await s.run();
  await sleep(s.pauseMs ?? 1000);
}
emit({kind: 'capture-end'});
