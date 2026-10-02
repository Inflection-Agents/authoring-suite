import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import type {Shot} from '../types';
import {Panel} from '../parts/Panel';

// slots.figure = {src: "figures/fig-01.svg"}; a slow push-in.
export const Figure: React.FC<{shot: Shot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const src = shot.slots.figure?.src;
  const scale = interpolate(frame, [0, shot.durationInFrames], [1, 1.06]);
  return (
    <AbsoluteFill style={{padding: 80}}>
      <Panel style={{flex: 1, background: '#F6F6F6'}}>
        {src ? <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'contain',
          transform: `scale(${scale})`}} /> : undefined}
      </Panel>
    </AbsoluteFill>
  );
};
