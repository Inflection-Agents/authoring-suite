import React from 'react';
import {Composition, type CalculateMetadataFunction} from 'remotion';
import {Cut} from './Cut';
import type {CutProps} from './types';

const fallback: CutProps = {fps: 30, width: 1920, height: 1080, cut: 'empty', scenes: []};

const calculateMetadata: CalculateMetadataFunction<CutProps> = ({props}) => ({
  durationInFrames: Math.max(1, props.scenes.reduce((n, s) => n + s.durationInFrames, 0)),
  fps: props.fps,
  width: props.width,
  height: props.height,
});

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Cut"
    component={Cut}
    durationInFrames={1}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={fallback}
    calculateMetadata={calculateMetadata}
  />
);
