import React from 'react';
import {AbsoluteFill} from 'remotion';
import type {Shot} from '../types';
import {CodePane} from '../parts/CodePane';
import {TerminalPane} from '../parts/TerminalPane';
import {Timer} from '../parts/Timer';

// The change made live: the edit retyped in the code pane, the real build and re-run output in the
// terminal, both from the take's events, and the timer between the take's timer marks.
export const EditorBuild: React.FC<{shot: Shot}> = ({shot}) => (
  <AbsoluteFill style={{padding: 40, gap: 20, display: 'flex', flexDirection: 'row'}}>
    <CodePane slot={shot.slots.code ?? {}} style={{width: 1080}} />
    <TerminalPane lines={shot.slots.terminal?.lines} label={shot.slots.terminal?.label ?? 'build'} height={1000}
      style={{width: 720}} />
    <Timer slot={shot.slots.timer} speed={shot.speed} />
  </AbsoluteFill>
);
