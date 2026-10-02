import React from 'react';
import {AbsoluteFill, staticFile} from 'remotion';
import {Video} from '@remotion/media';
import type {Shot} from '../types';
import {THREE_PANE as G} from '../theme';
import {Panel} from '../parts/Panel';
import {FactsPanel} from '../parts/FactsPanel';
import {TerminalPane} from '../parts/TerminalPane';

// left: terminal drawn from events; center: the browser recording, trimmed to the take's window and
// captured at exactly 820 x 1000 (820 x 780 with a log strip); right: facts; optional log strip.
export const ThreePane: React.FC<{shot: Shot}> = ({shot}) => {
  const {left, center, right, log} = shot.slots;
  const h = log ? G.height - G.log - G.gap : G.height;
  return (
    <AbsoluteFill style={{padding: G.pad, gap: G.gap, display: 'flex', flexDirection: 'column'}}>
      <div style={{height: h, display: 'flex', gap: G.gap}}>
        <TerminalPane lines={left?.lines} label={left?.label ?? 'api calls'} height={h} style={{width: G.left}} />
        <Panel label={center?.label} style={{width: G.center}}>
          {center?.src ? <Video src={staticFile(center.src)} trimBefore={center.trimBefore ?? 0}
            playbackRate={shot.speed} muted objectFit="cover" style={{width: '100%', height: '100%'}} /> : undefined}
        </Panel>
        <FactsPanel facts={right?.facts} style={{width: G.right}} />
      </div>
      {log ? <TerminalPane lines={log.lines} label={log.label ?? 'logs'} height={G.log} style={{height: G.log}} /> : null}
    </AbsoluteFill>
  );
};
