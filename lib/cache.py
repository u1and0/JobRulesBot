from typing import Any
from collections import namedtuple
from dataclasses import dataclass, field
from functools import lru_cache

CachedResponse = namedtuple("CachedResponse", ["vectorframe", "response"])


@dataclass
class Cache:
    """
    Usage:

    >>> cache = Cache()

    # キャッシュに値を保存する
    >>> cache.set("key1", "value1")

    # キャッシュから値を取得する
    >>> cache.get("key1")
    "value1"

    # キャッシュに値を保存する
    >>> cache["key2"] = "value2"

    # キャッシュから値を取得する
    >>> cache["key2"]
    "value2"

    # 存在しないキーを指定して値を取得する
    >>> cache.get("not_exist_key", "default_value")
    "default_value"
    """
    # dict[query: ["vectorframe", "response"]]
    cache_dict: dict[str, Any] = field(default_factory=dict)

    @lru_cache(maxsize=2)
    def get(self, key: str, default: Any = None) -> Any:
        """ 最長未使用頻度。最も長く使用されていないものから破棄
        100個まで値を保持可能。
        """
        return self.cache_dict.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.cache_dict[key] = value

    def __getitem__(self, key: str, default: Any = None) -> Any:
        return self.get(key, default)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self.cache_dict

    def __str__(self) -> str:
        return "Cache({})".format(str(self.cache_dict))

    def __repr__(self) -> str:
        return str(self)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
