import pyfiglet
from ServiceProvider import Command

@Command.register("ascii")
async def command(message):
    await message.reply("```\n{}```".format(pyfiglet.figlet_format(message.content, font='big')).strip())
#