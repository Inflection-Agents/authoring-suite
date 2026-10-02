// The toy's filled-in STEPS, pasted into demo/driver/driver.ts in place of the empty list.
const STEPS: Step[] = [
  {name: 'setup', pauseMs: 300, run: () => stub('payment-gateway')},
  {name: 'start', pauseMs: 1500, run: async () => {
    const r = await call('start', 'POST', '/orders/start', {total: 420});
    invocation('start', String(r.invocationId));
    fact('orderTotal', 420);
    state.id = String(r.invocationId);
  }},
  {name: 'approve', pauseMs: 1500, run: async () => {
    const r = await call('approve', 'POST', `/approve/${state.id}`);
    outcome('order-check', r.outcome);
  }},
];
