from collections import OrderedDict
from typing import Optional
from collections import OrderedDict, namedtuple

CachedResponse = namedtuple("CachedResponse", ["vectorframe", "response"])


class Cache:
    """
    Usage:

    >>> cache = Cache(maxsize=3)

    # キャッシュに値を保存する
    >>> cache["key1"] = "value1"

    # キャッシュから値を取得する
    >>> cache['key1']
    'value1'

    # 存在しないキーを指定して値を取得する
    >>> cache.get('not_exist_key', 'default_value')
    'default_value'

    # インスタンス化
    >>> cache = Cache(maxsize=3, a=1, b=2, c=3)

    >>> cache
    OrderedDict([('a', 1), ('b', 2), ('c', 3)])

    # maxsizeを超えると
    >>> cache["d"] = 4

    # 古いものから削除("a"の要素がなくなる)
    >>> cache
    OrderedDict([('b', 2), ('c', 3), ('d', 4)])

    # 参照すると
    >>> cache["c"]
    3

    # 新しく追加したものとして最後尾に追加
    >>> cache
    OrderedDict([('b', 2), ('d', 4), ('c', 3)])
    """
    def __init__(self, maxsize: Optional[int] = None, **kwargs):
        self.maxsize = maxsize
        self.data = OrderedDict(**kwargs)

    def __getitem__(self, key):
        value = self.data.pop(key)
        self.data[key] = value
        return value

    def __setitem__(self, key, value):
        if key in self.data:
            self.data.pop(key)
        elif len(self.data) >= self.maxsize:
            self.data.popitem(last=False)
        self.data[key] = value

    def get(self, key, default=None):
        if key in self.data:
            return self.__getitem__(key)
        return default

    def __repr__(self):
        return repr(self.data)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
