# ipf-discord-commands

## 概要

IPFactoryのサークルDiscord鯖用コマンドbot

## 使い方

botは以下の手順で起動する.

1. 環境変数の設定
2. 起動

### 環境変数の設定

環境変数BOT_TOKENの値にdiscord bot tokenを設定する。.

```shell-session
BOT_TOKEN=<discord bot token>
```

### 起動  

```shell-session 
$ pip3 -r install requirements.txt
$ python3 main.py 
```

 ## 実装されているコマンド
 
 - `historian`: サーバ・チャンネル内のログを抜粋する