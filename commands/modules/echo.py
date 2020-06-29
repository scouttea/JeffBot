from ServiceProvider import Command

@Command.register("echo")
async def command(message):
    await message.channel.send(message.content)