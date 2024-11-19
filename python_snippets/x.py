from __future__ import annotations
from typing import TypeVar, Generic, Type
from dataclasses import dataclass
from enum import Enum, auto
import pytest

class PushStatus(Enum):
    NIL = auto()
    OK = auto()
    ERR = auto()

class PopStatus(Enum):
    NIL = auto()
    OK = auto()
    ERR = auto()

class PeekStatus(Enum):
    NIL = auto()
    OK = auto()
    ERR = auto()

T = TypeVar('T')
S = TypeVar('S', bound='AbstractBoundedStack[T, any]') # type: ignore[valid-type]

class AbstractBoundedStack(Generic[T, S]):
    _element_type: Type[T]
    
    def __init__(self, element_type: Type[T]) -> None:
        self._element_type = element_type
        
    @property
    def peek_status(self) -> PeekStatus:
        raise NotImplementedError

    @property
    def pop_status(self) -> PopStatus:
        raise NotImplementedError

    @property
    def push_status(self) -> PushStatus:
        raise NotImplementedError

    @property
    def max_size(self) -> int:
        raise NotImplementedError

    def push(self, value: T) -> S:
        raise NotImplementedError

    def pop(self) -> S:
        raise NotImplementedError

    def clear(self) -> S:
        raise NotImplementedError

    def peek(self) -> tuple[T, S]:
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError

@dataclass
class BoundedStack(AbstractBoundedStack[T, 'BoundedStack[T]']):
    _element_type: Type[T]
    _stack: tuple[T, ...] = ()
    _max_size: int = 32
    _peek_status: PeekStatus = PeekStatus.NIL
    _pop_status: PopStatus = PopStatus.NIL
    _push_status: PushStatus = PushStatus.NIL

    @property
    def peek_status(self) -> PeekStatus:
        return self._peek_status

    @property
    def pop_status(self) -> PopStatus:
        return self._pop_status

    @property
    def push_status(self) -> PushStatus:
        return self._push_status

    @property
    def max_size(self) -> int:
        return self._max_size

    def push(self, value: T) -> 'BoundedStack[T]':
        if not isinstance(value, self._element_type):
            raise TypeError(f"Expected {self._element_type}, got {type(value)}")
            
        if self.size() >= self.max_size:
            return BoundedStack(
                self._element_type,
                self._stack,
                self._max_size,
                self._peek_status,
                self._pop_status,
                PushStatus.ERR
            )
        return BoundedStack(
            self._element_type,
            self._stack + (value,),
            self._max_size,
            self._peek_status,
            self._pop_status,
            PushStatus.OK
        )

    def pop(self) -> 'BoundedStack[T]':
        if self.size() > 0:
            return BoundedStack(
                self._element_type,
                self._stack[:-1],
                self._max_size,
                self._peek_status,
                PopStatus.OK,
                self._push_status
            )
        return BoundedStack(
            self._element_type,
            self._stack,
            self._max_size,
            self._peek_status,
            PopStatus.ERR,
            self._push_status
        )

    def clear(self) -> 'BoundedStack[T]':
        return BoundedStack(
            self._element_type,
            (),
            self._max_size,
            PeekStatus.NIL,
            PopStatus.NIL,
            PushStatus.NIL
        )

    def peek(self) -> tuple[T, 'BoundedStack[T]']:
        if self.size() > 0:
            return self._stack[-1], BoundedStack(
                self._element_type,
                self._stack,
                self._max_size,
                PeekStatus.OK,
                self._pop_status,
                self._push_status
            )
        raise ValueError("Stack is empty")

    def size(self) -> int:
        return len(self._stack)

    @classmethod
    def new_stack(cls, _element_type: Type[T]) -> 'BoundedStack[T]':
        """Factory method for creating properly typed stacks"""
        return cls(_element_type=_element_type)


class TestBoundedStack:
    @pytest.fixture
    def empty_stack(self) -> BoundedStack[int]:
        return BoundedStack.new_stack(int)

    @pytest.fixture
    def stack_with_items(self) -> BoundedStack[int]:
        stack = BoundedStack.new_stack(int)
        stack = stack.push(1)
        return stack.push(2)

    def test_initial_state(self, empty_stack: BoundedStack[int]) -> None:
        assert empty_stack.size() == 0
        assert empty_stack.peek_status == PeekStatus.NIL
        assert empty_stack.pop_status == PopStatus.NIL
        assert empty_stack.push_status == PushStatus.NIL
        assert empty_stack.max_size == 32

    def test_push_success(self, empty_stack: BoundedStack[int]) -> None:
        stack = empty_stack.push(1)
        assert stack.size() == 1
        assert stack.push_status == PushStatus.OK

        value, _ = stack.peek()
        assert value == 1

    def test_push_when_full(self) -> None:
        stack = BoundedStack(int, _max_size=1)
        stack = stack.push(1)
        stack = stack.push(2)
        assert stack.push_status == PushStatus.ERR
        assert stack.size() == 1

    def test_pop_success(self, stack_with_items: BoundedStack[int]) -> None:
        stack = stack_with_items.pop()
        assert stack.pop_status == PopStatus.OK
        assert stack.size() == 1

        value, _ = stack.peek()
        assert value == 1

    def test_pop_empty(self, empty_stack: BoundedStack[int]) -> None:
        stack = empty_stack.pop()
        assert stack.pop_status == PopStatus.ERR
        assert stack.size() == 0

    def test_peek_success(self, stack_with_items: BoundedStack[int]) -> None:
        value, stack = stack_with_items.peek()
        assert value == 2
        assert stack.peek_status == PeekStatus.OK
        assert stack.size() == 2

    def test_peek_empty(self, empty_stack: BoundedStack[int]) -> None:
        with pytest.raises(ValueError, match="Stack is empty"):
            empty_stack.peek()

    def test_clear(self, stack_with_items: BoundedStack[int]) -> None:
        stack = stack_with_items.clear()
        assert stack.size() == 0
        assert stack.peek_status == PeekStatus.NIL
        assert stack.pop_status == PopStatus.NIL
        assert stack.push_status == PushStatus.NIL

    def test_type_safety(self) -> None:
        stack = BoundedStack.new_stack(str)
        stack = stack.push("hello")
        value, _ = stack.peek()
        assert isinstance(value, str)
        
        with pytest.raises(TypeError):
            stack.push(123)


if __name__ == "__main__":
    pytest.main([__file__])
