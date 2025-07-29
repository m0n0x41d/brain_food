import json
import os

from returns.curry import curry
from returns.io import IO
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success
from returns.unsafe import unsafe_perform_io


# Example 1: Maybe as a monad for safe handling of None values
def safe_divide(x: float, y: float) -> Maybe[float]:
    if y == 0:
        return Nothing
    return Some(x / y)


def safe_sqrt(x: float) -> Maybe[float]:
    if x < 0:
        return Nothing
    return Some(x**0.5)


# Chain of safe operations (monadic composition)
def safe_calculation(a: float, b: float, c: float) -> Maybe[float]:
    return (
        safe_divide(a, b)
        .bind(safe_sqrt)  # bind allows chaining Maybe functions
        .map(lambda x: x * c)
    )  # map for regular functions


# Example 2: Result as a monad for error handling
class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def validate_email(email: str) -> Result[str, ValidationError]:
    if "@" not in email:
        return Failure(ValidationError("Email must contain @"))
    if len(email.split("@")) != 2:
        return Failure(ValidationError("Email must contain exactly one @"))
    return Success(email)


def validate_age(age: int) -> Result[int, ValidationError]:
    if age < 0:
        return Failure(ValidationError("Age cannot be negative"))
    if age > 150:
        return Failure(ValidationError("Age cannot be greater than 150"))
    return Success(age)


class User:
    def __init__(self, email: str, age: int):
        self.email = email
        self.age = age

    def __repr__(self):
        return f"User(email='{self.email}', age={self.age})"


@curry
def create_user(email: str, age: int) -> User:
    return User(email, age)


def validate_and_create_user(
    email: str, age: int
) -> Result[User, list[ValidationError]]:
    email_result = validate_email(email)
    age_result = validate_age(age)

    # Apply curried function to two Results
    # This is an example of applicative functor (built on monoids)
    return age_result.apply(email_result.apply(Result.from_value(create_user)))


# Example 3: IO as a monad for composing side effects
def read_config_file(filename: str) -> IO[dict]:
    def _read():
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    return IO(_read)


def log_action(message: str) -> IO[None]:
    def _log():
        print(f"[LOG] {message}")
        return None

    return IO(_log)


def process_config(config: dict) -> IO[dict]:
    def _process():
        processed = {
            k: v.upper() if isinstance(v, str) else v for k, v in config.items()
        }
        return processed

    return IO(_process)


def config_pipeline(filename: str) -> IO[dict]:
    return (
        log_action(f"Starting to read {filename}")
        .bind(lambda _: read_config_file(filename))  # Read file
        .bind(
            lambda config: log_action(f"Read config: {config}").bind(
                lambda _: process_config(config).map(lambda processed: processed)
            )
        )  # Process
        .bind(
            lambda processed: log_action(f"Processed config: {processed}").map(
                lambda _: processed
            )
        )
    )  # Return result


# Demonstration of working with monads through returns
if __name__ == "__main__":
    print("=== Example 1: Maybe monad ===")

    # Successful case
    result1 = safe_calculation(100, 4, 2)  # (100/4) -> sqrt(25) -> 5*2 = 10
    print(f"safe_calculation(100, 4, 2) = {result1}")

    # Division by zero case
    result2 = safe_calculation(100, 0, 2)
    print(f"safe_calculation(100, 0, 2) = {result2}")

    # Negative number under square root case
    result3 = safe_calculation(100, -4, 2)  # 100/(-4) = -25, sqrt(-25) = Nothing
    print(f"safe_calculation(100, -4, 2) = {result3}")

    print("\n=== Example 2: Result monad ===")

    # Successful validation
    user_result1 = validate_and_create_user("john@example.com", 25)
    print(f"Valid user: {user_result1}")

    # Failed validation (multiple errors)
    user_result2 = validate_and_create_user("invalid-email", -5)
    print(f"Invalid user: {user_result2}")

    print("\n=== Example 3: IO monad ===")

    # Create test config file
    test_config = {"name": "test", "version": "1.0", "debug": True}
    with open("test_config.json", "w") as f:
        json.dump(test_config, f)

    # Run processing pipeline
    pipeline_result = config_pipeline("test_config.json")
    final_config = unsafe_perform_io(pipeline_result)  # Execute IO action
    print(f"Final config: {final_config}")

    os.remove("test_config.json")

    print("\n=== Demonstration of monoidal properties ===")

    # Maybe as monoid: Some(x) <> Nothing = Some(x)
    some_value = Some(42)
    nothing_value = Nothing

    # In returns Maybe doesn't have direct mappend, but we can emulate through bind
    def maybe_first(m1: Maybe, m2: Maybe) -> Maybe:
        return m1.bind(lambda x: Some(x)) or m2

    print(f"Some(42) <> Nothing = {maybe_first(some_value, nothing_value)}")
    print(f"Nothing <> Some(42) = {maybe_first(nothing_value, some_value)}")
    print(f"Nothing <> Nothing = {maybe_first(nothing_value, nothing_value)}")
