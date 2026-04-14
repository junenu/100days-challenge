# Day003 — JavaScript 入門クイズゲーム

## 概要

JavaScript の基本概念をターミナル上で楽しく学べる **CLI クイズゲーム** です。
8 問のクイズに回答し、60% 以上の正解で合格となります。

外部ライブラリは一切使用せず、**Node.js の標準ライブラリのみ** で構築しています。

## 技術スタック

- Language: JavaScript (Node.js)
- Framework/Library: なし（標準ライブラリのみ）
- その他: readline（標準入力）, module.exports（モジュール分割）

## 起動方法

```bash
# セットアップ（依存関係なし、インストール不要）
cd day003_quiz-game

# 実行
node index.js
```

Node.js がインストールされていれば、すぐに実行できます。

## 機能一覧

### 実装済み

- [x] JavaScript 基礎知識を問う全 8 問のクイズ
- [x] 毎回ランダムな順番で出題（Fisher-Yates シャッフル）
- [x] 不正入力時のバリデーション（クラッシュしない）
- [x] 正誤判定と即時フィードバック
- [x] 各問題の解説表示
- [x] 最終スコアと合格判定の表示
- [x] 正解率（%）の計算

### 今後の改善候補（任意）

- [ ] 難易度選択機能（初級 / 中級 / 上級）
- [ ] スコア履歴の保存（JSON ファイルへの書き込み）
- [ ] 問題カテゴリ別の出題

---

## コード解説

このプロジェクトは JavaScript 学習者向けに、コードの各部分を詳しくコメントしています。
以下では主要な概念を整理して解説します。

### ファイル構成

```
day003_quiz-game/
├── index.js      — ゲームのメインロジック
├── questions.js  — クイズデータ（問題・選択肢・解説）
└── README.md     — このファイル
```

### questions.js — データの定義

```js
const QUIZ_QUESTIONS = [
  {
    question: "問題文",
    choices: ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
    answer: 1,          // 正解の番号（1 始まり）
    explanation: "解説",
  },
  // ...
];
module.exports = QUIZ_QUESTIONS;
```

**ポイント:**

| 概念 | 説明 |
|------|------|
| `const` | 再代入できない変数。値が変わらないデータに使う |
| `配列 []` | データを順番に並べたリスト。`arr[0]` で最初の要素を取得 |
| `オブジェクト {}` | キーと値のペアでデータを管理する構造 |
| `module.exports` | このファイルの値を他のファイルから `require()` で読み込めるようにする |

---

### index.js — ゲームロジック

#### 1. モジュールの読み込み

```js
const readline = require("readline");         // 標準ライブラリ
const QUIZ_QUESTIONS = require("./questions"); // 同フォルダのファイル
```

`require()` は Node.js でファイルやライブラリを読み込む仕組みです。
`"./"` は「このファイルと同じフォルダ」を意味します。

---

#### 2. 配列をシャッフルする関数

```js
function shuffleArray(array) {
  const shuffled = [...array]; // スプレッド構文でコピー
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]; // 分割代入で入れ替え
  }
  return shuffled;
}
```

**ポイント:**

| 構文 | 説明 |
|------|------|
| `[...array]` | スプレッド構文。配列を「コピー」する。元データを壊さないために使う |
| `Math.random()` | 0 以上 1 未満のランダムな小数を返す組み込み関数 |
| `Math.floor()` | 小数点以下を切り捨てて整数にする |
| `[a, b] = [b, a]` | 分割代入。2 変数の値を一行で入れ替えられる |

---

#### 3. Promise と非同期処理

```js
function askQuestion(rl, prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer.trim());
    });
  });
}
```

**なぜ Promise が必要か？**

ターミナルへのキーボード入力は「いつ入力されるかわからない」処理です。
JavaScript はこういった「待つ必要がある処理」を **Promise** で表現します。

```
通常の関数:  呼んだら即座に結果が返る
Promise:     「後で結果を返します」という約束を表すオブジェクト
```

`resolve()` は「処理完了、結果はこれです」と伝える関数です。

---

#### 4. async / await

```js
async function askQuizQuestion(rl, question, questionNumber) {
  // await をつけると Promise の結果が返るまで「待つ」
  const input = await askQuestion(rl, "\n番号を入力してください: ");
  // ...
}
```

`async` / `await` は Promise をよりわかりやすく書くための構文です。

```
// Promise のみで書くと:
askQuestion(rl, "?").then((input) => { ... });

// async/await で書くと（読みやすい！）:
const input = await askQuestion(rl, "?");
```

---

#### 5. 入力バリデーション

```js
while (true) {
  const input = await askQuestion(rl, "番号を入力してください (1〜4): ");
  const inputNumber = parseInt(input, 10); // 文字列 → 整数に変換

  const isValidRange = inputNumber >= 1 && inputNumber <= question.choices.length;

  if (!isNaN(inputNumber) && isValidRange) {
    // 有効な入力 → 処理を続ける
    break;
  }

  console.log("正しい番号を入力してください。"); // 無効 → 繰り返す
}
```

| 関数/演算子 | 説明 |
|------------|------|
| `parseInt(str, 10)` | 文字列を 10 進数の整数に変換する |
| `isNaN(value)` | 値が数値でない場合 `true` を返す。`!isNaN()` で「数値かどうか」を確認 |
| `&&` | 論理 AND。両方の条件が `true` のときだけ `true` |
| `while(true)` | 明示的に `break` するまで繰り返すループ |

---

#### 6. for...of ループ

```js
for (const [index, question] of questions.entries()) {
  const isCorrect = await askQuizQuestion(rl, question, index + 1);
}
```

`entries()` は配列を `[インデックス, 値]` のペアに変換します。
`for...of` はそのペアを順番に取り出すループです。

---

#### 7. try...finally

```js
try {
  // メインの処理
  for (const [index, question] of questions.entries()) { ... }
} finally {
  rl.close(); // エラーが起きても必ず実行される
}
```

`finally` に書かれた処理は、エラーが発生しても **必ず** 実行されます。
`readline` のクローズ処理のように「片付け」が必要な処理に使います。

---

### 学習の流れ

このコードを理解するための推奨ステップ：

1. `questions.js` を読んで **配列とオブジェクト** の構造を理解する
2. `index.js` の `shuffleArray()` を読んで **関数と for ループ** を理解する
3. `askQuestion()` の **Promise** の仕組みを理解する
4. `askQuizQuestion()` の **async/await** を理解する
5. `main()` で全体の流れを把握する

---

## 開発ログ

### 学んだこと

- `readline` モジュールを使ったターミナル入力の受け取り方
- Promise を使った非同期処理の設計
- Fisher-Yates シャッフルアルゴリズムの実装
- `entries()` を使った「インデックス付き for...of ループ」

### 詰まったこと・解決方法

- readline の `close()` タイミング問題 → `try...finally` で確実に閉じるよう修正
- 入力バリデーションで `NaN` 判定が必要と気づかず、文字入力でクラッシュ → `isNaN()` で対処

### 次回やってみたいこと

- JSON ファイルへのスコア永続化（`fs` モジュールの使い方）
- 問題データを外部 JSON ファイルに分離してデータと処理を完全分離
- 複数カテゴリ対応（選択式でジャンルを選べるように）
