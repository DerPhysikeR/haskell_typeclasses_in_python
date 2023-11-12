from enum import Enum, auto
from typing import Any, Callable, Iterator, Protocol, Self


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


class Monoid(Protocol):
    @classmethod
    def mempty(cls) -> Self:  # mempty
        ...

    # To be a Monoid, the object has to be a Semigroup first, the simplest way to
    # express this in Python is to just require this method here too.
    def mappend(self, other: Self) -> Self:  # <>
        ...


class Monad(Protocol):
    def bind(self, fun: Callable) -> Self:  # >>=
        ...

    # def then_(self, other: Self) -> Self: # >>
    #     ...

    def return_(self, something: Any) -> Self:  # return
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

    @classmethod
    def return_(cls, value: Any) -> Self:
        return cls(value)

    def bind(self, fun: Callable) -> Self:
        if self._value is None:
            return self.__class__(None)
        return fun(self._value)


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

    def mappend(self, other: Self) -> Self:  # semigroup
        return self.__class__(self._list + other._list)

    @classmethod
    def mempty(cls) -> Self:  # monoid
        return cls([])


class OneTwoMany(Enum):
    ONE = auto()
    TWO = auto()
    MANY = auto()

    def mappend(self, other: Self) -> Self:  # Semigroup
        if self == self.ONE and other == self.ONE:
            return self.__class__(self.TWO)
        return self.__class__(self.MANY)


def square(arg: Functor) -> Functor:
    return arg.fmap(lambda x: x * x)


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


def mconcat(mylist_of_monoids: MyList) -> Monoid:
    result = mylist_of_monoids.mempty()  # TODO: This should be mempty of its content
    for item in mylist_of_monoids:
        result = result.mappend(item)
    return result


def divide_twelve_by(x) -> Maybe:
    if x == 0:
        return Maybe(None)
    return Maybe(12 / x)


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

    # monoid examples
    print(mconcat(MyList([])))  # MyList([])
    print(
        mconcat(MyList([MyList([1, 2, 3]), MyList([4, 5, 6])]))
    )  # MyList([1, 2, 3, 4, 5, 6])

    # monad examples
    print(Maybe(None).bind(divide_twelve_by))  # Maybe(None)
    print(Maybe(0).bind(divide_twelve_by))  # Maybe(None)
    print(Maybe(2).bind(divide_twelve_by))  # Maybe(6.0)
    print(Maybe(2).bind(divide_twelve_by).bind(divide_twelve_by))  # Maybe(2.0)
    print(Maybe.return_(2).bind(divide_twelve_by).bind(divide_twelve_by))  # Maybe(2.0)
