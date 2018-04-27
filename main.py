from functools import wraps
from typing import List

import discord.utils
from discord import Object
from discord.ext import commands
import discord

bot = commands.Bot(
    command_prefix='~',
    self_bot=True,
)

banned_guilds = [
    365116470339960832,
    375597071094382603,
]


def check_guild(func):
    @wraps(func)
    async def wrapper(ctx: commands.Context, *args, **kwargs):
        if ctx.guild.id in banned_guilds:
            return
        return await func(ctx, *args, **kwargs)

    return wrapper


async def _context_react(self: commands.Context, emoji):
    await self.message.add_reaction(emoji)


commands.Context.react = _context_react


def dump_perms(permissions: discord.Permissions):
    def perm_names():
        for perm, value in permissions:
            if value:
                yield perm

    return ', '.join(perm_names())


@bot.event
async def on_ready():
    print('Logged in as %s#%s' % (bot.user.name, bot.user.discriminator))


def get_with_attr(arr, **attributes):
    def _get_with_attr():
        for el in arr:
            for key, val in attributes.items():
                if isinstance(val, str):
                    if str(getattr(el, key)).lower() != val.lower():
                        break
                else:
                    if type(val)(getattr(el, key)) != val:
                        break
            else:
                yield el

    return list(_get_with_attr())


@bot.command(name="user", pass_context=True)
@check_guild
async def user_cmd(ctx: commands.Context, identifier):
    import re
    identifier = str(identifier)
    if re.match(r'^<@!?[0-9]+>$', identifier):
        identifier = re.sub('[<@!>]+', '', identifier)

    identifier = int(identifier)
    profile: discord.Profile = await bot.get_user_profile(identifier)
    discord_profile: discord.User = bot.get_user(identifier)
    em = discord.Embed(
        title='%s#%s' % (discord_profile.name, discord_profile.discriminator),
    )
    desc = ""
    if profile.staff:
        desc += "Bow in awe of the mighty staff!\n"
    if profile.hypesquad:
        desc += "They got some hype\n"
    if profile.nitro:
        desc += "I can haz animated emotez since %s\n" % profile.premium_since
    if profile.partner:
        desc += "Discord Partner. woa\n"
    desc += '\n'
    em.description = desc

    guild_str = ""
    for guild in profile.mutual_guilds:
        guild_str += guild.name + "\n"
    em.add_field(name='Mutual guilds', value=guild_str, inline=True)

    for account in profile.connected_accounts:
        em.add_field(name=account['type'], value=('☑' if account['verified'] else '') + account['name'])

    em.set_thumbnail(url=discord_profile.avatar_url)
    em.add_field(name='Joined Discord', value=discord_profile.created_at, inline=True)
    guild: discord.Guild = ctx.guild
    if guild.get_member(identifier) is not None:
        member: discord.Member = guild.get_member(identifier)
        em.colour = member.color
        em.add_field(name="Permissions", value=dump_perms(member.guild_permissions), inline=True)
        em.add_field(name="Joined guild", value=member.joined_at)

    await ctx.send(embed=em)
    await ctx.react('✅')


@bot.command(pass_context=True, name="role")
@check_guild
async def role_cmd(ctx: commands.Context):
    txt = ctx.message.content
    role = txt[txt.find(' ') + 1:]
    role_obj = get_with_attr(ctx.guild.roles, name=role) \
               + get_with_attr(ctx.guild.roles, id=role)
    if len(role_obj) == 0:
        await ctx.react('❌')
        return
    await dump_roles(ctx, role_obj, False)
    await ctx.react('✅')


@bot.command(pass_context=True)
@check_guild
async def raw(ctx: commands.Context, id, quiet: bool=True):
    channel: discord.TextChannel = ctx.channel
    async for mes in channel.history(limit=2, around=Object(id=id)):
        if str(mes.id) == id:
            escaped = mes.content.replace('```', '``\u200B`')
            if quiet:
                print(mes.content)
            else:
                await ctx.send("```\n%s\n```" % escaped)
            await ctx.react('✅')
            return
    await ctx.react('❌')


async def dump_roles(ctx: commands.Context, roles: List[discord.Role], quiet: bool):
    def description(role: discord.Role):
        return """
        Name: `%s`
        Id: %s
        Color: %s
        Permissions: %s
        """ % (
            role.name,
            role.id,
            str(role.color),
            dump_perms(role.permissions)
        )

    tmp = ""
    texts = [description(role) for role in roles]
    if quiet:
        print('\n'.join(texts))
        return
    for text in texts:
        if len(text) + len(tmp) + len('\n') < 2000:
            tmp += text + '\n'
        else:
            await ctx.send(tmp)
            tmp = ""
    if len(tmp) != 0:
        await ctx.send(tmp)


@bot.command(pass_context=True, name="roles")
@check_guild
async def roles_cmd(ctx: commands.Context, quiet: bool = False):
    guild: discord.Guild = ctx.guild
    roles: List[discord.Role] = guild.roles

    await dump_roles(ctx, roles, quiet)
    await ctx.react('✅')


if __name__ == '__main__':
    with open('token.txt') as f:
        bot.run(f.read().strip(), bot=False)
