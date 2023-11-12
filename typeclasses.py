from enum import Enum, auto
from typing import Callable, Iterator, Protocol, Self


class Functor(Protocol):
    def fmap(self, fun: Callable) -> Self:  # <$>
        ...


class Applicative(Protocol):
    @classmethod
    def pure(cls, fun: Callable) -> Self:  # pure
        ...

    def ap(self, other: Self) -> Self:  # <*>
        ...


class Semigroup(Protocol):
    def mappend(self, other: Self) -> Self:  # <>
        ...


class Maybe:
    def __init__(self, value):
        self._value = value

    def __repr__(self) -> str:
        return f"Maybe({repr(self._value)})"

    def fmap(self, fun: Callable) -> Self:  # Functor
        if self._value is None:
            return self.__class__(None)
        return self.__class__(fun(self._value))

    @classmethod
    def pure(cls, fun: Callable) -> Self:  # Applicative
        return cls(fun)

    def ap(self, other: Self) -> Self:  # Applicative
        if self._value is None or other._value is None:
            return self.__class__(None)
        return self.__class__(self._value(other._value))


class MyList:
    def __init__(self, ls: list) -> None:
        self._list = ls

    def __repr__(self) -> str:
        return f"MyList({repr(self._list)})"

    def __iter__(self) -> Iterator:
        return iter(self._list)

    def fmap(self, fun: Callable) -> Self:  # Functor
        return self.__class__(list(map(fun, self._list)))

    @classmethod
    def pure(cls, fun: Callable) -> Self:  # Applicative
        return cls([fun])

    def ap(self, other: Self) -> Self:  # Applicative
        return self.__class__([x(y) for x in self._list for y in other._list])


class OneTwoMany(Enum):
    ONE = auto()
    TWO = auto()
    MANY = auto()

    def mappend(self, other: Self) -> Self:  # Semigroup
        if self == self.ONE and other == self.ONE:
            return self.__class__(self.TWO)
        return self.__class__(self.MANY)


# function which requires an instance of Functor
def square(arg: Functor) -> Functor:
    return arg.fmap(lambda x: x * x)


# function which requires an instance of Applicative
def ap_sum(x: Applicative, y: Applicative) -> Applicative:
    # In Haskell, functions support partial application by default, to simulate that
    # we split a two argument function into two single argument functions
    def add(x):
        def inner_add(y):
            return x + y

        return inner_add

    return x.pure(add).ap(x).ap(y)


def mappend(x: Semigroup, y: Semigroup) -> Semigroup:
    return x.mappend(y)


if __name__ == "__main__":
    # functor examples
    print(square(Maybe(None)))  # Maybe(None)
    print(square(Maybe(5)))  # Maybe(25)
    print(square(MyList([])))  # MyList([])
    print(square(MyList([1, 2, 3])))  # MyList([1, 4, 9])

    # applicative examples
    print(ap_sum(Maybe(None), Maybe(None)))  # Maybe(None)
    print(ap_sum(Maybe(5), Maybe(None)))  # Maybe(None)
    print(ap_sum(Maybe(5), Maybe(5)))  # Maybe(10)
    print(ap_sum(Maybe(None), Maybe(5)))  # Maybe(None)
    print(ap_sum(MyList([]), MyList([4, 5, 6])))  # MyList([])
    print(
        ap_sum(MyList([1, 2, 3]), MyList([4, 5, 6]))
    )  # MyList([5, 6, 7, 6, 7, 8, 7, 8, 9])

    # semigroup examples
    print(mappend(OneTwoMany.ONE, OneTwoMany.ONE))  # OneTwoMany.TWO
    print(mappend(OneTwoMany.ONE, OneTwoMany.TWO))  # OneTwoMany.MANY
    print(mappend(OneTwoMany.ONE, OneTwoMany.MANY))  # OneTwoMany.MANY
