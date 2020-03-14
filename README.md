# ipf-discord-commands

## 概要

IPFactoryのサークルDiscord鯖用コマンドbot

## 使い方

botは以下の手順で起動する.

1. 環境変数の設定
2. 起動

### 環境変数の設定

`.env`という名前のファイルを作成し,内容を以下のように編集する.

```
BOT_TOKEN=<discord bot token>
```

[.env.sample](./.env.sample)をコピーすると右辺だけ編集すれば済む.

```shell-session
$ cp .env.sample .env
```

### 起動  

```shell-session 
$ pip3 -r install requirements.txt
$ python3 main.py 
```

 ## 実装されているコマンド
 
 - `historian`: サーバ・チャンネル内のログを抜粋する