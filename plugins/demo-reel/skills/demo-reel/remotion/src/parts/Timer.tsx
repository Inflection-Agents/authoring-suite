import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import type {Slot} from '../types';
import {theme} from '../theme';

// Real elapsed time between the take's timer-start and timer-stop marks. Before the start it reads
// 0:00; after the stop it holds the real total, so it can never show time that did not pass.
export const Timer: React.FC<{slot?: Slot; speed: number}> = ({slot, speed}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!slot || slot.startFrame === undefined || slot.stopFrame === undefined || slot.seconds === undefined) return null;
  const running = frame >= slot.stopFrame ? slot.seconds
    : Math.max(0, Math.min(slot.seconds, ((frame - slot.startFrame) / fps) * speed));
  const s = Math.floor(running);
  return (
    <div style={{position: 'absolute', left: 60, bottom: 50, padding: '10px 18px', borderRadius: 10,
      background: theme.bg, border: `1.5px solid ${theme.accent}`, color: theme.accent,
      font: `600 40px ${theme.mono}`, zIndex: 5}}>
      {Math.floor(s / 60)}:{String(s % 60).padStart(2, '0')}
    </div>
  );
};
