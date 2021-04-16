from os.path import dirname, join

# 環境変数からdiscord bot tokenを読み込む
BOT_TOKEN = os.environ.get('BOT_TOKEN')

COMMAND_PREFIX = '!'
INITIAL_EXTENSIONS = [
    'cogs.historian',
    'cogs.nominator'
]

# 生成したMarkdownを保存するディレクトリ
MD_DIR = join(dirname(__file__), 'mdtmp')

# nominatorコマンドで指名できる人数の上限
NOMINATOR_LIMIT = 50
