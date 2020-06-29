import sys
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec

class Service():
    def __init__(self,service):
        self.service = service

    def rebind(self,service):
        self.service = service.bind(self.service)

    def __getattr__(self,key):
        if key in self.__dict__:
            return self.__dict__[key]
        return getattr(self.__dict__["service"],key)

class ServiceProvider():
    def __init__(self,spec):
        self.__name__    = spec.name
        self.__path__    = "virtual"
        self.__loader__  = spec.loader
        self.__package__ = ""
        self._services = {}

    def Service(self,name):
        def wrap(cls):
            self.register_service(name,cls())
            return cls
        return wrap

    def register_service(self,name,delegate):
        if name in self._services:
            raise Exception(name + " is already registered as a serivce")
        self._services[name] = Service(delegate)

    def bind(self,name,service):
        if name not in self._services:
            raise Exception("no such service " + name)
        self._services[name] = self._services[name].rebind(service)

    def __getattr__(self,key):
        if key in self.__dict__:
            return self.__dict__[key]
        if key in self._services:
            return self._services[key]
        raise Exception("no delegate found for " + key)

class Loader(Loader):
    def create_module(cls, spec):
        return ServiceProvider(spec)

    def exec_module (cls, module):
        module.__dict__["k"]=5

class Finder(MetaPathFinder):
    def find_spec(cls, fullname, path=None, target=None):
        if (fullname == "ServiceProvider"):
            return ModuleSpec(fullname,Loader())

sys.meta_path.insert (0, Finder())
