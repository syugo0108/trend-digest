# Trend Digest — 毎朝の運用手順

毎朝 6:57 JST に、ChatGPT の定期実行が本手順を実行する。会話の記憶に依存しない。
このファイルの手順を順に実施する。無人実行なので、質問せず最後まで完遂すること。

## 0. 準備
1. 今日の日付を JST で決める: `TZ=Asia/Tokyo date +%F`(以下 YYYY-MM-DD)。曜日も `TZ=Asia/Tokyo date +%u` で確認する。
2. リポジトリを取得する(新しいセッションなので毎回 clone)。

```
mkdir -p ~/trend-digest && cd ~/trend-digest
git clone --depth 10 https://github.com/syugo0108/trend-digest.git site
```

3. **重複チェック**: 最新の main を読み、`site/archive/YYYY-MM-DD.html` が既にあれば再生成しない。ただし公開サイトと一致するまで配信済みとは扱わず、手順5でデプロイを確認する。
4. 直近2〜3日分の `archive/*.html` に目を通し、継続中の話題(続報として扱うもの)を把握する。

GitHub の既存コネクタ認証を使用する。認証情報を指示文・ファイル・ログに転記せず、新しいトークンや権限を作らない。ローカルに push 認証がなくても、接続済み GitHub コネクタから更新できる。

## 1. ソース収集
利用可能な Web 読み取りツールで取得する。実行環境で許可された公開 HTTP の読み取りも使用できる。HTTP 403 や認証要求を回避せず、取得不可のソースとして記録する。取得日時と元データは作業領域に保存する(記事本文全文を公開リポジトリには含めない)。
URL 末尾に `?_=YYYYMMDD` などを付けてキャッシュを回避する。

- Hacker News: `https://news.ycombinator.com/`(トップページ。Algolia API は前日の内容を返すことが多いので使わない)
- はてなブックマーク: `https://b.hatena.ne.jp/hotentry/it`(宛先URLも一緒に取得させる)
- Techmeme: `https://www.techmeme.com/feed.xml`(permalink も一緒に取得させる)
- Zenn: `https://zenn.dev/api/articles?order=daily`
- 余裕があれば: Qiita `https://qiita.com/`、HF Daily Papers `https://huggingface.co/papers`、dev.to

取得不可・恒常的に除外: Lobsters / Reddit / GitHub Trending / X(旧Twitter)。
前日と同一の内容が返ったソースは使わず、フッターに明記する。

## 2. 選別・要約
`profile.md` の基準に従う。15〜20本。
主要な記事、特に断定しづらい内容は WebFetch で本文を確認してから書く。
本文を取得できなかった記事は「本文未取得、見出しベース」と明記し、推測で中身を書かない。
数字が報道によって食い違う場合はその旨を書く。

## 3. サイト更新
- `site/archive/YYYY-MM-DD.html` を新規作成。直近ファイルの1〜65行目(head部分)を流用し、`<title>` の日付だけ差し替える。
- 本文の構造は直近ファイルと同じ(`<div class="item">` … `stars` / `title` / `orig` / `badges` / `summary` / `related`、footer)。
- 書いたら確認: `grep -c '<div class="item">'` が meta の「全N本」と一致すること。ハングル文字が混入していないこと(`python3 -c "import re,sys;print(re.findall(r'[가-힯]',open(sys.argv[1]).read()))" FILE`)。
- `site/archive/index.html` の `<ul id="list">` 直後に今日の `<li>` を追加。
- `site/index.html` は今日のファイルのコピー。

## 4. commit & push
検証: `python3 scripts/validate.py YYYY-MM-DD` を実行する。過去の号と `profile.md` が変更されていないことも差分で確認する。

接続済み GitHub コネクタの Git オブジェクト API を使い、最新 main の tree を base に、当日号・トップ・アーカイブ一覧の3ファイルを**1コミット**で更新する。最後に main を fast-forward する。force push はしない。競合した場合は最新 main からやり直し、当日号の重複を再確認する。
ローカルの認証済み git push が既に利用できる場合は、それでもよい。main への更新で既存 Cloudflare Pages 連携が自動デプロイする。

## 5. 公開確認・報告
- コミットの `check-runs` で Cloudflare Pages が `completed / success` になったことを確認する。
- `https://trend-digest.pages.dev/`、当日号、`/archive/` を取得し、公開したファイルと一致すること、新しい日付と記事が表示されることを確認する。
- 公開成功時のみ「更新完了」として、本日の紹介とサイトへのリンクを日本語で報告する。失敗時は生成・GitHub 更新・公開のどこまで完了したか、具体的な障害を報告する。認証が不足したら作成せず報告する。
- 過去の欠配日は現在の情報で埋め戻さない。旧 Claude 予約が残っている可能性は別途確認する。同じ日の既存号は上書きしない。

## 公開先
- GitHub: https://github.com/syugo0108/trend-digest (production branch: main)
- Cloudflare Pages: https://trend-digest.pages.dev/
