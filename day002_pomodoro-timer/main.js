#!/usr/bin/env node

'use strict';

const readline = require('readline');

// ─── 設定 ────────────────────────────────────────────────────────────────────

// [HIGH fix] NaN 検証: 不正な環境変数値はデフォルト値にフォールバック
function parsePositiveInt(value, defaultValue) {
  const n = parseInt(value, 10);
  return Number.isFinite(n) && n > 0 ? n : defaultValue;
}

const CONFIG = {
  WORK_MINUTES: parsePositiveInt(process.env.WORK_MINUTES, 25),
  SHORT_BREAK_MINUTES: parsePositiveInt(process.env.SHORT_BREAK_MINUTES, 5),
  LONG_BREAK_MINUTES: parsePositiveInt(process.env.LONG_BREAK_MINUTES, 15),
  LONG_BREAK_AFTER: 4,
  PROGRESS_BAR_WIDTH: 30,
};

// ─── ANSI カラー定義 ──────────────────────────────────────────────────────────

const COLOR = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgBlue: '\x1b[44m',
};

// ─── セッション種別 ───────────────────────────────────────────────────────────

const SESSION = {
  WORK: 'work',
  SHORT_BREAK: 'short_break',
  LONG_BREAK: 'long_break',
};

// ─── ユーティリティ ───────────────────────────────────────────────────────────

function clearScreen() {
  process.stdout.write('\x1b[2J\x1b[H');
}

function colorize(text, ...codes) {
  return codes.join('') + text + COLOR.reset;
}

