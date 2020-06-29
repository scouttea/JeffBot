class Registry():
    def __init__(self):
        self.registry = {}

    def bind(self,delegate):
        try:
            self.registry = registry
        except Exception as e:
            raise Exception("not supported")

    def register(self,name):
        def wrap(f):
            self.registry[name]=f
            return f
        return wrap