import re
from ServiceProvider import Service
from services.Registry import Registry

class CommandBridge():
    def __init__(self, message, client, content):
        self.message = message
        self.content = content
        self.client = client

    async def reply(self, content):
        return await self.message.channel.send(content)

@Service("Command")
class Commands(Registry):
    async def respond(self,message,client):
        try:
            r = re.match("^!([^ ]+)( |$)(.*)",message.content)
            name,_,args = r.groups()
            if name not in self.registry:
                return None
            await self.registry[name](CommandBridge(message,client,args))
            return True
        except AttributeError as e:
            pass

from commands.modules import *
