import React from 'react';
import {AbsoluteFill} from 'remotion';
import type {Shot} from '../types';
import {CodePane} from '../parts/CodePane';

// slots.code = {tokens, focus, error, edits}
export const CodeShot: React.FC<{shot: Shot}> = ({shot}) => (
  <AbsoluteFill style={{padding: 80}}>
    <CodePane slot={shot.slots.code ?? {}} style={{flex: 1}} />
  </AbsoluteFill>
);
