/**
 * index.js — クイズゲームのメインファイル
 *
 * 【このファイルで学べること】
 * 1. require()  — 別ファイルのコードを読み込む方法
 * 2. readline   — ターミナルでキーボード入力を受け取る方法
 * 3. Promise    — 非同期処理（待つ処理）の書き方
 * 4. async/await — 非同期処理をわかりやすく書く方法
 * 5. 関数        — 処理をまとめて再利用する方法
 * 6. for...of   — 配列を順番に処理するループ
 */

// ===== モジュールの読み込み =====

// require() で別ファイルや標準ライブラリを読み込みます
const readline = require("readline"); // キーボード入力を扱う標準ライブラリ
const QUIZ_QUESTIONS = require("./questions"); // 同じフォルダの questions.js を読み込む

// ===== 定数の定義 =====

const TOTAL_QUESTIONS = QUIZ_QUESTIONS.length; // 問題数
const PASS_SCORE = Math.ceil(TOTAL_QUESTIONS * 0.6); // 合格ライン（60%以上）

// ===== ユーティリティ関数 =====

/**
 * ターミナルに区切り線を表示する関数
 * （関数は「処理に名前をつけて何度でも呼び出せる」仕組みです）
 */
function printDivider() {
  console.log("─".repeat(50));
}

/**
 * 配列をランダムな順番に並び替える関数（Fisher-Yates シャッフル）
 *
 * 【学習ポイント】
 * - [...array] で配列をコピーしています（元のデータを変えないための工夫）
 * - Math.random() は 0 以上 1 未満のランダムな数値を返します
 * - Math.floor() は小数点以下を切り捨てます
 *
 * @param {Array} array - シャッフルしたい配列
 * @returns {Array} - シャッフルされた新しい配列
 */
function shuffleArray(array) {
  const shuffled = [...array]; // 元の配列をコピー（スプレッド構文）
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    // 分割代入で 2 つの変数を同時に入れ替える
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

/**
 * ユーザーの入力を 1 行受け取る関数（Promise を使った非同期処理）
 *
 * 【学習ポイント】
 * - Promise: 「後で結果が返ってくる」処理を表すオブジェクト
 * - resolve(): 処理成功時に呼ぶ関数（return のようなもの）
 * - readline: ターミナルから 1 行のテキストを受け取る仕組み
 *
 * @param {readline.Interface} rl - readline のインターフェース
 * @param {string} prompt - 表示するプロンプト（「?」のような記号）
 * @returns {Promise<string>} - 入力された文字列
 */
function askQuestion(rl, prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer.trim()); // trim() で前後の空白を除去
    });
  });
}

// ===== クイズのコア機能 =====

/**
 * 1 問を出題して正誤を判定する関数
 *
 * 【学習ポイント】
 * - async 関数: 内部で await を使える関数
 * - await: Promise の結果が返るまで待つキーワード
 * - template literal: `${変数}` で文字列に変数を埋め込む方法
 *
 * @param {readline.Interface} rl
 * @param {Object} question - 問題オブジェクト（questions.js の 1 要素）
 * @param {number} questionNumber - 問題番号（1 始まり）
 * @returns {Promise<boolean>} - 正解なら true、不正解なら false
 */
async function askQuizQuestion(rl, question, questionNumber) {
  printDivider();

  // 問題番号と問題文を表示（template literal を使って変数を埋め込む）
  console.log(`\n問題 ${questionNumber}/${TOTAL_QUESTIONS}`);
  console.log(`\n${question.question}\n`);

  // 選択肢を表示
  // forEach は配列の各要素に対して処理を行うメソッド
  // (choice, index) で「値」と「番号」を同時に取得
  question.choices.forEach((choice, index) => {
    console.log(`  ${index + 1}. ${choice}`); // index は 0 始まりなので +1 する
  });

  // 入力バリデーションのループ
  // while(true) で「条件が満たされるまで繰り返す」
  while (true) {
    const input = await askQuestion(rl, "\n番号を入力してください (1〜4): ");
    const inputNumber = parseInt(input, 10); // 文字列を整数に変換（10 進数）

    // isNaN(): 数値でないかどうかを確認する関数
    const isValidRange =
      inputNumber >= 1 && inputNumber <= question.choices.length;

    if (!isNaN(inputNumber) && isValidRange) {
      // 正誤判定
      const isCorrect = inputNumber === question.answer;

      if (isCorrect) {
        console.log("\n✓ 正解！");
      } else {
        // 不正解の場合は正解の選択肢を表示
        const correctChoice = question.choices[question.answer - 1]; // -1 で 0 始まりに変換
        console.log(`\n✗ 不正解... 正解は「${correctChoice}」でした`);
      }

      // 解説を表示
      console.log(`\n📖 解説: ${question.explanation}\n`);

      return isCorrect; // 関数の戻り値（true or false）
    }

    // 不正な入力の場合はやり直し
    console.log(
      `1〜${question.choices.length} の番号を入力してください。`
    );
  }
}

/**
 * 最終結果を表示する関数
 *
 * @param {number} score - 正解数
 * @param {number} total - 総問題数
 */
function showResult(score, total) {
  printDivider();
  console.log("\n===== 結果発表 =====\n");

  const percentage = Math.round((score / total) * 100); // 正解率（小数点なし）

  console.log(`正解数: ${score} / ${total}`);
  console.log(`正解率: ${percentage}%`);

  // 条件分岐（if / else if / else）でメッセージを切り替える
  if (score === total) {
    console.log("\n🎉 満点！完璧です！");
  } else if (score >= PASS_SCORE) {
    console.log("\n👏 合格！よくできました！");
  } else {
    console.log("\n📚 もう一度チャレンジしてみましょう！");
  }

  console.log("");
  printDivider();
}

// ===== メイン処理 =====

/**
 * ゲーム全体を制御するメイン関数
 *
 * 【学習ポイント】
 * - async function: 非同期処理を含む関数
 * - for...of: 配列の各要素を順番に処理するループ
 * - try...finally: エラーが起きても必ず実行する処理
 */
async function main() {
  // readline インターフェースを作成（入出力の設定）
  const rl = readline.createInterface({
    input: process.stdin, // 入力元: キーボード
    output: process.stdout, // 出力先: ターミナル
  });

  // タイトルを表示
  console.log("\n");
  printDivider();
  console.log("   🧠 JavaScript 入門クイズ");
  console.log(`   全 ${TOTAL_QUESTIONS} 問 | 合格ライン: ${PASS_SCORE} 問以上`);
  printDivider();
  console.log("\nスペースキー or Enterを押してスタート...");

  await askQuestion(rl, "");

  // 問題をシャッフル（毎回違う順番で出題）
  const questions = shuffleArray(QUIZ_QUESTIONS);

  let score = 0; // 正解数を記録する変数（let は後から値を変えられる）

  // try...finally: エラーが起きても finally の中は必ず実行される
  try {
    // for...of で配列の各要素を順番に取り出す
    for (const [index, question] of questions.entries()) {
      // entries() でインデックスと値を同時に取得
      const isCorrect = await askQuizQuestion(rl, question, index + 1);

      if (isCorrect) {
        score++; // 正解なら score を 1 増やす（score = score + 1 の省略形）
      }
    }

    showResult(score, TOTAL_QUESTIONS);
  } finally {
    // readline を必ず閉じる（リソースの解放）
    rl.close();
  }
}

// ===== エントリーポイント =====
// main() を呼び出してゲームを開始
// .catch() でエラーが起きた場合の処理を書く
main().catch((error) => {
  console.error("エラーが発生しました:", error.message);
  process.exit(1); // エラーコード 1 で終了
});
