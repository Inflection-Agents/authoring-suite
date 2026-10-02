import React from 'react';
import {AbsoluteFill, Freeze, staticFile, useCurrentFrame} from 'remotion';
import {Video} from '@remotion/media';
import type {Shot} from '../types';
import {THREE_PANE as G, theme} from '../theme';
import {Panel} from '../parts/Panel';
import {FactsPanel} from '../parts/FactsPanel';
import {TerminalPane} from '../parts/TerminalPane';
import {Timer} from '../parts/Timer';

// left: terminal drawn from events; center: the browser recording, trimmed to the take's window and
// captured at exactly 820 x 1000 (820 x 780 with a log strip); right: facts; optional log strip;
// optional timer, for a shot that continues a timed change begun in an earlier shot.
export const ThreePane: React.FC<{shot: Shot}> = ({shot}) => {
  const {left, center, right, log} = shot.slots;
  const frame = useCurrentFrame();
  // after the window's `out` event the recording would show what came next, so it holds its last frame
  const held = center?.freezeAt !== undefined && frame >= center.freezeAt;
  const h = log ? G.height - G.log - G.gap : G.height;
  return (
    <AbsoluteFill style={{padding: G.pad, gap: G.gap, display: 'flex', flexDirection: 'column'}}>
      <div style={{height: h, display: 'flex', gap: G.gap}}>
        <TerminalPane lines={left?.lines} label={left?.label ?? 'api calls'} height={h} style={{width: G.left}} />
        <Panel style={{width: G.center}}>
          {center?.src ? (
            <Freeze frame={center.freezeAt ?? 0} active={held}>
              <Video src={staticFile(center.src)} trimBefore={center.trimBefore ?? 0}
                playbackRate={shot.speed} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
            </Freeze>
          ) : undefined}
        </Panel>
        <FactsPanel facts={right?.facts} style={{width: G.right}} />
      </div>
      {log ? <TerminalPane lines={log.lines} label={log.label ?? 'logs'} height={G.log} style={{height: G.log}} /> : null}
      {/* the recording fills its panel at its captured size, so its label sits in the margin above it */}
      {center?.label ? (
        <div style={{position: 'absolute', top: 10, left: G.pad + G.left + G.gap + 16, font: `500 18px ${theme.mono}`,
          letterSpacing: '0.12em', textTransform: 'uppercase', color: theme.muted}}>{center.label}</div>
      ) : null}
      <Timer slot={shot.slots.timer} speed={shot.speed}
        style={{left: undefined, bottom: undefined, top: G.pad + 12, right: 1920 - G.pad - G.left + 12}} />
    </AbsoluteFill>
  );
};
