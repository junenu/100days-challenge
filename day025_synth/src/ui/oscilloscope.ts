export class Oscilloscope {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private analyser: AnalyserNode;
  private animId: number | null = null;
  private dataArray: Float32Array<ArrayBuffer>;

  constructor(canvas: HTMLCanvasElement, analyser: AnalyserNode) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.analyser = analyser;
    this.dataArray = new Float32Array(analyser.fftSize) as Float32Array<ArrayBuffer>;
  }

  start(): void {
    const draw = () => {
      this.animId = requestAnimationFrame(draw);
      this.render();
    };
    draw();
  }

  stop(): void {
    if (this.animId !== null) {
      cancelAnimationFrame(this.animId);
      this.animId = null;
    }
  }

  private render(): void {
    const { width, height } = this.canvas;
    this.analyser.getFloatTimeDomainData(this.dataArray);

    this.ctx.fillStyle = '#0a0a14';
    this.ctx.fillRect(0, 0, width, height);

    // Grid lines
    this.ctx.strokeStyle = '#1a1a2e';
    this.ctx.lineWidth = 1;
    for (let i = 1; i < 4; i++) {
      const y = (height / 4) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(width, y);
      this.ctx.stroke();
    }
    this.ctx.beginPath();
    this.ctx.moveTo(width / 2, 0);
    this.ctx.lineTo(width / 2, height);
    this.ctx.stroke();

    // Center line
    this.ctx.strokeStyle = '#2a2a4a';
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.moveTo(0, height / 2);
    this.ctx.lineTo(width, height / 2);
    this.ctx.stroke();

    // Waveform with glow
    const gradient = this.ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, '#00d4ff');
    gradient.addColorStop(0.5, '#a855f7');
    gradient.addColorStop(1, '#00d4ff');

    this.ctx.shadowColor = '#a855f7';
    this.ctx.shadowBlur = 8;
    this.ctx.strokeStyle = gradient;
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();

    const sliceWidth = width / this.dataArray.length;
    let x = 0;
    for (let i = 0; i < this.dataArray.length; i++) {
      const v = this.dataArray[i];
      const y = (v * 0.8 * height) / 2 + height / 2;
      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
      x += sliceWidth;
    }
    this.ctx.stroke();
    this.ctx.shadowBlur = 0;
  }
}
