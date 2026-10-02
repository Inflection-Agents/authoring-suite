import React from 'react';
import {useCurrentFrame} from 'remotion';
import type {TermLine} from '../types';
import {theme} from '../theme';
import {Panel} from './Panel';

const TYPE_FRAMES = 15;   // a command types out over half a second at 30 fps
const LINE_PX = 34;
const KEEP = 40;          // lines kept for layout; the pane clips the oldest at its top

// Drawn from the take's events, not recorded: each line appears on the take's clock, so the pane is
// always in sync with the facts panel and the browser recording, and its text is always legible. A long
// line wraps instead of being cut, so a request path or a compiler error reads in full.
export const TerminalPane: React.FC<{lines?: TermLine[]; label?: string; style?: React.CSSProperties;
  height?: number}> = ({lines = [], label = 'terminal', style}) => {
  const frame = useCurrentFrame();
  const shown = lines.filter((l) => l.atFrame <= frame);
  return (
    <Panel label={label} style={style}>
      <div style={{position: 'absolute', left: 24, right: 24, top: 56, bottom: 24, overflow: 'hidden',
        display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', font: `400 22px/${LINE_PX}px ${theme.mono}`}}>
        {shown.slice(-KEEP).map((l, i) => {
          const typed = l.kind === 'cmd'
            ? l.text.slice(0, Math.ceil((l.text.length * (frame - l.atFrame + 1)) / TYPE_FRAMES))
            : l.text;
          return (
            <div key={`${l.atFrame}-${i}`} style={{flexShrink: 0, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere',
              color: l.kind === 'cmd' ? theme.ink : l.kind === 'err' ? theme.error : theme.muted}}>
              {l.kind === 'cmd' ? <span style={{color: theme.accent}}>$ </span> : null}{typed}
            </div>
          );
        })}
      </div>
    </Panel>
  );
};
