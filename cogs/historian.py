import os
import random
import string
import sys
from collections import Counter
from datetime import timedelta
from os.path import join

import discord
from discord.ext import commands

import constants


# discord.Messageをマークダウンに変換する.(discord.Messageのクラスメソッドとして登録する.)
def _to_md(self) -> str:
    created_at = self.created_at.strftime("%Y/%m/%d %H:%M:%S")
    message_url = self.jump_url
    author = self.author
    content = self.content
    edited = "**(編集済み)**" if self.edited_at is not None else ""
    return f'- **[{created_at}]({message_url}) {author}**: {content} {edited}'


# discord.MessageのリストからMarkdown文字列を生成する.
def messages_to_mdstr(messages: list, title: str) -> str:
    history = '\n'.join([m.to_md() for m in filter(lambda m: not m.author.bot, messages)])

    author_and_msg_count = dict(Counter([m.author for m in filter(lambda m: not m.author.bot, messages)]).most_common())
    participants = '\n'.join([f'- {user}' for user in author_and_msg_count])

    return '\n\n'.join([f'# {title}', '## 参加者(登場人物)', participants, '## 会話ログ', history])


# サーバー・チャンネル内の会話ログを抜粋する系のコマンド
class Historian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        setattr(discord.Message, "to_md", _to_md)

    @commands.group(
        name='historian',
        aliases=['history'],
        usage='<サブコマンド>',
        help='サーバー・チャンネル内の会話ログを抜粋する',
    )
    async def historian(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f'サブコマンドが指定されていません. (詳細は`!help {sys._getframe().f_code.co_name}`で確認できます.)')

    @historian.command(
        name='channel',
        aliases=['c'],
        usage='<先頭メッセージID> <末尾メッセージID> (<タイトル>)',
        help=('コマンドを実行したチャンネルの会話ログを抜粋する.\n'
              '先頭のメッセージIDと末尾のメッセージIDを指定することで,その範囲のログを切り出したMarkdownが生成される.\n'
              'タイトルを指定した場合,Markdownの大見出しにその文字列が設定される.\n')
    )
    async def channel(self, ctx, id_a: int = None, id_b: int = None, title: str = ''):
        if id_a is None or id_b is None:
            await ctx.send(f'引数が足りません. (詳細は`!help historian {sys._getframe().f_code.co_name}`で確認できます.)')
            return

        try:
            msg_a = await ctx.fetch_message(id_a)
            msg_b = await ctx.fetch_message(id_b)

            since, until = sorted([msg_a.created_at, msg_b.created_at])
            since -= timedelta(milliseconds=1)
            until += timedelta(milliseconds=1)

            messages = await ctx.history(after=since, before=until).flatten()

            MD_FILE_NAME = f'{"".join([random.choice(string.ascii_letters + string.digits) for _ in range(20)])}.md'
            MD_FILE_PATH = join(constants.MD_DIR, MD_FILE_NAME)
            MD_STR = messages_to_mdstr(messages,
                                       title if title != '' else f'{since.strftime("%Y-%m-%d %H:%M")}~{until.strftime("%Y-%m-%d %H:%M")}')

            with open(MD_FILE_PATH, mode='w', encoding='UTF-8') as f:
                f.write(MD_STR)

            await ctx.send(file=discord.File(f'{MD_FILE_PATH}'))
            os.remove(MD_FILE_PATH)

        except discord.NotFound:
            await ctx.send('指定したIDのメッセージIDが見つかりませんでした.')

        except discord.Forbidden:
            await ctx.send('この機能を利用する権限がありません.')

        except discord.HTTPException as e:
            await ctx.send(e)

        except Exception:
            await ctx.send('エラーが発生しました.')

    @channel.error
    async def channel_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send(f'引数の値が不正です. (詳細は`!help historian {sys._getframe().f_code.co_name[:-6]}`)')
        else:
            raise error


def setup(bot):
    bot.add_cog(Historian(bot))
