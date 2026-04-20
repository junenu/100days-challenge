# markdown-preview サンプル

ターミナルで **Markdown** をカラー整形表示する CLI ツールのサンプルです。

## 見出し

### H3 見出し

#### H4 見出し

## テキスト装飾

- **太字テキスト**
- _イタリック_
- `インラインコード`
- [リンクテキスト](https://example.com)

## リスト

### 順序なし

- りんご
- バナナ
  - 黄色いバナナ
  - 赤いバナナ
- チェリー

### 順序あり

1. 最初のステップ
2. 次のステップ
3. 最後のステップ

## コードブロック

```javascript
function greet(name) {
  const message = `Hello, ${name}!`;
  console.log(message);
  return message;
}

greet('World');
```

```bash
npm install
node src/index.js sample.md
```

## 引用

> これは引用ブロックです。
> 複数行にわたる引用も表示できます。

## テーブル

| 言語       | 型     | 主な用途         |
| ---------- | ------ | ---------------- |
| JavaScript | 動的型 | Web フロントエンド |
| TypeScript | 静的型 | 大規模 Web 開発  |
| Go         | 静的型 | サーバーサイド   |
| Python     | 動的型 | ML・スクリプト   |

## 水平線

---

## まとめ

見出し・リスト・コードブロック・テーブル・引用をカラーでレンダリングします。
