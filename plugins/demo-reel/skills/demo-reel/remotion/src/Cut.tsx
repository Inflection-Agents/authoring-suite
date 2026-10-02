import React from 'react';
import {AbsoluteFill, Sequence, Series, staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import type {CutProps, Shot} from './types';
import {theme} from './theme';
import {TitleCard} from './layouts/TitleCard';
import {Figure} from './layouts/Figure';
import {CodeShot} from './layouts/CodeShot';
import {ThreePane} from './layouts/ThreePane';
import {EditorBuild} from './layouts/EditorBuild';
import {Badges} from './parts/Badges';

const LAYOUTS: Record<Shot['layout'], React.FC<{shot: Shot}>> = {
  title: TitleCard,
  figure: Figure,
  code: CodeShot,
  'three-pane': ThreePane,
  'editor-build': EditorBuild,
};

export const Cut: React.FC<CutProps> = ({scenes}) => (
  <AbsoluteFill style={{backgroundColor: theme.bg}}>
    <Series>
      {scenes.map((scene) => (
        <Series.Sequence key={scene.id} durationInFrames={scene.durationInFrames} name={scene.id}>
          {scene.audio ? <Audio src={staticFile(scene.audio)} /> : null}
          {scene.shots.map((shot) => {
            const Layout = LAYOUTS[shot.layout];
            return (
              <Sequence key={shot.id} from={shot.from} durationInFrames={shot.durationInFrames} name={shot.id}>
                <Layout shot={shot} />
                <Badges badges={shot.badges} />
              </Sequence>
            );
          })}
        </Series.Sequence>
      ))}
    </Series>
  </AbsoluteFill>
);
