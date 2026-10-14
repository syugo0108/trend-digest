# Trend Digest — 毎朝の運用手順

毎朝 6:57 JST に、定期実行が新しいセッションを起動する(会話の記憶はない)。
このファイルの手順を順に実施する。無人実行なので、質問せず最後まで完遂すること。

## 0. 準備
1. 今日の日付を JST で決める: `TZ=Asia/Tokyo date +%F`(以下 YYYY-MM-DD)。曜日も `TZ=Asia/Tokyo date +%u` で確認する。
2. リポジトリを取得する(新しいセッションなので毎回 clone)。

```
mkdir -p ~/trend-digest && cd ~/trend-digest
git clone --depth 10 https://github.com/syugo0108/trend-digest.git site
```

3. **重複チェック**: `site/archive/YYYY-MM-DD.html` が既にあれば、今日の分は配信済み。何もせず「本日分は配信済み」とだけ報告して終了する。
4. 直近2〜3日分の `archive/*.html` に目を通し、継続中の話題(続報として扱うもの)を把握する。

GitHub トークン(PAT)は定期実行の指示文にだけ書かれている。ファイルやコミットには絶対に書かない。

## 1. ソース収集(必ず WebFetch を使う)
bash/python での HTTP は proxy に塞がれている。WebFetch のみ使い、取得できないものを別手段で取りに行かない。
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
URL埋め込みの認証は proxy に拒否される。Authorization ヘッダ方式を使う。commit と push は別々の Bash 呼び出しに分ける。

```
cd ~/trend-digest/site
git add -A
git -c user.email="siba010866@gmail.com" -c user.name="Trend Digest Bot" commit -qm "digest: YYYY-MM-DD"
```

```
cd ~/trend-digest/site
AUTH=$(printf 'x-access-token:<指示文にあるトークン>' | base64 -w0)
git -c http.extraheader="Authorization: Basic $AUTH" push origin main
```

main への push で Cloudflare Pages が自動デプロイする。push が失敗しても手順5は必ず実施し、その旨を添える。

## 5. 配信
- `SendUserFile` で `archive/YYYY-MM-DD.html` を送る(status=proactive, display=render)
- 最後に、★★★ の紹介と `https://trend-digest.pages.dev/` を短く伝える。

## 公開先
- GitHub: https://github.com/syugo0108/trend-digest (production branch: main)
- Cloudflare Pages: https://trend-digest.pages.dev/
