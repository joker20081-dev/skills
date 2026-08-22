#!/usr/bin/env python3
"""Zenn 記事の公開前チェック。

Usage:
    python check_article.py articles/my-article-slug.md [more.md ...]

frontmatter の規約違反 (ERROR) と、公開前に見直したい点 (WARN) を報告する。
ERROR が 1 件でもあれば終了コード 1。標準ライブラリのみで動作する。
"""

import os
import re
import sys

SLUG_RE = re.compile(r"^[a-z0-9_-]{12,50}$")
PUBLISHED_AT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
CONTAINER_RE = re.compile(r"^(:{3,})\s*(\S*)")
IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)")
REQUIRED = ("title", "emoji", "type", "topics", "published")

# 絵文字 1 文字判定で無視する結合用コードポイント（異体字セレクタ・ZWJ・キーキャップ）
IGNORABLE = {0xFE0F, 0xFE0E, 0x200D, 0x20E3}


def parse_frontmatter(lines):
    """先頭の --- ブロックを {key: raw_value} と本文開始行に分解する。"""
    if not lines or lines[0].strip() != "---":
        return None, 0
    body_start = 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body_start = i + 1
            break
    if not body_start:
        return None, 0

    data = {}
    for line in lines[1:body_start - 1]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = strip_comment(value.strip())
    return data, body_start


def strip_comment(value):
    """値の後ろに付いた # コメントを落とす。引用符の内側の # は残す。"""
    if value.startswith(("'", '"')):
        quote = value[0]
        end = value.find(quote, 1)
        if end == -1:
            return value
        return value[:end + 1]
    return value.split("#", 1)[0].strip()


def unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_list(value):
    value = value.strip()
    if not value.startswith("["):
        return None
    inner = value[1:-1] if value.endswith("]") else value[1:]
    return [unquote(item.strip()) for item in inner.split(",") if item.strip()]


def emoji_length(value):
    """結合文字・肌色修飾子を除いたコードポイント数。絵文字 1 文字なら 1。"""
    return sum(
        1
        for ch in value
        if ord(ch) not in IGNORABLE and not (0x1F3FB <= ord(ch) <= 0x1F3FF)
    )


def check_frontmatter(fm, errors, warnings):
    for key in REQUIRED:
        if key not in fm:
            errors.append("frontmatter に必須フィールド `{}` がありません".format(key))

    title = unquote(fm.get("title", ""))
    if "title" in fm and not title:
        errors.append("`title` が空です")
    elif len(title) > 60:
        warnings.append(
            "`title` が {} 文字あります。一覧で省略される可能性があります（60 文字程度まで推奨）".format(len(title))
        )

    if "emoji" in fm:
        emoji = unquote(fm["emoji"])
        if not emoji:
            errors.append("`emoji` が空です")
        elif emoji.isascii():
            errors.append("`emoji` に絵文字以外が指定されています: {!r}".format(emoji))
        elif emoji_length(emoji) != 1:
            errors.append(
                "`emoji` は絵文字 1 文字にしてください（現在 {} 文字分）: {}".format(emoji_length(emoji), emoji)
            )

    if "type" in fm:
        article_type = unquote(fm["type"])
        if article_type not in ("tech", "idea"):
            errors.append("`type` は tech か idea のみ有効です（現在: {!r}）".format(article_type))

    if "topics" in fm:
        topics = parse_list(fm["topics"])
        if topics is None:
            errors.append('`topics` は配列で指定してください（例: ["react", "typescript"]）')
        elif not topics:
            errors.append("`topics` が空です。1 つ以上指定しないと検索に乗りません")
        elif len(topics) > 5:
            errors.append("`topics` は最大 5 個です（現在 {} 個）".format(len(topics)))
        else:
            for topic in topics:
                if not topic.isascii():
                    warnings.append(
                        "topic `{}` は日本語です。Zenn の既存タグと一致するか確認してください".format(topic)
                    )
                elif topic != topic.lower():
                    warnings.append(
                        "topic `{}` に大文字が含まれます。Zenn 上の表記と揃っているか確認してください".format(topic)
                    )

    if "published" in fm:
        published = unquote(fm["published"]).lower()
        if published not in ("true", "false"):
            errors.append("`published` は true か false です（現在: {!r}）".format(fm["published"]))
        elif published == "false":
            warnings.append("`published: false` です。公開するときは true に変更して push してください")

    if "published_at" in fm:
        published_at = unquote(fm["published_at"])
        if not PUBLISHED_AT_RE.match(published_at):
            errors.append(
                "`published_at` の形式が不正です（YYYY-MM-DD または YYYY-MM-DD hh:mm）: {!r}".format(published_at)
            )


