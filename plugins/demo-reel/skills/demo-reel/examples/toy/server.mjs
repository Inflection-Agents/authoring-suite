// A toy system for proving the capture chain: start a booking, open its page, confirm it.
// node server.mjs   (port 8080)
import {createServer} from 'node:http';
import {randomUUID} from 'node:crypto';

const bookings = new Map();
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
  if (req.method === 'POST' && a === 'bookings') {
    const id = `id_${randomUUID().slice(0, 8)}`;
    bookings.set(id, {nights: body.nights, status: 'PENDING'});
    return send(res, 200, {invocationId: id});
  }
  if (req.method === 'POST' && a === 'confirm' && bookings.has(b)) {
    const booking = bookings.get(b);
    booking.status = 'CONFIRMED';
    return send(res, 200, {outcome: booking.status});
  }
  if (req.method === 'GET' && a === 'ui' && bookings.has(b)) {
    const booking = bookings.get(b);
    return send(res, 200, `<html><head><meta http-equiv="refresh" content="0.5"></head>
      <body style="font:28px system-ui;padding:40px;background:#fff"><h2>Booking ${b}</h2>
      <p>nights: ${booking.nights}</p><p>status: <b>${booking.status}</b></p></body></html>`, 'text/html');
  }
  send(res, 404, {error: 'not found'});
}).listen(8080);
