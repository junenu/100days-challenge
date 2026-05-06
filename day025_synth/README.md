# Day025 — SYNTH25

## 概要

Web Audio API を使ったブラウザ動作のポリフォニック・シンセサイザー。
仮想ピアノ鍵盤（C4〜E5）でリアルタイム音声合成ができ、波形・ADSR エンベロープ・エフェクトをインタラクティブに調整できる。

## 技術スタック

- Language: TypeScript
- Framework/Library: Vite (バンドラー)
- Audio: Web Audio API（OscillatorNode, GainNode, DelayNode, ConvolverNode, AnalyserNode）
- Rendering: Canvas API（オシロスコープ）

## 起動方法

```bash
# セットアップ
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build
```

ブラウザで `http://localhost:5173` を開く。

## 機能一覧

### 実装済み

- [x] 仮想ピアノ鍵盤（C4〜E5、白鍵 10 鍵 + 黒鍵 7 鍵）
- [x] キーボード入力（`A`–`;` = 白鍵、`W E T Y U O P` = 黒鍵）
- [x] マウス / タッチ入力でノートオン・オフ
- [x] 4 種類の波形（sine / square / sawtooth / triangle）
- [x] ADSR エンベロープ制御（Attack / Decay / Sustain / Release）
- [x] ディレイエフェクト（Delay Time / Delay Feedback）
- [x] リバーブエフェクト（コンボルバーによる空間感）
- [x] マスターボリューム制御
- [x] リアルタイム・オシロスコープ表示（Canvas + AnalyserNode）
- [x] ポリフォニック発音（複数ノートの同時発音対応）

### 今後の改善候補（任意）

- [ ] プリセット保存・読み込み
- [ ] MIDIキーボード入力対応
- [ ] フィルター（ローパス / ハイパス）
- [ ] LFO モジュレーション
- [ ] FFT スペクトラム表示

## 操作方法

| 操作 | 内容 |
|------|------|
| `A` `S` `D` `F` `G` `H` `J` `K` `L` `;` | C4〜E5 の白鍵 |
| `W` `E` `T` `Y` `U` `O` `P` | C#4 D#4 F#4 G#4 A#4 C#5 D#5 の黒鍵 |
| マウスクリック（ドラッグ可）| 鍵盤を押す / 離す |
| Oscillator ボタン | 波形を切り替え |
| ADSR スライダー | エンベロープを調整 |
| Effects スライダー | ディレイ・リバーブを調整 |

## 開発ログ

### 学んだこと

- `AudioContext` の `OscillatorNode` → `GainNode` → エフェクト → `AnalyserNode` → `destination` のルーティング
- ADSR エンベロープは `linearRampToValueAtTime` で滑らかに制御できる
- `ConvolverNode` に指数減衰ホワイトノイズを使うと安価なリバーブが実現できる
- `AnalyserNode.getFloatTimeDomainData()` で Canvas にリアルタイム波形を描画できる
- Web Audio API は最初のユーザーインタラクションまで `suspended` 状態になる

### 詰まったこと・解決方法

- Canvas への`Float32Array`の型エラー → `as Float32Array<ArrayBuffer>` でキャスト
- Keyboard クラスがコンテナの className を上書きしていた → `this.container.className = 'keyboard'` を削除して修正
- 絶対位置指定の鍵盤が親要素を突き抜けていた → `.keyboard-wrap` に `overflow: hidden` と `position: relative` を設定

### 次回やってみたいこと

- Rust + ratatui でターミナル TUI アプリに挑戦
