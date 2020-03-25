import os
import random
import string
from collections import Counter
from datetime import datetime, timedelta
from os.path import join
from typing import List

import discord
from discord.ext import commands

import constants


# discord.Messageをマークダウンに変換する.(discord.Messageのクラスメソッドとして登録する.)
def _to_md(self) -> str:
    created_at = f'{(self.created_at + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M")}(+09:00)'
    message_url = self.jump_url
    author = self.author
    content = self.clean_content
    attachments = '\n'.join([f'![{a.filename}]({a.url})' for a in self.attachments])
    edited = "**(編集済)**" if self.edited_at is not None else ""
    return (f'- **[{created_at}]({message_url}) {author}**: {content} {edited}\n'
            f'{attachments}')


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
            await ctx.send(f'サブコマンドが指定されていません. (詳細は`!help {self.historian}`で確認できます.)')

    @historian.group(
        name='channel',
        aliases=['c'],
        usage='<サブコマンド>',
        help='チャンネル内の会話ログを抜粋する',
        invoke_without_command=True
    )
    async def channel(self, ctx, id_a: int = None, id_b: int = None, title: str = ''):
        await self.cut(ctx, id_a, id_b, title)

    @channel.command(
        name='cut',
        aliases=['range', 'r'],  # rangeが予約語のため、エイリアスとして使えるようにした。
        usage='<先頭メッセージID> (<末尾メッセージID>) (<タイトル>)',
        help=('先頭のメッセージIDと末尾のメッセージIDを指定することで,その範囲のログを切り出したMarkdownが生成される.\n'
              '末尾のメッセージIDを省略した場合,先頭メッセージIDから最新のメッセージまでを切り出す.\n'
              'タイトルを指定した場合,Markdownの大見出しにその文字列が設定される.\n')
    )
    async def cut(self, ctx, id_a: int = None, id_b: int = None, title: str = ''):
        if id_a is None:
            await ctx.send(f'引数が足りません. (詳細は`!help historian {sys._getframe().f_code.co_name}`で確認できます.)')
            return

        if id_b is None:
            id_b = ctx.channel.last_message_id

        try:
            msg_a = await ctx.fetch_message(id_a)
            msg_b = await ctx.fetch_message(id_b)

            since, until = sorted([msg_a.created_at, msg_b.created_at])
            messages = await self._extractMessagesInRange(ctx, since, until)

            since_str = since.strftime("%Y-%m-%d %H:%M")
            until_str = until.strftime("%Y-%m-%d %H:%M")
            MD_STR = messages_to_mdstr(messages, title if title != '' else f'{since_str}~{until_str}')

            MD_FILE_NAME = f'{"".join([random.choice(string.ascii_letters + string.digits) for _ in range(20)])}.md'
            MD_FILE_PATH = join(constants.MD_DIR, MD_FILE_NAME)
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

    @cut.error
    async def cut_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send(f'引数の値が不正です. (詳細は`!help {self.cut}`で確認できます。)')
        else:
            raise error

    @channel.command(
        name='pick',
        aliases=['ids', 'p'],
        usage='<メッセージID...>',
        help=('複数のメッセージIDを指定すると、それらをピックアップしてMarkdownを生成する.\n'
              'タイトルは指定できない.\n')
    )
    async def pick(self, ctx, *ids: int):
        if len(ids) < 1:
            await ctx.send(f'メッセージIDが指定されていません. (詳細は`!help {self.pick}`で確認できます.)')
            return

        try:
            messages = [await ctx.fetch_message(id) for id in ids]
            messages.sort(key=lambda m: m.created_at)

            MD_STR = messages_to_mdstr(messages, f'{len(ids)}件のメッセージ')

            MD_FILE_NAME = f'{"".join([random.choice(string.ascii_letters + string.digits) for _ in range(20)])}.md'
            MD_FILE_PATH = join(constants.MD_DIR, MD_FILE_NAME)
            with open(MD_FILE_PATH, mode='w', encoding='UTF-8') as f:
                f.write(MD_STR)

            await ctx.send(file=discord.File(f'{MD_FILE_PATH}'))
            os.remove(MD_FILE_PATH)

        except discord.NotFound:
            await ctx.send('存在しないIDが含まれています.')

        except discord.Forbidden:
            await ctx.send('この機能を利用する権限がありません.')

        except discord.HTTPException as e:
            await ctx.send(e)

        except Exception:
            await ctx.send('エラーが発生しました.')

    @pick.error
    async def pick_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send(f'引数の値が不正です. (詳細は`!help {self.pick}`で確認できます。)')
        else:
            raise error

    # 先頭と末尾の時刻を指定すると、その範囲内に投稿されたログを抽出する.
    async def _extractMessagesInRange(self, ctx, since: datetime, until: datetime) -> List[discord.Message]:
        since -= timedelta(milliseconds=1)
        until += timedelta(milliseconds=1)
        return await ctx.history(after=since, before=until).flatten()


def setup(bot):
    bot.add_cog(Historian(bot))
