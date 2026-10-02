import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Shot} from '../types';
import {theme} from '../theme';

// slots.text = {text: "..."}; the text types out over the first two seconds. A phrase written
// ~~like this~~ is struck through once typed. slots.total = {kind: 'timer-total', seconds} shows a
// take's real timer total under the text, filled by build_props from the take's timer marks.
export const TitleCard: React.FC<{shot: Shot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const raw = shot.slots.text?.text ?? '';
  const parts = raw.split(/(~~[^~]+~~)/).filter(Boolean).map((p) =>
    p.startsWith('~~') ? {text: p.slice(2, -2), struck: true} : {text: p, struck: false});
  const length = parts.reduce((n, p) => n + p.text.length, 0);
  let left = Math.round(interpolate(frame, [0, 2 * fps], [0, length], {extrapolateRight: 'clamp'}));
  const strike = interpolate(frame, [2 * fps, 2.5 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const total = shot.slots.total?.seconds;
  const totalIn = interpolate(frame, [2.5 * fps, 3 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 200px'}}>
      <div style={{font: `600 72px ${theme.sans}`, color: theme.ink, lineHeight: 1.2}}>
        {parts.map((p, i) => {
          const shown = p.text.slice(0, Math.max(0, left));
          left -= p.text.length;
          return p.struck ? (
            <span key={i} style={{position: 'relative', color: strike > 0 ? theme.muted : theme.ink}}>
              {shown}
              <span style={{position: 'absolute', left: 0, top: '55%', height: 6, width: `${strike * 100}%`,
                background: theme.error}} />
            </span>
          ) : <span key={i}>{shown}</span>;
        })}
      </div>
      {total !== undefined ? (
        <div style={{marginTop: 48, opacity: totalIn, font: `600 96px ${theme.mono}`, color: theme.accent}}>
          {Math.floor(total / 60)}:{String(Math.floor(total % 60)).padStart(2, '0')}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
