
import yaml
from copy import deepcopy
from functools import reduce
from itertools import chain, starmap


# YAML functions

def load(path):
    with open(path) as f:
        return yaml.load(f)


def dump(obj, path, **kwargs):
    opts = dict(explicit_start=True, explicit_end=False, default_flow_style=False)
    opts.update(kwargs)

    with open(path, 'w') as f:
        yaml.dump(obj, f, **opts)


# collections

def merge(source, target):
    if target is None:
        return deepcopy(source)

    if isinstance(source, dict) and isinstance(target, dict):
        return {k: merge(source.get(k), target.get(k))for k in chain(source, target)}

    return target


# cursor

class Cursor(object):

    def __init__(self, doc, path=None):
        self._doc = doc
        self._path = path or tuple()

    @property
    def root(self):
        return Cursor(self._doc)

    def parent(self, depth=-1):
        if self._path:
            return Cursor(self._doc, self._path[:depth])

    @property
    def children(self):
        if isinstance(self.value, dict):
            return [self[k] for k in self.value]
        else:
            return []

    def __getitem__(self, key):
        return Cursor(self._doc, self._path + (key,))

    def __contains__(self, key):
        return isinstance(self.value, dict) and key in self.value

    @property
    def path(self):
        return self._path

    @property
    def key(self):
        if self._path:
            return self._path[-1]

    def match(self, path=None, key=None):
        if not self._match(self.key, key):
            return False
        if path:
            return len(self._path) == len(path) and all(starmap(self._match, zip(self._path, path)))
        return True

    @staticmethod
    def _match(k, pattern):
        return pattern is None or k == pattern or (isinstance(pattern, (list, tuple, set)) and k in pattern)

    @property
    def value(self):
        if self._path:
            parent = reduce(dict.__getitem__, self._path[:-1], self._doc)
            return parent[self.key]
        else:
            return self._doc

    @value.setter
    def value(self, obj):
        if self._path:
            parent = reduce(dict.__getitem__, self._path[:-1], self._doc)
            parent[self.key] = obj
        else:
            self._doc = obj

    def __str__(self):
        return '::'.join(map(str, self._path))


# template renderer

class Template:

    def __init__(self):
        self._filter = lambda _: True
        self._before = lambda _, **kwargs: None
        self._after = lambda _, **kwargs: None
        self._handlers = []

    def filter(self, fn):
        self._filter = fn
        return fn

    def before(self, fn):
        self._before = fn
        return fn

    def after(self, fn):
        self._after = fn
        return fn

    def on(self, *path, key=None):
        def decorator(fn):
            def handler(cursor, *args, **kwargs):
                if cursor.match(path, key=key):
                    return fn(cursor, *args, **kwargs)
            self._handlers.append(handler)
            return handler

        return decorator

    def render(self, doc, defs=None, context=None):
        """
        render input file to output using predefined handlers

        :param doc:
        :param defs:
        :param context:
        :return:
        """
        defs = {} if defs is None else defs
        context = {} if context is None else context
        cursor, stack = None, [Cursor(doc)]

        try:
            cursor = Cursor(doc)
            self._before(cursor, defs=defs, context=context)

            while stack:
                cursor = stack.pop()
                if self._filter(cursor):
                    for handler in self._handlers:
                        handler(cursor, defs=defs, context=context)
                    stack += [child for child in cursor.children]

            cursor = Cursor(doc)
            self._after(cursor, defs=defs, context=context)

        except Exception:
            print('error occurred at path %s' % cursor)
            raise

        return doc
