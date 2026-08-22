---
name: zenn-article
description: Write, review, and publish technical articles for Zenn (zenn.dev) — a Japanese developer publishing platform whose articles live as Markdown files in a GitHub-linked repository. Use this skill whenever the user mentions Zenn, zenn.dev, zenn-cli, `articles/*.md`, or asks to write/draft/review/polish a 技術記事, tech blog post, or article aimed at Japanese developers — even if they only say "記事を書きたい" while sitting in a Zenn repository. Also use when checking an existing article's frontmatter, slug, topics, or Zenn-specific markdown before publishing. Do NOT use for internal docs, specs, or proposals (use doc-coauthoring), or for Qiita/note/Medium posts unless the user asks to adapt a Zenn article for them.
---

# Zenn 技術記事の執筆

Zenn は GitHub 連携でリポジトリ内の Markdown をそのまま公開するプラットフォームです。したがって成果物は常に **`articles/<slug>.md` という 1 ファイル**であり、frontmatter が壊れていれば公開自体が失敗します。書く前に形式を固め、書いた後に機械的に検証する — この順序を守ってください。

## 進め方

軽量な 4 ステップで進めます。ユーザーがすでに構成やドラフトを持っている場合は、該当ステップから合流してください。全部を律儀に踏む必要はなく、「もう書き始めていい」と言われたら Step 3 に飛んで構いません。

### Step 1: 読者とゴールを 30 秒で固める

いきなり書き始めると、誰に向けた記事か曖昧なまま前提説明が過不足になります。次の 3 点だけ確認してください（まとめて 1 回で聞く。ユーザーが既に答えている項目は聞き直さない）。

1. **想定読者** — 例: 「React は書けるが Server Components は初めての人」。技術名だけでなく「どこまで知っている人か」を引き出す
2. **読後にどうなってほしいか** — 「手元で同じ構成を再現できる」「この技術を採用すべきか判断できる」など、1 文で
3. **記事の種類** — `type: tech`（技術的な知見・解説）か `type: idea`（考え方・ポエム・意見）か

あわせて、既存記事があればトーンの参考として読ませてもらうと文体が揃います。

### Step 2: 構成案を出して合意を取る

見出し（H2 / H3）レベルの構成案を提示し、「この順番で書きますが、過不足ありますか」と確認します。ここで合意しておくと、書き上がってから章ごと書き直す事故が減ります。

構成を考えるときの型は `references/writing-style.md` を読んでください。読者の離脱ポイント、冒頭の書き方、コードと文章の比率など、Zenn / 技術記事特有の判断材料をまとめてあります。

### Step 3: 執筆する

ファイルを作成して書きます。既存の Zenn リポジトリ内であれば `articles/` に置きます。

新規記事は zenn-cli に作らせるのが確実です（slug と frontmatter が規約通りに生成されます）:

```bash
npx zenn new:article --slug my-article-slug --title "記事タイトル" --type tech --emoji 🦔
```

`npx zenn` が使えない環境なら、`references/frontmatter.md` の雛形を手で書いてください。**`published: false` で書き始めること** — 執筆途中の記事が push で公開されるのを防げます。

執筆中は Zenn 独自記法を活用します。`:::message` によるメッセージボックス、`:::details` の折りたたみ、コードブロックのファイル名表示、`@[card]` などの埋め込み — 一覧と正確な書式は **`references/syntax.md`** にあります。書く前に一度読んでください。標準 Markdown だけで書いた記事は Zenn 上で明らかに素っ気なく見えます。

書き方そのもの（文体、コードの見せ方、タイトルの付け方）は `references/writing-style.md` を参照してください。

### Step 4: 公開前チェック

書き終えたら、必ず検証スクリプトを通します。frontmatter の不備は目視では見落とします。パスはこのスキルのディレクトリからの相対です。

```bash
python <このスキルのパス>/scripts/check_article.py articles/my-article-slug.md
```

slug の文字種と長さ、topics の個数、emoji、type の値、記法の閉じ忘れ、リンク切れの疑いなどを機械的に確認します。エラーが 1 つでも残っている状態で「完成しました」と言わないでください。

続けてローカルプレビューを勧めます。埋め込みや数式は実際にレンダリングしないと崩れに気づけません:

```bash
npx zenn preview
```

最後に、余力があれば**読者テスト**を提案してください。記事本文だけを渡した新しい Claude（サブエージェント、または別会話）に、想定読者が抱きそうな質問を 5 個ぶつけます。著者には自明で読者には伝わらない箇所が、ここで一番よく見つかります。ただしサブエージェントの起動はユーザーの同意を取ってから行ってください。

公開は `published: true` に変えて push するだけです。**このフラグの変更と push はユーザーの明示的な指示があるまで行わないでください** — 公開は取り消しの効きにくい外向きの操作です。

## 判断に迷ったとき

- **タイトルと emoji** — 決め打ちせず 3 案ほど出して選んでもらう。emoji は記事一覧でのアイキャッチになるため、内容と結びつくものを選ぶ
- **topics** — 最大 5 個。Zenn 上で既存タグと表記が一致していないと検索に乗らないので、`React` `TypeScript` のような一般的な表記に寄せる
- **記事が長くなりすぎたら** — 分割を提案する。1 記事 1 テーマのほうが読まれます
- **画像** — リポジトリ管理なら `/images/<slug>/foo.png` に置いて `![](/images/<slug>/foo.png)` で参照。Zenn のアップローダーを使う場合は絶対 URL になります

## 参照ファイル

| ファイル | 読むタイミング |
|---|---|
| `references/syntax.md` | 執筆前。Zenn 独自記法の完全な一覧 |
| `references/frontmatter.md` | frontmatter を手書きするとき、slug や topics の規約を確認するとき |
| `references/writing-style.md` | 構成を考えるとき、文体や見せ方に迷ったとき |
| `scripts/check_article.py` | 書き終えたあと必ず |
