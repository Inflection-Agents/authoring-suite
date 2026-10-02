// The toy's filled-in SCENARIOS, pasted into demo/driver/driver.ts in place of the empty one.
const SCENARIOS: Record<string, Step[]> = {toy: [
  {name: 'setup', pauseMs: 300, run: () => stub('hotel-api')},
  {name: 'start', pauseMs: 1500, run: async () => {
    const r = await call('start', 'POST', '/bookings/start', {nights: 3});
    invocation('start', String(r.invocationId));
    fact('nights', 3);
    state.id = String(r.invocationId);
  }},
  {name: 'confirm', pauseMs: 1500, run: async () => {
    const r = await call('confirm', 'POST', `/confirm/${state.id}`);
    outcome('booking', r.outcome);
  }},
]};
