// A toy system for proving the capture chain: start an order, open its page, approve it.
// node server.mjs   (port 8080)
import {createServer} from 'node:http';
import {randomUUID} from 'node:crypto';

const orders = new Map();
const send = (res, code, body, type = 'application/json') => {
  res.writeHead(code, {'content-type': type});
  res.end(type === 'application/json' ? JSON.stringify(body) : body);
};
createServer(async (req, res) => {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const body = chunks.length ? JSON.parse(Buffer.concat(chunks).toString()) : {};
  const [, a, b] = req.url.split('/');
  if (req.method === 'GET' && a === 'health') return send(res, 200, {ok: true});
  if (req.method === 'POST' && a === 'orders') {
    const id = `id_${randomUUID().slice(0, 8)}`;
    orders.set(id, {total: body.total, status: 'WAITING'});
    return send(res, 200, {invocationId: id});
  }
  if (req.method === 'POST' && a === 'approve' && orders.has(b)) {
    const o = orders.get(b);
    o.status = o.total > 500 ? 'MANUAL_CHECK' : 'APPROVED';
    return send(res, 200, {outcome: o.status});
  }
  if (req.method === 'GET' && a === 'ui' && orders.has(b)) {
    const o = orders.get(b);
    return send(res, 200, `<html><head><meta http-equiv="refresh" content="0.5"></head>
      <body style="font:28px system-ui;padding:40px;background:#fff"><h2>Order ${b}</h2>
      <p>total: ${o.total}</p><p>status: <b>${o.status}</b></p></body></html>`, 'text/html');
  }
  send(res, 404, {error: 'not found'});
}).listen(8080);
