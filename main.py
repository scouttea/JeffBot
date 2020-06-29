import discord
import configparser
import services.Services
import commands.Command

from ServiceProvider import Command

client = discord.Client()
config = configparser.ConfigParser()
config.read('config.ini')
token = config["main"]["token"]

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await Command.respond(message)


client.run(token)
print("bye")