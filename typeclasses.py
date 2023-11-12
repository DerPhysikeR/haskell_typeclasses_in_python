from typing import Callable, Iterator, Protocol, Self


class Functor(Protocol):
    def fmap(self, fun: Callable) -> Self:  # <$>
        ...


class Maybe:
    def __init__(self, value):
        self._value = value

    def __repr__(self) -> str:
        return f"Maybe({repr(self._value)})"

    def fmap(self, fun: Callable) -> Self:
        if self._value is None:
            return self.__class__(None)
        return self.__class__(fun(self._value))


class MyList:
    def __init__(self, ls: list) -> None:
        self._list = ls

    def __repr__(self) -> str:
        return f"MyList({repr(self._list)})"

    def __iter__(self) -> Iterator:
        return iter(self._list)

    def fmap(self, fun: Callable) -> Self:
        return self.__class__(list(map(fun, self._list)))


# function which requires an instance of Functor
def square(arg: Functor) -> Functor:
    return arg.fmap(lambda x: x * x)


if __name__ == "__main__":
    # functor examples
    maybe_none = Maybe(None)
    maybe_just = Maybe(5)
    print(square(maybe_none))  # Maybe(None)
    print(square(maybe_just))  # Maybe(25)

    empty_list = MyList([])
    some_list = MyList([1, 2, 3])
    print(square(empty_list))  # MyList([])
    print(square(some_list))  # MyList([1, 4, 9])
