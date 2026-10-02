import React from 'react';
import {theme} from '../theme';

export const Badges: React.FC<{badges: string[]}> = ({badges}) =>
  badges.length ? (
    <div style={{position: 'absolute', top: 32, right: 40, display: 'flex', gap: 12, zIndex: 10}}>
      {badges.map((b) => (
        <div key={b} style={{padding: '8px 16px', borderRadius: 999, border: `1.5px solid ${theme.accent}`,
          color: theme.accent, background: 'rgba(15,17,21,0.85)', font: `600 22px ${theme.mono}`}}>{b}</div>
      ))}
    </div>
  ) : null;
