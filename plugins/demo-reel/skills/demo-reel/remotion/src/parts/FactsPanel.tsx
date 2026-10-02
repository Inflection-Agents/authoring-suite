import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {Fact} from '../types';
import {theme} from '../theme';
import {Panel} from './Panel';

// One row per name, in the order names first appeared, showing the newest value: a hold that changes
// from 15 to 20 minutes updates its row instead of adding a second one.
const latest = (facts: Fact[]) => {
  const rows = new Map<string, Fact>();
  for (const f of facts) rows.set(f.name, f);
  return [...rows.values()];
};

export const FactsPanel: React.FC<{facts?: Fact[]; style?: React.CSSProperties}> = ({facts = [], style}) => {
  const frame = useCurrentFrame();
  return (
    <Panel label="Facts" style={style}>
      <div style={{padding: '56px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14}}>
        {latest(facts.filter((f) => f.atFrame <= frame)).map((f) => {
          const t = interpolate(frame, [f.atFrame, f.atFrame + 12], [0, 1], {extrapolateRight: 'clamp'});
          return (
            <div key={f.name} style={{opacity: t, transform: `translateY(${(1 - t) * 12}px)`,
              display: 'flex', justifyContent: 'space-between', gap: 16, font: `500 24px ${theme.mono}`}}>
              <span style={{color: theme.muted, whiteSpace: 'nowrap', flexShrink: 0}}>{f.name}</span>
              <span style={{color: theme.ink, textAlign: 'right'}}>{String(f.value)}</span>
            </div>
          );
        })}
      </div>
    </Panel>
  );
};
