import random

from discord.ext import commands

from constants import NOMINATOR_LIMIT


class Nominator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='nominator',
        usage='<[母集団に含めるべきユーザに付与されたロール...> <指名する人の人数>',
        help=('指定したロールが付与されたメンバーから,指定された人数のメンバーをランダムに選び,メンションを飛ばす.\n'
              'なお,ロールは複数個指定できる.\n'),
        invoke_without_command=True
    )
    async def nominator(self, ctx: commands.Context, *args):
        if not args:
            await ctx.send(f'引数を指定してください. (詳細は`!help {self.nominator}`で確認できます.)')

        *target_roles, c = args

        try:
            c = int(c)
        except:
            await ctx.send(f'指名する人数は整数で入力してください.')
            return

        population = [m for m in ctx.channel.members
                      if set(target_roles) & set(map(lambda x: x.name, m.roles))]

        if c < 1:
            await ctx.send('指名する人数は1以上にしてください.')
            return

        if c > 50:
            await ctx.send(f'指名する人数が多すぎます. 指名できるのは{NOMINATOR_LIMIT}人までです.')
            return

        if len(population) < c:
            await ctx.send(f'指名すべき人数が候補者の人数を超えています. (候補者数={len(population)})')
            return

        nominees = random.sample(population, c)
        await ctx.send(', '.join(f'{i}: {self._gen_mention_str(u.id)}' for i, u in enumerate(nominees, start=1)))

    @staticmethod
    def _gen_mention_str(user_id: int) -> str:
        return f'<@!{user_id}>'


def setup(bot):
    bot.add_cog(Nominator(bot))
