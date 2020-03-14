import os
from os.path import join, dirname

# 環境変数からdiscord bot tokenを読み込む
BOT_TOKEN = os.environ.get('BOT_TOKEN')

COMMAND_PREFIX = '!'
INITIAL_EXTENSIONS = [
    'cogs.historian'
]

# 生成したMarkdownを保存するディレクトリ
MD_DIR = join(dirname(__file__), 'mdtmp')
