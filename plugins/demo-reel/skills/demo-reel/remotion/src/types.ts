export type Fact = {atFrame: number; name: string; value: string | number | boolean};
export type TermLine = {atFrame: number; kind: 'cmd' | 'out' | 'err'; text: string};
export type Edit = {atFrame: number; line: number; before: string; after: string};

export type Slot = {
  kind?: 'terminal' | 'browser' | 'facts-panel' | 'code' | 'figure' | 'timer' | 'timer-total';
  label?: string;
  text?: string;          // title
  src?: string;           // figure image or browser recording, under public/
  trimBefore?: number;    // frames to skip at the start of a recording
  freezeAt?: number;      // shot frame where the recording reaches its window's end and holds still
  tokens?: string;        // code tokens JSON under public/, from scripts/tokenize.mjs
  focus?: number[];       // line numbers to light; the rest dim
  error?: {line: number; message: string};
  edits?: Edit[];
  lines?: TermLine[];
  facts?: Fact[];
  startFrame?: number;    // timer
  stopFrame?: number;
  seconds?: number;
};

export type Shot = {
  id: string;
  layout: 'title' | 'figure' | 'code' | 'three-pane' | 'editor-build';
  from: number;
  durationInFrames: number;
  slots: Record<string, Slot>;
  badges: string[];
  speed: number;
};

export type Scene = {id: string; title: string; audio?: string; durationInFrames: number; shots: Shot[]};
export type CutProps = {fps: number; width: number; height: number; cut: string; scenes: Scene[]};
