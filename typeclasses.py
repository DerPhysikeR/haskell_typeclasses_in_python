from typing import Callable, Protocol, Self


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


# function that needs an instance of Functor
def square(arg: Functor) -> Functor:
    return arg.fmap(lambda x: x * x)


if __name__ == "__main__":
    # functor examples
    maybe_none = Maybe(None)
    maybe_just = Maybe(5)
    print(square(maybe_none))
    print(square(maybe_just))
