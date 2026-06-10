# シンギュラリティ・サーバー AI News Bot

Discordサーバー「シンギュラリティ・サーバー」の「最新情報」チャンネルに、AI関連ニュースを自動投稿するためのシンプルなBotです。

やることはこれだけです。

1. RSSを読む
2. 各RSSの最新1件だけ確認する
3. まだ投稿していない記事だけDiscordに投稿する
4. 投稿済みの記事を `posted_articles.json` に記録する

AI要約はしません。OpenAI APIも使いません。追加課金なしで運用できます。

## 投稿フォーマット

```text
:icon:SINGULARITY FEED:icon:

記事タイトル
記事URL
```

## ファイル構成

```text
.
├── main.py
├── requirements.txt
├── .env.example
├── feeds.json
├── posted_articles.json
├── README.md
└── .github
    └── workflows
        └── newsbot.yml
```

## 各ファイルの役割

| ファイル | 役割 |
| --- | --- |
| `main.py` | RSS取得、Discord投稿、重複チェックをするBot本体 |
| `requirements.txt` | 必要なPythonライブラリ一覧 |
| `.env.example` | ローカル確認用の環境変数サンプル |
| `feeds.json` | RSS一覧。追加・削除はここを編集します |
| `posted_articles.json` | 投稿済み記事の記録 |
| `.github/workflows/newsbot.yml` | GitHub Actionsで1時間ごとに動かす設定 |

## 無料で運用できる理由

- Discord Webhookは無料です
- RSS取得は無料です
- GitHub Actionsの無料枠で動かせます
- OpenAI APIなどの有料APIを使いません
- サーバーやデータベースを借りません

## Discord Webhookの作り方

1. Discordで投稿したいチャンネルを開きます
2. チャンネル名の右にある歯車アイコンを押します
3. 「連携サービス」を開きます
4. 「ウェブフック」を開きます
5. 「新しいウェブフック」を押します
6. 投稿先チャンネルが「最新情報」になっていることを確認します
7. 名前をわかりやすくします。例: `AI News Bot`
8. 「ウェブフックURLをコピー」を押します

コピーしたURLはとても大事です。ほかの人に見せないでください。

## ローカルで動作確認する方法

まず、このフォルダでライブラリを入れます。

```bash
pip install -r requirements.txt
```

次に `.env.example` をコピーして `.env` を作ります。

```bash
cp .env.example .env
```

`.env` を開いて、コピーしたDiscord Webhook URLを入れます。

```text
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

実行します。

```bash
python main.py
```

成功すると、Discordにニュースが投稿されます。

初回でも大量投稿されないように、各RSSから最新1件だけ投稿します。

## GitHub Secretsの設定方法

GitHub Actionsで動かす場合、Discord Webhook URLをGitHub Secretsに入れます。

1. GitHubでこのリポジトリを開きます
2. `Settings` を開きます
3. 左メニューの `Secrets and variables` を開きます
4. `Actions` を開きます
5. `New repository secret` を押します
6. `Name` にこれを入れます

```text
DISCORD_WEBHOOK_URL
```

7. `Secret` にDiscord Webhook URLを貼ります
8. `Add secret` を押します

これでGitHub ActionsからDiscordに投稿できます。

## GitHub Actionsでの自動実行

`.github/workflows/newsbot.yml` により、1時間ごとに自動実行されます。

```yaml
cron: "0 * * * *"
```

これは「毎時0分に実行」という意味です。

手動で試したい場合は、GitHubの `Actions` 画面から `AI News Bot` を選び、`Run workflow` を押してください。

## 投稿済み記事の記録について

投稿済みの記事は `posted_articles.json` に保存されます。

GitHub Actionsで新しい記事を投稿した場合、このファイルも自動で更新してGitHubに反映します。

このファイルを消すと、過去の記事がもう一度投稿される可能性があります。基本的には触らなくて大丈夫です。

## RSSの追加方法

RSSを追加したいときは `feeds.json` を編集します。

例:

```json
{
  "name": "Example AI Blog",
  "url": "https://example.com/feed.xml",
  "category": "ai",
  "language": "ja"
}
```

一時的に止めたい場合は、`disabled: true` を追加します。

```json
{
  "name": "Example AI Blog",
  "url": "https://example.com/feed.xml",
  "category": "ai",
  "language": "ja",
  "disabled": true
}
```

RSSが取れるか怪しいものは、無理に有効化しないでください。壊れにくさ優先です。

## 現在「要確認」にしているRSS

以下は候補として残していますが、2026-06-08時点の確認では取得できなかった、または不安定だったため `disabled: true` にしています。

- Anthropic News
- Ledge.ai
- ZDNET Japan
- Techable
- BRIDGE

RSS URLがわかったら、`feeds.json` の `url` を直して `disabled` を消してください。

## よくあるつまずき

### Discordに投稿されない

まず `DISCORD_WEBHOOK_URL` が正しく設定されているか確認してください。

ローカルなら `.env`、GitHub ActionsならGitHub Secretsです。

### 同じ記事が何度も投稿される

`posted_articles.json` が消えていないか確認してください。

### GitHub Actionsは動くが、投稿済み記録が反映されない

リポジトリの `Settings` で、GitHub Actionsに書き込み権限があるか確認してください。

通常はこのファイルの設定だけで大丈夫です。

```yaml
permissions:
  contents: write
```

### RSSを追加したらエラーになる

RSS URLが間違っている可能性があります。

まずはそのRSSを `disabled: true` に戻してください。Bot全体を止めないことが大事です。

## 大事な方針

このBotは、最初から高機能を目指しません。

まずは「RSSを読んでDiscordに貼るだけ」の、壊れにくいニュース拾い係として運用します。
