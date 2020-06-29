from ServiceProvider import Command

@Command.register("echo")
async def command(message):
    if message.content:
        await message.reply("*\""+message.content+"\"* echoes in the distance")
    else:
        await message.reply("*silence*")