import React from 'react';
import {theme} from '../theme';

// The labelled frame every slot sits in. With no children it draws "no asset", so a missing
// recording shows up in review instead of failing the render.
export const Panel: React.FC<{label?: string; children?: React.ReactNode; style?: React.CSSProperties}> = ({
  label, children, style,
}) => (
  <div style={{position: 'relative', background: theme.panel, border: `1px solid ${theme.rule}`,
    borderRadius: 12, overflow: 'hidden', ...style}}>
    {label ? (
      <div style={{position: 'absolute', top: 12, left: 16, zIndex: 2, font: `500 18px ${theme.mono}`,
        letterSpacing: '0.12em', textTransform: 'uppercase', color: theme.muted}}>{label}</div>
    ) : null}
    {children ?? (
      <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center',
        font: `400 22px ${theme.mono}`, color: theme.muted}}>no asset</div>
    )}
  </div>
);
