import re
from ServiceProvider import Service
from services.Registry import Registry

from discord import TextChannel, DMChannel
def location(message):
    location = [message.id,message.channel.id]
    if False:
        pass
    elif isinstance(message.channel,TextChannel):
        location += [message.channel.category_id, message.channel.guild.id]
    elif isinstance(message.channel,DMChannel):
        location += [message.channel.recipient.id]
    else:
        raise Exception("unkown location")
    return tuple(location)



class CommandBridge():
    def __init__(self, message, content):
        self.message = message
        self.content = content

    async def reply(self, content):
        await self.message.channel.send(content)

@Service("Command")
class Commands(Registry):
    async def respond(self,message):
        location(message)
        try:
            r = re.match("^!([^ ]+)( |$)(.*)",message.content)
            name,_,args = r.groups()
            if name not in self.registry:
                return None
            await self.registry[name](CommandBridge(message,args))
            return True
        except AttributeError as e:
            pass

from commands.modules import *