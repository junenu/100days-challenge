import { Synth } from '../audio/synth';
import type { WaveType } from '../audio/synth';

function makeKnob(
  label: string,
  min: number,
  max: number,
  value: number,
  step: number,
  onChange: (v: number) => void
): HTMLElement {
  const wrap = document.createElement('div');
  wrap.className = 'knob-wrap';

  const lbl = document.createElement('label');
  lbl.textContent = label;

  const input = document.createElement('input');
  input.type = 'range';
  input.min = String(min);
  input.max = String(max);
  input.value = String(value);
  input.step = String(step);
  input.addEventListener('input', () => onChange(parseFloat(input.value)));

  const val = document.createElement('span');
  val.className = 'knob-value';
  val.textContent = value.toFixed(2);
  input.addEventListener('input', () => {
    val.textContent = parseFloat(input.value).toFixed(2);
  });

  wrap.append(lbl, input, val);
  return wrap;
}

export function buildControls(container: HTMLElement, synth: Synth): void {
  // Wave type
  const waveSection = document.createElement('div');
  waveSection.className = 'control-section';
  const waveTitle = document.createElement('h3');
  waveTitle.textContent = 'Oscillator';
  waveSection.appendChild(waveTitle);

  const waveTypes: WaveType[] = ['sine', 'square', 'sawtooth', 'triangle'];
  const waveBtnGroup = document.createElement('div');
  waveBtnGroup.className = 'btn-group';

  waveTypes.forEach(type => {
    const btn = document.createElement('button');
    btn.textContent = type;
    btn.className = type === synth.state.waveType ? 'wave-btn active' : 'wave-btn';
    btn.addEventListener('click', () => {
      synth.setWaveType(type);
      waveBtnGroup.querySelectorAll('.wave-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
    waveBtnGroup.appendChild(btn);
  });
  waveSection.appendChild(waveBtnGroup);
  container.appendChild(waveSection);

  // ADSR
  const adsrSection = document.createElement('div');
  adsrSection.className = 'control-section';
  const adsrTitle = document.createElement('h3');
  adsrTitle.textContent = 'ADSR Envelope';
  adsrSection.appendChild(adsrTitle);

  const adsrGrid = document.createElement('div');
  adsrGrid.className = 'knob-grid';
  adsrGrid.appendChild(makeKnob('Attack', 0.001, 2, synth.state.adsr.attack, 0.001, v => synth.setAdsr({ attack: v })));
  adsrGrid.appendChild(makeKnob('Decay', 0.001, 2, synth.state.adsr.decay, 0.001, v => synth.setAdsr({ decay: v })));
  adsrGrid.appendChild(makeKnob('Sustain', 0, 1, synth.state.adsr.sustain, 0.01, v => synth.setAdsr({ sustain: v })));
  adsrGrid.appendChild(makeKnob('Release', 0.001, 4, synth.state.adsr.release, 0.001, v => synth.setAdsr({ release: v })));
  adsrSection.appendChild(adsrGrid);
  container.appendChild(adsrSection);

  // Effects
  const fxSection = document.createElement('div');
  fxSection.className = 'control-section';
  const fxTitle = document.createElement('h3');
  fxTitle.textContent = 'Effects';
  fxSection.appendChild(fxTitle);

  const fxGrid = document.createElement('div');
  fxGrid.className = 'knob-grid';
  fxGrid.appendChild(makeKnob('Delay Time', 0, 1, synth.state.delayTime, 0.01, v => synth.setDelayTime(v)));
  fxGrid.appendChild(makeKnob('Delay Feedback', 0, 0.95, synth.state.delayFeedback, 0.01, v => synth.setDelayFeedback(v)));
  fxGrid.appendChild(makeKnob('Reverb', 0, 1, synth.state.reverbAmount, 0.01, v => synth.setReverbAmount(v)));
  fxSection.appendChild(fxGrid);
  container.appendChild(fxSection);

  // Volume
  const volSection = document.createElement('div');
  volSection.className = 'control-section';
  const volTitle = document.createElement('h3');
  volTitle.textContent = 'Master Volume';
  volSection.appendChild(volTitle);

  const volGrid = document.createElement('div');
  volGrid.className = 'knob-grid';
  volGrid.appendChild(makeKnob('Volume', 0, 1, synth.state.volume, 0.01, v => synth.setVolume(v)));
  volSection.appendChild(volGrid);
  container.appendChild(volSection);
}
