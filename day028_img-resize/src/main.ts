import './style.css';

interface State {
  image: HTMLImageElement | null;
  filename: string;
  originalWidth: number;
  originalHeight: number;
  targetWidth: number;
  targetHeight: number;
  aspectLocked: boolean;
  format: string;
  quality: number;
  resultBlob: Blob | null;
}

const state: State = {
  image: null,
  filename: '',
  originalWidth: 0,
  originalHeight: 0,
  targetWidth: 0,
  targetHeight: 0,
  aspectLocked: true,
  format: 'image/png',
  quality: 0.9,
  resultBlob: null,
};

// DOM refs
const dropZone = document.getElementById('drop-zone') as HTMLDivElement;
const fileInput = document.getElementById('file-input') as HTMLInputElement;
const controlsSection = document.getElementById('controls-section') as HTMLElement;
const originalPreview = document.getElementById('original-preview') as HTMLImageElement;
const originalInfo = document.getElementById('original-info') as HTMLDivElement;
const widthInput = document.getElementById('width-input') as HTMLInputElement;
const heightInput = document.getElementById('height-input') as HTMLInputElement;
const lockBtn = document.getElementById('lock-btn') as HTMLButtonElement;
const lockNote = document.getElementById('lock-note') as HTMLParagraphElement;
const qualityGroup = document.getElementById('quality-group') as HTMLDivElement;
const qualityInput = document.getElementById('quality-input') as HTMLInputElement;
const qualityLabel = document.getElementById('quality-label') as HTMLSpanElement;
const resizeBtn = document.getElementById('resize-btn') as HTMLButtonElement;
const resultCard = document.getElementById('result-card') as HTMLDivElement;
const resultPreview = document.getElementById('result-preview') as HTMLImageElement;
const resultInfo = document.getElementById('result-info') as HTMLDivElement;
const downloadBtn = document.getElementById('download-btn') as HTMLButtonElement;

// File upload handling
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer?.files[0];
  if (file) loadFile(file);
});

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  const file = fileInput.files?.[0];
  if (file) loadFile(file);
});

function loadFile(file: File): void {
  if (!file.type.startsWith('image/')) {
    alert('PNG・JPEG・WebP 形式の画像ファイルを選択してください。');
    return;
  }

  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => {
    state.image = img;
    state.filename = file.name;
    state.originalWidth = img.naturalWidth;
    state.originalHeight = img.naturalHeight;
    state.targetWidth = img.naturalWidth;
    state.targetHeight = img.naturalHeight;

    originalPreview.src = url;
    originalInfo.innerHTML = buildInfoHtml(img.naturalWidth, img.naturalHeight, file.size, file.type);
    widthInput.value = String(img.naturalWidth);
    heightInput.value = String(img.naturalHeight);

    controlsSection.classList.remove('hidden');
    resultCard.classList.add('hidden');
    state.resultBlob = null;
    clearActivePreset();
  };
  img.src = url;
}

function buildInfoHtml(w: number, h: number, bytes: number, mime: string): string {
  const ext = mime.split('/')[1]?.toUpperCase() ?? 'Unknown';
  const size = bytes < 1024 * 1024
    ? `${(bytes / 1024).toFixed(1)} KB`
    : `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `
    <div class="info-row"><span>解像度</span><span class="info-val">${w} × ${h} px</span></div>
    <div class="info-row"><span>フォーマット</span><span class="info-val">${ext}</span></div>
    <div class="info-row"><span>ファイルサイズ</span><span class="info-val">${size}</span></div>
  `;
}

// Aspect lock toggle
lockBtn.addEventListener('click', () => {
  state.aspectLocked = !state.aspectLocked;
  lockBtn.classList.toggle('active', state.aspectLocked);
  lockNote.textContent = state.aspectLocked ? 'アスペクト比: 固定中' : 'アスペクト比: 固定解除';
});

// Width/Height input sync
widthInput.addEventListener('input', () => {
  const w = parseInt(widthInput.value, 10);
  if (!isNaN(w) && w > 0 && state.aspectLocked && state.originalWidth > 0) {
    const h = Math.round(w * state.originalHeight / state.originalWidth);
    heightInput.value = String(h);
    state.targetHeight = h;
  }
  state.targetWidth = w;
});

heightInput.addEventListener('input', () => {
  const h = parseInt(heightInput.value, 10);
  if (!isNaN(h) && h > 0 && state.aspectLocked && state.originalHeight > 0) {
    const w = Math.round(h * state.originalWidth / state.originalHeight);
    widthInput.value = String(w);
    state.targetWidth = w;
  }
  state.targetHeight = h;
});

// Preset buttons
document.querySelectorAll<HTMLButtonElement>('.preset-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const w = parseInt(btn.dataset.w ?? '0', 10);
    const h = parseInt(btn.dataset.h ?? '0', 10);
    state.targetWidth = w;
    state.targetHeight = h;
    widthInput.value = String(w);
    heightInput.value = String(h);

    document.querySelectorAll('.preset-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

function clearActivePreset(): void {
  document.querySelectorAll('.preset-btn').forEach((b) => b.classList.remove('active'));
}

// Format buttons
document.querySelectorAll<HTMLButtonElement>('.format-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    state.format = btn.dataset.format ?? 'image/png';
    document.querySelectorAll('.format-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    qualityGroup.style.display = state.format === 'image/png' ? 'none' : 'block';
  });
});

// Quality slider
qualityInput.addEventListener('input', () => {
  const q = parseInt(qualityInput.value, 10);
  qualityLabel.textContent = String(q);
  state.quality = q / 100;
});

// Resize
resizeBtn.addEventListener('click', () => {
  if (!state.image) return;

  const w = parseInt(widthInput.value, 10);
  const h = parseInt(heightInput.value, 10);

  if (isNaN(w) || isNaN(h) || w <= 0 || h <= 0) {
    alert('有効な幅と高さを指定してください。');
    return;
  }

  if (w > 8192 || h > 8192) {
    alert('最大サイズは 8192px です。');
    return;
  }

  state.targetWidth = w;
  state.targetHeight = h;

  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(state.image, 0, 0, w, h);

  canvas.toBlob(
    (blob) => {
      if (!blob) return;
      state.resultBlob = blob;

      const url = URL.createObjectURL(blob);
      resultPreview.src = url;
      resultInfo.innerHTML = buildInfoHtml(w, h, blob.size, state.format);
      resultCard.classList.remove('hidden');
    },
    state.format,
    state.format === 'image/png' ? undefined : state.quality
  );
});

// Download
downloadBtn.addEventListener('click', () => {
  if (!state.resultBlob) return;

  const ext = state.format === 'image/jpeg' ? 'jpg'
    : state.format === 'image/webp' ? 'webp'
    : 'png';

  const base = state.filename.replace(/\.[^.]+$/, '');
  const name = `${base}_${state.targetWidth}x${state.targetHeight}.${ext}`;

  const url = URL.createObjectURL(state.resultBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
});
