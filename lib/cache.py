from typing import Any, Optional
from collections import namedtuple, UserDict
from functools import lru_cache

CachedResponse = namedtuple("CachedResponse", ["vectorframe", "response"])


class Cache(UserDict):
    """
    Usage:

    >>> cache = Cache()

    # キャッシュに値を保存する
    >>> cache.set('key1', 'value1')

    # キャッシュから値を取得する
    >>> v1 = cache.get('key1')
    >>> v1 == 'value1'
    True

    # キャッシュに値を保存する
    >>> cache['key2'] = 'value2'

    # キャッシュから値を取得する
    >>> cache['key2']
    'value2'

    # 存在しないキーを指定して値を取得する
    >>> cache.get('not_exist_key', 'default_value')
    'default_value'
    """
    def __hash__(self):
        """ @lru_cacheをget()につけるために必要。
        __hash__メソッドはオブジェクトをハッシュ可能にするためのメソッドです。
        このメソッドを実装することで、@lru_cacheが適用できるようになります。
        ただし、この実装は単純にオブジェクトのIDをハッシュ値として使用しているため、
        別のオブジェクトによってIDが再利用された場合に誤った結果が得られる可能性があります。"""
        return id(self)

    @lru_cache(maxsize=3)
    def __getitem__(self, key, default=None):
        """ 最長未使用頻度。最も長く使用されていないものから破棄
        100個まで値を保持可能。
        """
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def __str__(self) -> str:
        return "Cache({})".format(str(self.data))

    def __repr__(self) -> str:
        return str(self)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
