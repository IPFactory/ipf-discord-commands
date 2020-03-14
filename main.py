import os
import traceback
from os.path import isdir

from discord.ext import commands

import constants


# ヘルプ日本語化
class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = 'コマンド:'
        self.no_category = 'その他'
        self.command_attrs['help'] = '利用できるコマンド一覧と説明を表示します'

    def get_ending_note(self):
        return (f'各コマンドの説明: {constants.COMMAND_PREFIX}help <コマンド名>\n'
                f'各カテゴリの説明: {constants.COMMAND_PREFIX}help <カテゴリ名>\n')


class IPFCommandsBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, help_command=JapaneseHelpCommand())
        for cog in constants.INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print(f'[Info] Logged in as {bot.user.name}(id: {bot.user.id}).')


if __name__ == '__main__':
    if not isdir(constants.MD_DIR):
        os.makedirs(constants.MD_DIR)
    bot = IPFCommandsBot(command_prefix=constants.COMMAND_PREFIX)
    bot.run(constants.BOT_TOKEN)
