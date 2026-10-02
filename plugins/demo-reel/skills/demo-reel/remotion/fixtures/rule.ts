export function checkOrder(order: {total: number}, limit = 500) {
  // one rule: an order over the limit needs a manual check
  if (order.total > limit) {
    return {ok: false, reason: 'OVER_LIMIT'};
  }
  return {ok: true};
}

export const ORDER_LIMIT = 500;
