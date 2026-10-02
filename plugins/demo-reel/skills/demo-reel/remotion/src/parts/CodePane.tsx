import React, {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';
import type {Slot} from '../types';
import {theme} from '../theme';
import {Panel} from './Panel';

type Token = {content: string; color?: string};
type Tokens = {lines: Token[][]; firstLine: number; file: string};
const EDIT_FRAMES = 20;

// Code from a tokens file: lit lines at full strength, the rest dimmed, an error underline and
// callout, and edits that retype a line on the take's clock.
export const CodePane: React.FC<{slot: Slot; style?: React.CSSProperties}> = ({slot, style}) => {
  const frame = useCurrentFrame();
  const [data, setData] = useState<Tokens | null>(null);
  const [handle] = useState(() => (slot.tokens ? delayRender('tokens') : null));
  useEffect(() => {
    if (!slot.tokens || handle === null) return;
    fetch(staticFile(slot.tokens)).then((r) => r.json()).then((d: Tokens) => {
      setData(d);
      continueRender(handle);
    });
  }, [slot.tokens, handle]);
  const focus = new Set(slot.focus ?? []);
  const edits = (slot.edits ?? []).filter((e) => e.atFrame <= frame);
  return (
    <Panel label={data?.file ?? slot.label} style={style}>
      {data ? (
        <pre style={{margin: 0, padding: '64px 40px 40px', font: `400 28px/1.55 ${theme.mono}`}}>
          {data.lines.map((line, i) => {
            const n = data.firstLine + i;
            const edit = edits.filter((e) => e.line === n).pop();
            const lit = focus.size === 0 || focus.has(n) || Boolean(edit);
            const err = slot.error?.line === n;
            let body: React.ReactNode = line.map((t, j) => <span key={j} style={{color: t.color}}>{t.content}</span>);
            if (edit) {
              const k = Math.min(1, (frame - edit.atFrame + 1) / EDIT_FRAMES);
              const indent = edit.before.match(/^\s*/)?.[0] ?? '';
              body = <span style={{color: theme.ink, background: 'rgba(41,231,214,0.15)'}}>
                {indent + edit.after.trimStart().slice(0, Math.ceil(edit.after.trimStart().length * k))}</span>;
            }
            return (
              <div key={n} style={{opacity: lit ? 1 : 0.3, display: 'flex',
                textDecoration: err ? `wavy underline ${theme.error}` : undefined}}>
                <span style={{width: 64, flexShrink: 0, color: theme.muted, textAlign: 'right', marginRight: 32}}>{n}</span>
                <span style={{whiteSpace: 'pre'}}>{body}</span>
              </div>
            );
          })}
        </pre>
      ) : undefined}
      {slot.error ? (
        <div style={{position: 'absolute', right: 40, bottom: 40, maxWidth: 760, padding: '16px 20px',
          border: `1.5px solid ${theme.error}`, borderRadius: 10, background: theme.bg,
          color: theme.error, font: `500 22px ${theme.mono}`}}>{slot.error.message}</div>
      ) : null}
    </Panel>
  );
};