// [LOW fix] padStart は formatTime 内でインライン化（1 箇所のみ使用）
function formatTime(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function buildProgressBar(elapsed, total) {
  const width = CONFIG.PROGRESS_BAR_WIDTH;
  const filled = Math.round((elapsed / total) * width);
  const empty = width - filled;
  const bar = '█'.repeat(filled) + '░'.repeat(empty);
  return `[${bar}]`;
}

function formatPercent(elapsed, total) {
  return `${Math.round((elapsed / total) * 100)}%`;
}

// ─── 状態管理 ─────────────────────────────────────────────────────────────────

function createState() {
  return {
    session: SESSION.WORK,
    completedPomodoros: 0,
    remainingSeconds: CONFIG.WORK_MINUTES * 60,
    totalSeconds: CONFIG.WORK_MINUTES * 60,
    running: true,
    paused: false,
  };
}

function nextSession(state) {
  const newCompleted =
    state.session === SESSION.WORK
      ? state.completedPomodoros + 1
      : state.completedPomodoros;

  if (state.session === SESSION.WORK) {
    const isLongBreak = newCompleted % CONFIG.LONG_BREAK_AFTER === 0;
    const nextSessionType = isLongBreak ? SESSION.LONG_BREAK : SESSION.SHORT_BREAK;
    const minutes = isLongBreak
      ? CONFIG.LONG_BREAK_MINUTES
      : CONFIG.SHORT_BREAK_MINUTES;
    return {
      ...state,
      session: nextSessionType,
      completedPomodoros: newCompleted,
      remainingSeconds: minutes * 60,
      totalSeconds: minutes * 60,
      paused: false,
    };
  }

  return {
    ...state,
    session: SESSION.WORK,
    completedPomodoros: newCompleted,
    remainingSeconds: CONFIG.WORK_MINUTES * 60,
    totalSeconds: CONFIG.WORK_MINUTES * 60,
    paused: false,
  };
}

// ─── 表示 ─────────────────────────────────────────────────────────────────────

// [MEDIUM fix] default ケースを追加して未知のセッション種別でも安全に動作
function sessionLabel(session) {
  switch (session) {
    case SESSION.WORK:
      return colorize(' 🍅 作業中 ', COLOR.bold, COLOR.bgRed, COLOR.white);
    case SESSION.SHORT_BREAK:
      return colorize(' ☕ 短い休憩 ', COLOR.bold, COLOR.bgGreen, COLOR.white);
    case SESSION.LONG_BREAK:
      return colorize(' 🌿 長い休憩 ', COLOR.bold, COLOR.bgBlue, COLOR.white);
    default:
      return colorize(` ${session} `, COLOR.bold);
  }
}

function sessionColor(session) {
  switch (session) {
    case SESSION.WORK:
      return COLOR.red;
    case SESSION.SHORT_BREAK:
      return COLOR.green;
    case SESSION.LONG_BREAK:
      return COLOR.blue;
    default:
      return COLOR.white;
  }
}

// [LOW fix] Array.from で慣用的に記述
// [LOW fix] 4 個完了時（長い休憩に入るタイミング）は全部 🍅 を表示
function renderPomodoroDots(count) {
  const progress = count % CONFIG.LONG_BREAK_AFTER || (count > 0 ? CONFIG.LONG_BREAK_AFTER : 0);
  return Array.from(
    { length: CONFIG.LONG_BREAK_AFTER },
    (_, i) => i < progress ? '🍅' : '○'
  ).join(' ');
}

function render(state) {
  clearScreen();
  const elapsed = state.totalSeconds - state.remainingSeconds;
  const color = sessionColor(state.session);

  console.log('');
  console.log(colorize('  ╔══════════════════════════════════════╗', color));
  console.log(colorize('  ║        🍅  Pomodoro Timer  🍅         ║', color));
  console.log(colorize('  ╚══════════════════════════════════════╝', color));
  console.log('');
  console.log(`  セッション: ${sessionLabel(state.session)}`);
  console.log('');
  console.log(
    `  時間: ${colorize(formatTime(state.remainingSeconds), COLOR.bold, color)}`
  );
  console.log('');
  console.log(
    `  ${colorize(buildProgressBar(elapsed, state.totalSeconds), color)} ${formatPercent(elapsed, state.totalSeconds)}`
  );
  console.log('');
  console.log(
    `  完了ポモドーロ: ${colorize(String(state.completedPomodoros), COLOR.bold, COLOR.cyan)} 個`
  );
  console.log(`  進捗: ${renderPomodoroDots(state.completedPomodoros)}`);
  console.log('');

  if (state.paused) {
    console.log(colorize('  ⏸  一時停止中', COLOR.bold, COLOR.yellow));
  }

  console.log('');
  console.log(colorize('  操作:', COLOR.bold));
  console.log('    [Space] / [p] — 一時停止 / 再開');
  console.log('    [s]          — スキップ（次のセッションへ）');
  console.log('    [q] / [Ctrl+C] — 終了');
  console.log('');
}

function renderComplete(session) {
  clearScreen();
  console.log('');
  if (session === SESSION.WORK) {
    console.log(colorize('  ✅ 作業セッション完了！お疲れさまです。', COLOR.bold, COLOR.green));
  } else {
    console.log(colorize('  ✅ 休憩終了！作業を再開しましょう。', COLOR.bold, COLOR.cyan));
  }
  console.log('');
  console.log('  次のセッションを開始します...');
  console.log('');
}

function renderFinal(completedPomodoros) {
  clearScreen();
  console.log('');
  console.log(colorize('  ╔══════════════════════════════════════╗', COLOR.cyan));
  console.log(colorize('  ║           終了しました 👋              ║', COLOR.cyan));
  console.log(colorize('  ╚══════════════════════════════════════╝', COLOR.cyan));
  console.log('');
  console.log(
    `  今日完了したポモドーロ: ${colorize(String(completedPomodoros), COLOR.bold, COLOR.cyan)} 個`
  );
  console.log('');
}

// ─── メインループ ─────────────────────────────────────────────────────────────

function run() {
  // [MEDIUM fix] 非 TTY 環境（パイプ・CI）では操作不能になるため早期終了
  if (!process.stdin.isTTY) {
    console.error('Error: このツールはインタラクティブな TTY 環境でのみ使用できます。');
    process.exit(1);
  }

  let state = createState();

  // stdin をキャラクター入力モードに設定
  readline.emitKeypressEvents(process.stdin);
  process.stdin.setRawMode(true);

  let tickInterval = null;
  // [HIGH fix] セッション完了後の遷移タイマーを保持（skipSession でキャンセル可能にする）
  let pendingTransitionId = null;

  function startTick() {
    if (tickInterval) return;
    tickInterval = setInterval(() => {
      if (state.paused || !state.running) return;

      state = { ...state, remainingSeconds: state.remainingSeconds - 1 };
      render(state);

      if (state.remainingSeconds <= 0) {
        clearInterval(tickInterval);
        tickInterval = null;
        handleSessionComplete();
      }
    }, 1000);
  }

  function stopTick() {
    if (tickInterval) {
      clearInterval(tickInterval);
      tickInterval = null;
    }
  }

  function handleSessionComplete() {
    renderComplete(state.session);
    // [HIGH fix] ID を保持して skipSession からキャンセルできるようにする
    pendingTransitionId = setTimeout(() => {
      pendingTransitionId = null;
      state = nextSession(state);
      render(state);
      startTick();
    }, 2000);
  }

  function skipSession() {
    // [HIGH fix] 完了待機中の遷移タイマーをキャンセルして二重遷移を防ぐ
    if (pendingTransitionId) {
      clearTimeout(pendingTransitionId);
      pendingTransitionId = null;
    }
    stopTick();
    state = nextSession(state);
    render(state);
    startTick();
  }

  function quit() {
    if (pendingTransitionId) {
      clearTimeout(pendingTransitionId);
      pendingTransitionId = null;
    }
    stopTick();
    state = { ...state, running: false };
    process.stdin.setRawMode(false);
    renderFinal(state.completedPomodoros);
    process.exit(0);
  }

  // キー入力ハンドラ
  process.stdin.on('keypress', (_str, key) => {
    if (!key) return;

    // Ctrl+C または q で終了
    if ((key.ctrl && key.name === 'c') || key.name === 'q') {
      quit();
      return;
    }

    // スペースまたは p で一時停止 / 再開
    if (key.name === 'space' || key.name === 'p') {
      state = { ...state, paused: !state.paused };
      render(state);
      return;
    }

    // s でスキップ
    if (key.name === 's') {
      skipSession();
      return;
    }
  });

  // 初期表示 & タイマー開始
  render(state);
  startTick();
}

// ─── エントリポイント ─────────────────────────────────────────────────────────

run();
