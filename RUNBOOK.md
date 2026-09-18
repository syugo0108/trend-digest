# Trend Digest — 毎朝の運用手順

毎朝7:00 JST(= 前日22:00 UTC)に send_later のリマインダーが発火する。以下を順に実施する。
無人実行なので、質問せず最後まで完遂すること。

## 0. コンテナがリセットされていたら
作業ファイルは `/home/claude/trend-digest/` 配下。消えていたら復旧する:

```
mkdir -p /home/claude/trend-digest && cd /home/claude/trend-digest
git clone --depth 5 https://github.com/syugo0108/trend-digest.git site
```

RUNBOOK.md と profile.md はこのリポジトリ直下にも入れてあるので、cloneすれば一緒に戻る。
PAT(GitHubトークン)はファイルに保存しない。会話履歴から取得してコマンド内でのみ使う。

## 1. 最初に翌朝の予約を入れる(チェーン切れ防止)
何よりも先に `mcp__claude-code-remote__send_later` で翌日22:00 UTC の同じリマインダーを予約する。
これを忘れると連鎖が止まる。

## 2. ソース収集(必ず WebFetch を使う)
bash/python での HTTP は proxy に 403 で塞がれている。WebFetch のみ。
URL 末尾に `&_=YYYYMMDD` を付けてキャッシュを回避する。

- Hacker News: `https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30`
- Zenn: `https://zenn.dev/api/articles?order=daily`
- はてなブックマーク: `https://b.hatena.ne.jp/hotentry/it` (宛先URLも一緒に取得させる)
- Qiita: `https://qiita.com/` (APIは robots で不可)
- Techmeme: `https://www.techmeme.com/feed.xml` (permalink も一緒に取得させる)
- HF Daily Papers: `https://huggingface.co/api/daily_papers?limit=20`
- dev.to: `https://dev.to/api/articles?top=1&per_page=25`

取得不可・恒常的に除外: Lobsters / Reddit(robots) / GitHub Trending(内容が不正確)。
前日と同一バッチや古いデータが返ることがある。その場合は使わず、フッターに明記する。

## 3. 選別・要約
`profile.md` の基準に従う。15〜20本。日本語で1〜2文の要約。
海外記事は邦題を付け、`.orig` に原題を入れる。
★★★ は3〜4本まで。重複はまとめて `関連` リンクにする。継続中の話題は「続報」として前日までの流れに触れる。
主要な記事、特に断定しづらい内容は WebFetch で本文を確認してから書く(誤った紹介を避けるため)。

## 4. サイト更新
- `site/archive/YYYY-MM-DD.html` を新規作成(前日ファイルの1〜65行目=head部分を流用し、titleだけ差し替える)
- `site/archive/index.html` の `<ul id="list">` 直後に今日の `<li>` を追加
- `site/index.html` は今日のファイルのコピー

## 5. commit & push
URL埋め込みの認証は proxy に拒否される。Authorization ヘッダ方式を使う。

```
cd /home/claude/trend-digest/site
cp archive/YYYY-MM-DD.html index.html
git add -A
git -c user.email="siba010866@gmail.com" -c user.name="Trend Digest Bot" commit -qm "digest: YYYY-MM-DD

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01JmnGbbc7rJF92kjscQA3vC"
AUTH=$(printf 'x-access-token:<会話履歴にあるPAT>' | base64 -w0)
git -c http.extraheader="Authorization: Basic $AUTH" push origin main
```

commit と push を1コマンドに繋げると稀に拒否されるので、別々の Bash 呼び出しに分ける。
push が失敗しても、ダイジェストの送付(手順6)は必ず実施し、その旨を添える。

## 6. 配信
- `SendUserFile` で `archive/YYYY-MM-DD.html` を送る(status=proactive, display=render)
- `SendUserMessage` で ★★★ の紹介 + `https://trend-digest.pages.dev/` + 「明朝7時の分も予約済み」

## 公開先
- GitHub: https://github.com/syugo0108/trend-digest (production branch: main)
- Cloudflare Pages: https://trend-digest.pages.dev/ (Git連携で main への push により自動デプロイ)
