class TGHandler(object):
    obj = None
    attr_name = None
    default = None

    def __init__(self, obj, attr_name, default):
        self.obj = obj
        self.attr_name = attr_name
        self.default = default
        self.attr_cached = None
        self._cache()

    def _cache(self):
        self.attr_cached = self.obj.attributes.get(self.attr_name, default=self.default)

    def get(self):
        return self.attr_cached

    def add(self, value):
        self.obj.attributes.add(self.attr_name, value)
        self.attr_cached = value


class TGHandlerDict(object):
    obj = None
    attr_name = None

    def __init__(self, obj, attr_name):
        self.obj = obj
        self.attr_name = attr_name
        self.attr_cached = {}
        self._cache()

    def _cache(self):
        self.attr_cached = self.obj.attributes.get(self.attr_name, default={})

    def get(self, key, default=None):
        return self.attr_cached.get(key, default)

    def add(self, key, value):
        self.obj.attributes.get(self.attr_name, default={})[key] = value
        self.attr_cached[key] = value

    def contains(self,key):
        return key in self.attr_cached

    def remove(self, key):
        return False

    def items(self):
        return self.attr_cached.items()


class TGDescriptionHandler(TGHandler):
    def __init__(self, obj):
        super(TGDescriptionHandler, self).__init__(obj, "desc", "")
