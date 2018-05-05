import re
from typing import List, Dict, Pattern
import discord

REPLACEMENTS: Dict[Pattern, str] = {
    re.compile(r'<@!?(?P<id>[0-9]+)>'): '(guild.get_member({id}) if guild is not None else client.get_user({id}))',
    re.compile(r'<#(?P<id>[0-9]+)>'): '(discord.utils.get(all_channels, id={id}))',
    re.compile(r'<@&(?P<id>[0-9]+)>'): '(discord.utils.get(all_roles, id={id}))',
    # Maybe later emoji support
}


async def handle_eval(message: discord.Message, client: discord.Client):
    content: str = message.content
    command_start: int = content.find(' ')
    channel: discord.TextChannel = message.channel
    author: discord.Member = message.author

    all_channels: List[discord.Guild] = []
    all_roles: List[discord.Role] = []
    for guild in client.guilds:
        guild: discord.Guild = guild  # for type hints
        all_channels += guild.channels
        all_roles += guild.roles

    variables = {
        'message': message,
        'author': author,
        'channel': channel,
        'all_channels': all_channels,
        'all_roles': all_roles,
        'client': client,
        'discord': discord,
    }
    if channel.guild is not None:
        variables['guild'] = channel.guild
    lines: List[str] = content[command_start:].strip().split('\n')
    lines[-1] = 'return ' + lines[-1]
    block: str = '\n'.join(' ' + line for line in lines)
    code = f"async def code({', '.join(variables.keys())}):\n" \
           f"{block}"

    for regex, replacement in REPLACEMENTS.items():
        code = re.sub(regex, lambda match: replacement.format(**match.groupdict()), code)

    _globals, _locals = {}, {}
    exec(code, _globals, _locals)
    result = {**_globals, **_locals}
    result = await result["code"](**variables)

    return await channel.send("Evaluation success: ```tr\n%r\n```" % result)
