"""
maxsizeに指定された数までのキャッシュの値を
保持するクラス「LRUCache」を定義しています。
指定したキーごとに保持する値がある場合、
データを末尾に移動し 一番古い値を先頭から
削除する仕組みが備わっています。
また、UserDictを継承しており、
辞書型と同様のメソッドを利用できます。
"""
from typing import Optional
from collections import OrderedDict, UserDict


class LRUCache(UserDict):
    """
    getや__getitem__で参照されるたびに要素を末尾に移動します。
    __setitem__されたばかりの要素も末尾に追加されます。
    つまり、最初の方に__setitem__され、かつ__getitem__で参照されていないものが、
    __setitem__されたときにmaxsizeを超えると先頭から削除されます。

    Usage:

    >>> cache = LRUCache(maxsize=3)

    # キャッシュに値を保存する
    >>> cache["key1"] = "value1"

    # キャッシュから値を取得する
    >>> cache['key1']
    'value1'

    # 存在しないキーを指定して値を取得する
    >>> cache.get('not_exist_key', 'default_value')
    'default_value'

    # インスタンス化
    >>> cache = LRUCache(maxsize=3, a=1, b=2, c=3)

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

    # `values`, `items`は
    # RuntimeError: OrderedDict mutated during iteration
    # が発生するので再実装
    # 表示を合わせるために`keys`も再実装

    >>> cache.keys()
    odict_keys(['b', 'd', 'c'])

    >>> cache.values()
    odict_values([2, 4, 3])

    >>> cache.items()
    odict_items([('b', 2), ('d', 4), ('c', 3)])

    # ここからはUserDictによる継承が機能しているかのテスト

    # __repr__
    >>> cache
    OrderedDict([('b', 2), ('d', 4), ('c', 3)])

    # __len__
    >>> len(cache)
    3

    # __contains__
    >>> "b" in cache
    True

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
        elif self.maxsize is not None and len(self.data) >= self.maxsize:
            self.data.popitem(last=False)
        self.data[key] = value

    def get(self, key, default=None):
        if key in self.data:
            return self.__getitem__(key)
        return default

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
