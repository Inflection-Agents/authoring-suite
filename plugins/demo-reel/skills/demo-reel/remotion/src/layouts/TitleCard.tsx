import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Shot} from '../types';
import {theme} from '../theme';

// slots.text = {text: "..."}; the text types out over the first two seconds.
export const TitleCard: React.FC<{shot: Shot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const text = shot.slots.text?.text ?? '';
  const shown = Math.round(interpolate(frame, [0, 2 * fps], [0, text.length], {extrapolateRight: 'clamp'}));
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 200px'}}>
      <div style={{font: `600 72px ${theme.sans}`, color: theme.ink, lineHeight: 1.2}}>{text.slice(0, shown)}</div>
    </AbsoluteFill>
  );
};
