# frontmatter と リポジトリ規約

## 雛形

```yaml
---
title: "記事タイトル"
emoji: "🦔"
type: "tech" # tech: 技術記事 / idea: アイデア記事
topics: ["react", "typescript"]
published: false
---
```

`npx zenn new:article` を使えばこの形で生成されます。手書きするのは CLI が使えない環境のときだけにしてください。

## 各フィールド

| フィールド | 必須 | 制約 |
|---|---|---|
| `title` | ✅ | 記事タイトル。長すぎると一覧で省略されるので 60 文字程度まで |
| `emoji` | ✅ | **絵文字 1 文字**。記事一覧のアイキャッチになる |
| `type` | ✅ | `tech` か `idea` のどちらか。それ以外の値は不可 |
| `topics` | ✅ | 配列。**最大 5 個**。Zenn 上の既存タグと表記を揃えると検索に乗る |
| `published` | ✅ | `true` / `false`。執筆中は `false` |
| `published_at` | – | `YYYY-MM-DD` または `YYYY-MM-DD hh:mm`（JST）。予約投稿用。**公開後は変更不可** |
| `publication_name` | – | Publication に紐づけて公開する場合のみ |

## slug（ファイル名）

`articles/<slug>.md` の `<slug>` が記事 URL（`https://zenn.dev/<user>/articles/<slug>`）になります。

- **文字種**: 半角小文字 `a-z`、数字 `0-9`、ハイフン `-`、アンダースコア `_` のみ
- **長さ**: 12〜50 文字
- **一意性**: 同じユーザーの記事内で重複不可
- **日本語不可**

内容が推測できる英語の slug にしてください（例: `nextjs-rsc-cache-pitfalls`）。**公開後に slug を変えると URL が変わり、既存のリンクが切れます。**

## ディレクトリ構成

```
.
├── articles/
│   └── nextjs-rsc-cache-pitfalls.md
├── images/
│   └── nextjs-rsc-cache-pitfalls/
│       └── flow.png
└── books/
```

## CLI コマンド

```bash
npx zenn init                    # リポジトリの初期化（初回のみ）
npx zenn new:article             # 対話的に記事を作成
npx zenn new:article --slug my-article-slug --title "タイトル" --type tech --emoji 🦔
npx zenn preview                 # ローカルプレビュー（--port 3000 で変更可）
```

## 公開

`published: true` にして GitHub にプッシュすると公開されます。記事に関係ないコミットでデプロイを走らせたくない場合は、コミットメッセージに `[skip ci]` を含めます。

公開は取り消しの効きにくい操作です。`published` の切り替えと push は、ユーザーが明示的に指示したときだけ行ってください。