def check_body(lines, body_start, errors, warnings):
    fence = None      # 現在開いているコードフェンス
    containers = []   # [(コロン数, 名前, 行番号)]

    for offset, raw in enumerate(lines[body_start:]):
        lineno = body_start + offset + 1
        line = raw.rstrip("\n")

        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue

        container_match = CONTAINER_RE.match(line)
        if container_match:
            colons, name = container_match.group(1), container_match.group(2)
            if name:
                containers.append((len(colons), name, lineno))
            elif containers:
                depth, _, open_line = containers.pop()
                if depth != len(colons):
                    errors.append(
                        "L{}: 閉じるコロンの数が合いません（{} 個で閉じようとしていますが、"
                        "L{} は {} 個で開いています）".format(lineno, len(colons), open_line, depth)
                    )
            else:
                errors.append("L{}: 対応する開始がない `{}` です".format(lineno, colons))
            continue

        if line.startswith("# "):
            warnings.append(
                "L{}: 本文に H1 見出しがあります。タイトルは frontmatter の `title` なので H2 から始めてください".format(lineno)
            )

        for match in IMAGE_RE.finditer(line):
            alt, src = match.group("alt"), match.group("src")
            if not alt.strip():
                warnings.append("L{}: 画像に代替テキストがありません: {}".format(lineno, src))
            if src.startswith(("./images", "images/", "../")):
                errors.append(
                    "L{}: 画像パスは先頭スラッシュ付きの /images/... にしてください: {}".format(lineno, src)
                )

        if re.search(r"\bTODO\b|\bFIXME\b|TBD", line):
            warnings.append("L{}: 未完成のマーカーが残っています: {}".format(lineno, line.strip()[:60]))

        if re.search(r"\(http://(?!localhost|127\.0\.0\.1)", line):
            warnings.append("L{}: http:// のリンクがあります。https に変えられないか確認してください".format(lineno))

    if fence is not None:
        errors.append("コードブロックが閉じられていません")
    for depth, name, lineno in containers:
        errors.append("L{}: `{}{}` が閉じられていません".format(lineno, ":" * depth, name))

    if not any(l.startswith("## ") for l in lines[body_start:]):
        warnings.append("見出し（##）が 1 つもありません。長い記事は読者が現在地を見失います")


def check_file(path):
    errors, warnings = [], []
    filename = os.path.basename(path)
    slug = filename[:-3] if filename.endswith(".md") else filename

    if not SLUG_RE.match(slug):
        errors.append(
            "slug（ファイル名）`{}` が規約違反です。"
            "半角小文字・数字・ハイフン・アンダースコアのみ、12〜50 文字".format(slug)
        )
    parent = os.path.basename(os.path.dirname(os.path.abspath(path)))
    if parent != "articles":
        warnings.append(
            "`articles/` 直下にありません（現在: {}/）。Zenn は articles/ 配下のみ記事として認識します".format(parent)
        )

    with open(path, encoding="utf-8") as handle:
        lines = handle.readlines()

    fm, body_start = parse_frontmatter(lines)
    if fm is None:
        errors.append("frontmatter（先頭の --- で囲まれたブロック）が見つかりません")
    else:
        check_frontmatter(fm, errors, warnings)
        check_body(lines, body_start, errors, warnings)

        body_chars = sum(len(l) for l in lines[body_start:])
        if body_chars < 500:
            warnings.append("本文が {} 文字と短めです。書きかけでないか確認してください".format(body_chars))

    return errors, warnings


def main(argv):
    # Windows の既定コードページ (cp932) だと絵文字の出力で落ちるため UTF-8 に固定する
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    if len(argv) < 2:
        print(__doc__)
        return 2

    total_errors = 0
    for path in argv[1:]:
        if not os.path.isfile(path):
            print("x {}: ファイルが見つかりません".format(path))
            total_errors += 1
            continue

        errors, warnings = check_file(path)
        total_errors += len(errors)

        header = "{}  (ERROR {} / WARN {})".format(path, len(errors), len(warnings))
        print("\n{}\n{}".format(header, "-" * len(header)))
        for message in errors:
            print("  ERROR  {}".format(message))
        for message in warnings:
            print("  WARN   {}".format(message))
        if not errors and not warnings:
            print("  OK  問題は見つかりませんでした")

    print()
    if total_errors:
        print("ERROR が {} 件あります。修正してから公開してください。".format(total_errors))
        return 1
    print("ERROR はありません。`npx zenn preview` で表示を確認してください。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
