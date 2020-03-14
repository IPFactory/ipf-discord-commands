import os
from os.path import join, dirname

from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv(join(dirname(__file__), '.env'))

BOT_TOKEN = os.environ.get('BOT_TOKEN')

COMMAND_PREFIX = '!'
INITIAL_EXTENSIONS = [
    'cogs.historian'
]

# 生成したMarkdownを保存するディレクトリ
MD_DIR = join(dirname(__file__), 'mdtmp')
