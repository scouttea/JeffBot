import re
from ServiceProvider import register_service

class Commands():
    def __init__(self):
        self.registry = {}

    def bind(self,delegate):
        raise Exception("not supported")

    def register(self,name):
        def wrap(f):
            self.registry[name]=f
            return f
        return wrap

    async def respond(self,message):
        start = "!"
        content = message.content
        if content.startswith(start):
            content = content[len(start):]
            for k,v in self.registry.items():
                if re.match("^!"+k+"( |$)",message.content):
                    await v(message)
                    return True
            await message.add_reaction("❌")
        return None

register_service("Command",Commands())
from commands.modules import *