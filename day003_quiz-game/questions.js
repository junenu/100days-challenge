/**
 * questions.js — クイズデータファイル
 *
 * 【学習ポイント】
 * - 配列（Array）: [] で囲まれたデータの集まり
 * - オブジェクト（Object）: {} で囲まれたキーと値のペア
 * - 定数（const）: 再代入できない変数
 * - module.exports: このファイルの内容を他のファイルから使えるようにする
 */

// QUIZ_QUESTIONS は「配列」です。
// 配列の各要素が「オブジェクト」になっています。
// 各オブジェクトは 1 問のクイズを表します。
const QUIZ_QUESTIONS = [
  {
    // question: 問題文（文字列）
    question: "JavaScriptで変数を宣言するキーワードはどれ？",
    // choices: 選択肢（文字列の配列）
    choices: ["var", "let", "const", "全部正解"],
    // answer: 正解の選択肢番号（1 始まり）
    answer: 4,
    // explanation: 解説文
    explanation:
      "var / let / const はどれも変数宣言に使えます。" +
      "ただし現代のJSではletとconstを使うのが主流です。",
  },
  {
    question: "次のうち、JavaScriptの「配列」を表すのはどれ？",
    choices: ["{ name: 'Alice' }", "[ 1, 2, 3 ]", "( 1, 2, 3 )", '"hello"'],
    answer: 2,
    explanation:
      "配列は [ ] で囲みます。{ } はオブジェクト、( ) はグループ化や関数呼び出し、\"\" は文字列です。",
  },
  {
    question: "console.log('Hello') の出力結果は？",
    choices: ["Hello", '"Hello"', "undefined", "エラーになる"],
    answer: 1,
    explanation:
      "console.log() は引数をコンソールに表示します。" +
      "文字列を渡すとクォートなしで表示されます。",
  },
  {
    question: "JavaScriptで関数を定義する方法として正しいのはどれ？",
    choices: [
      "function greet() {}",
      "const greet = () => {}",
      "const greet = function() {}",
      "全部正解",
    ],
    answer: 4,
    explanation:
      "JavaScriptには関数定義の方法が複数あります。" +
      "どれも有効ですが、用途によって使い分けます。",
  },
  {
    question: "次のコード「2 + '3'」の結果は？\n(ヒント: 数値 + 文字列)",
    choices: ["5", '"23"', "エラー", "NaN"],
    answer: 2,
    explanation:
      "数値と文字列を + で結合すると、数値が文字列に変換されて文字列結合されます。" +
      "結果は文字列の '23' になります。これを「型変換」と呼びます。",
  },
  {
    question: "if文の条件として「falsy（偽）」になる値はどれ？",
    choices: ["0", '""（空文字）', "null", "全部正解"],
    answer: 4,
    explanation:
      "0、空文字、null、undefined、false、NaN はすべて falsy です。" +
      "これら以外の値は truthy（真）として扱われます。",
  },
  {
    question: "配列 [10, 20, 30] の最初の要素を取得するコードは？",
    choices: ["arr[0]", "arr[1]", "arr.first()", "arr.get(0)"],
    answer: 1,
    explanation:
      "配列のインデックス（番号）は 0 から始まります。" +
      "最初の要素は arr[0]、2番目は arr[1] で取得できます。",
  },
  {
    question: "=== と == の違いは？",
    choices: [
      "違いはない",
      "=== は型も比較する",
      "== は型も比較する",
      "=== は代入に使う",
    ],
    answer: 2,
    explanation:
      "== は値だけを比較（型変換あり）、=== は値と型を両方比較します。" +
      "例: 1 == '1' は true、1 === '1' は false。基本的に === を使いましょう。",
  },
];

// このファイルを他のファイルから import できるようにする
module.exports = QUIZ_QUESTIONS;
