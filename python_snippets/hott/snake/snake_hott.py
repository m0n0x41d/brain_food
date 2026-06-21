from typing import Callable, List, Tuple

from core.base_types import Path, Product, Sum, unit
from core.dependent_types import Pi
from core.hits import NTorus


class GameField:
    def __init__(self, width: int, height: int):
        """
        Initialize the game field as a two-dimensional torus.

        Args:
            width: Game field width.
            height: Game field height.
        """
        # Use a 2D torus as the base topology for the game.
        self.torus = NTorus(2)
        if self.torus.dimension() != 2:
            raise ValueError("GameField must be backed by a 2-torus")

        self.width = width
        self.height = height

    def get_dimensions(self) -> Tuple[int, int]:
        """Return the game field dimensions."""
        return (self.width, self.height)

    def get_torus(self) -> NTorus:
        """Return the HoTT 2-torus structure backing the game field."""
        return self.torus

    def get_horizontal_loop(self):
        """Return the torus fundamental loop along the X axis."""
        return self.torus.loop(0)

    def get_vertical_loop(self):
        """Return the torus fundamental loop along the Y axis."""
        return self.torus.loop(1)

    def create_position(self, x: int, y: int) -> Product:
        """
        Create a game field position using the Product type.

        Args:
            x: X coordinate, wrapped according to the torus topology.
            y: Y coordinate, wrapped according to the torus topology.

        Returns:
            Product representing the (x, y) position.
        """
        # Wrap coordinates around the torus boundaries.
        wrapped_x = x % self.width
        wrapped_y = y % self.height

        # Use Product to represent the position.
        return Product(wrapped_x, wrapped_y)

    def normalize_position(self, position: Product) -> Product:
        """
        Normalize a field position into a point of the 2-torus [0, 1] x [0, 1].
        """
        normalized_x = position.first_value / self.width
        normalized_y = position.second_value / self.height

        return Product(normalized_x, normalized_y)

    def calculate_axis_wrap(
        self,
        start_value: int,
        end_value: int,
        size: int,
    ) -> int:
        """
        Calculate the integer torus wrap for the shortest path along one axis.
        """
        direct_delta = end_value - start_value
        positive_loop_delta = end_value + size - start_value
        negative_loop_delta = end_value - size - start_value
        candidates = [
            Product(direct_delta, 0),
            Product(positive_loop_delta, 1),
            Product(negative_loop_delta, -1),
        ]
        shortest_candidate = min(
            candidates,
            key=lambda candidate: (
                abs(candidate.first_value),
                abs(candidate.second_value),
            ),
        )

        return shortest_candidate.second_value

    def calculate_loop_count(self, start: Product, end: Product) -> Product:
        """
        Calculate wrap counts along the 2-torus fundamental loops.
        """
        self.get_horizontal_loop()
        self.get_vertical_loop()

        x_wraps = self.calculate_axis_wrap(
            start.first_value,
            end.first_value,
            self.width,
        )
        y_wraps = self.calculate_axis_wrap(
            start.second_value,
            end.second_value,
            self.height,
        )

        return Product(x_wraps, y_wraps)

    def calculate_torus_path(self, start: Product, end: Product) -> Product:
        """
        Create a 2-torus path as Product(Path, Product(x_wraps, y_wraps)).
        """
        normalized_start = self.normalize_position(start)
        normalized_end = self.normalize_position(end)
        base_path = Path(normalized_start, normalized_end)
        loop_count = self.calculate_loop_count(start, end)

        return Product(base_path, loop_count)

    def calculate_torus_path_with_loop_count(
        self,
        start: Product,
        end: Product,
        loop_count: Product,
    ) -> Product:
        """
        Create a 2-torus path with an explicit loop count.
        """
        normalized_start = self.normalize_position(start)
        normalized_end = self.normalize_position(end)
        base_path = Path(normalized_start, normalized_end)

        return Product(base_path, loop_count)

    def calculate_effective_delta(
        self,
        start: Product,
        end: Product,
        loop_count: Product,
    ) -> Product:
        """
        Calculate cell-space delta after choosing a torus loop count.
        """
        effective_dx = end.first_value + loop_count.first_value * self.width
        effective_dx = effective_dx - start.first_value
        effective_dy = end.second_value + loop_count.second_value * self.height
        effective_dy = effective_dy - start.second_value

        return Product(effective_dx, effective_dy)

    def calculate_delta_length(self, delta: Product) -> int:
        """
        Calculate Manhattan length for a snake trajectory delta.
        """
        return abs(delta.first_value) + abs(delta.second_value)

    def get_candidate_loop_counts(self) -> List[Product]:
        """
        Return loop-count candidates with at most one wrap per torus axis.
        """
        return [
            Product(x_wraps, y_wraps)
            for x_wraps in [-1, 0, 1]
            for y_wraps in [-1, 0, 1]
        ]

    def decompose_delta_to_directions(
        self,
        delta: Product,
        axis_order: Tuple[str, str],
    ) -> List[Sum]:
        """
        Decompose a cell-space delta into directions using a chosen axis order.
        """
        axis_directions = {
            "x": self._decompose_x_delta(delta.first_value),
            "y": self._decompose_y_delta(delta.second_value),
        }

        return [direction for axis in axis_order for direction in axis_directions[axis]]

    def _decompose_x_delta(self, dx: int) -> List[Sum]:
        if dx > 0:
            return [Direction.right() for _ in range(dx)]

        if dx < 0:
            return [Direction.left() for _ in range(abs(dx))]

        return []

    def _decompose_y_delta(self, dy: int) -> List[Sum]:
        if dy > 0:
            return [Direction.down() for _ in range(dy)]

        if dy < 0:
            return [Direction.up() for _ in range(abs(dy))]

        return []

    def trace_direction_positions(
        self,
        start: Product,
        directions: List[Sum],
    ) -> List[Product]:
        """
        Trace positions visited after applying directions from start.
        """
        positions = []
        current_position = start

        for direction in directions:
            dx, dy = Direction.get_delta(direction)
            current_position = self.move_position(current_position, dx, dy)
            positions.append(current_position)

        return positions

    def route_hits_positions(
        self,
        start: Product,
        directions: List[Sum],
        blocked_positions: List[Product],
    ) -> bool:
        """
        Check whether a route visits any blocked position.
        """
        visited_positions = self.trace_direction_positions(start, directions)

        return any(
            visited_position == blocked_position
            for visited_position in visited_positions
            for blocked_position in blocked_positions
        )

    def calculate_shortest_trajectory(
        self,
        start: Product,
        end: Product,
    ) -> Product:
        """
        Calculate the shortest torus trajectory without body constraints.
        """
        return self.calculate_shortest_trajectory_avoiding(start, end, [])

    def calculate_shortest_trajectory_avoiding(
        self,
        start: Product,
        end: Product,
        blocked_positions: List[Product],
    ) -> Product:
        """
        Calculate the shortest torus trajectory, preferring routes avoiding blocked cells.

        Returns:
            Product(torus_path, directions).
        """
        candidates = [
            self._build_trajectory_candidate(
                start,
                end,
                loop_count,
                axis_order,
                blocked_positions,
            )
            for loop_count in self.get_candidate_loop_counts()
            for axis_order in [("x", "y"), ("y", "x")]
        ]
        shortest_safe_candidates = [
            candidate
            for candidate in candidates
            if not candidate.second_value.second_value
        ]
        selectable_candidates = shortest_safe_candidates or candidates
        selected_candidate = min(
            selectable_candidates,
            key=lambda candidate: (
                candidate.second_value.first_value,
                len(candidate.first_value.second_value),
            ),
        )

        return selected_candidate.first_value

    def _build_trajectory_candidate(
        self,
        start: Product,
        end: Product,
        loop_count: Product,
        axis_order: Tuple[str, str],
        blocked_positions: List[Product],
    ) -> Product:
        torus_path = self.calculate_torus_path_with_loop_count(
            start,
            end,
            loop_count,
        )
        delta = self.calculate_effective_delta(start, end, loop_count)
        directions = self.decompose_delta_to_directions(delta, axis_order)
        length = self.calculate_delta_length(delta)
        hits_blocked = self.route_hits_positions(
            start,
            directions,
            blocked_positions,
        )

        return Product(
            Product(torus_path, directions),
            Product(length, hits_blocked),
        )

    def calculate_shortest_path_to_food(self, snake, food_position: Product) -> Product:
        """
        Calculate the shortest body-aware torus trajectory from snake head to food.
        """
        blocked_positions = snake.get_body()[1:]

        return self.calculate_shortest_trajectory_avoiding(
            snake.get_head(),
            food_position,
            blocked_positions,
        )

    def move_position(self, position: Product, dx: int, dy: int) -> Product:
        """
        Move a position by the given deltas using the torus topology.

        Args:
            position: Current position as Product.
            dx: X coordinate delta.
            dy: Y coordinate delta.

        Returns:
            New position as Product.
        """
        x, y = position.first_value, position.second_value
        return self.create_position(x + dx, y + dy)

    def move_on_torus(self, position: Product, dx: int, dy: int) -> Product:
        """
        Move a position and return the movement as a path on the 2-torus.

        Returns:
            Product(new_position, torus_path), where torus_path =
            Product(Path(normalized_start, normalized_end), Product(x_wraps, y_wraps)).
        """
        new_position = self.move_position(position, dx, dy)
        torus_path = self.calculate_torus_path(position, new_position)

        return Product(new_position, torus_path)

    def calculate_path(self, start: Product, end: Product) -> Path:
        """
        Create a Path between two game field positions.

        Args:
            start: Start position.
            end: End position.

        Returns:
            Path representing movement from start to end.
        """
        return Path(start, end)

    def positions_equal(self, pos1: Product, pos2: Product) -> bool:
        """
        Check whether two positions are equal.

        Args:
            pos1: First position.
            pos2: Second position.

        Returns:
            True when positions are equal, otherwise False.
        """
        return (
            pos1.first_value == pos2.first_value
            and pos1.second_value == pos2.second_value
        )


class GameEvent:
    """
    Represent game events using the HoTT Sum type.

    Events can be: continue game, food collected, or collision detected.
    """

    @staticmethod
    def continue_game() -> Sum:
        """The game continues normally."""
        return Sum.left(unit, "CONTINUE")

    @staticmethod
    def food_collected() -> Sum:
        """The snake collected food."""
        return Sum.right("FOOD_COLLECTED", unit)

    @staticmethod
    def collision_detected() -> Sum:
        """The snake collided with itself or a field boundary."""
        return Sum.right("COLLISION", unit)

    @staticmethod
    def is_continue(event: Sum) -> bool:
        """Check for the continue-game event."""
        return event.is_left_active

    @staticmethod
    def is_food_collected(event: Sum) -> bool:
        """Check for the food-collected event."""
        return not event.is_left_active and event.right_value == "FOOD_COLLECTED"

    @staticmethod
    def is_collision(event: Sum) -> bool:
        """Check for the collision event."""
        return not event.is_left_active and event.right_value == "COLLISION"


class Direction:
    """
    Represent movement directions using the HoTT Sum type.

    Each direction is a Sum variant with its corresponding coordinate delta.
    """

    @staticmethod
    def up() -> Sum:
        """Up direction (0, -1)."""
        return Sum.left((0, -1), "UP")

    @staticmethod
    def down() -> Sum:
        """Down direction (0, 1)."""
        return Sum.left((0, 1), "DOWN")

    @staticmethod
    def left() -> Sum:
        """Left direction (-1, 0)."""
        return Sum.left((-1, 0), "LEFT")

    @staticmethod
    def right() -> Sum:
        """Right direction (1, 0)."""
        return Sum.left((1, 0), "RIGHT")

    @staticmethod
    def get_delta(direction: Sum) -> Tuple[int, int]:
        """
        Extract the movement delta from a Sum direction.
        """
        return direction.match(
            lambda value: value,
            lambda _: (0, 0),  # Fallback variant.
        )

    @staticmethod
    def are_opposite(dir1: Sum, dir2: Sum) -> bool:
        """Check whether two directions are opposite."""
        delta1 = Direction.get_delta(dir1)
        delta2 = Direction.get_delta(dir2)

        return delta1[0] == -delta2[0] and delta1[1] == -delta2[1]

    @staticmethod
    def to_string(direction: Sum) -> str:
        """
        Return the string representation of a direction.
        """
        return direction.match(lambda _: direction.right_value, lambda _: "UNKNOWN")


class SnakeBody:
    """
    Represent the snake body as Product(head, tail).

    head: Head position.
    tail: List of remaining body positions.
    """

    def __init__(self, positions: List[Product]):
        if not positions:
            raise ValueError("SnakeBody must contain at least one position")

        if not all(isinstance(position, Product) for position in positions):
            raise TypeError("SnakeBody positions must be Product values")

        self.state = Product(positions[0], positions[1:])

    def get_head(self) -> Product:
        """Return the snake head position."""
        return self.state.first_value

    def get_tail(self) -> List[Product]:
        """Return body positions excluding the head."""
        return self.state.second_value

    def get_positions(self) -> List[Product]:
        """Return all snake positions."""
        return [self.get_head()] + self.get_tail()

    def contains_position(self, position: Product) -> bool:
        """Check whether a position belongs to the snake body."""
        return any(body_position == position for body_position in self.get_positions())


class Snake:
    """
    Represent the snake as Product(direction, body).

    direction: Movement direction as Sum.
    body: SnakeBody, where the first position is the head.
    """

    def __init__(self, direction: Sum, body):
        if isinstance(body, SnakeBody):
            snake_body = body
        else:
            snake_body = SnakeBody(body)

        self.state = Product(direction, snake_body)

    def get_direction(self) -> Sum:
        """Return the current snake direction."""
        return self.state.first_value

    def get_body_container(self) -> SnakeBody:
        """Return the snake body as a HoTT container."""
        return self.state.second_value

    def get_body(self) -> List[Product]:
        """Return snake body positions."""
        return self.get_body_container().get_positions()

    def get_head(self) -> Product:
        """Return the snake head position."""
        return self.get_body_container().get_head()

    def set_direction(self, direction: Sum):
        """Create a snake with an updated direction."""
        return Snake(direction, self.get_body_container())

    def contains_position(self, position: Product) -> bool:
        """Check whether the snake occupies a position."""
        return self.get_body_container().contains_position(position)


class GameState:
    """
    Represent the complete game state using HoTT Product types.

    The game state combines snake state, food position, score, and control flags.
    """

    def __init__(
        self,
        snake,
        food_position: Product,
        score: int = 0,
        is_demo: bool = False,
    ):
        """
        Initialize game state: snake, food position, score, and control flags.

        Args:
            snake: Snake object.
            food_position: Food position as Product.
            score: Current score. Defaults to 0.
            is_demo: Demo-mode flag. Defaults to False.
        """
        # Store snake and food together in Product.
        self.entity_state = Product(snake, food_position)

        # Store score and demo mode together in Product.
        self.control_state = Product(score, is_demo)

        # GameState = Product(Product(snake, food), Product(score, is_demo))
        self.state = Product(self.entity_state, self.control_state)

        # Game control flags.
        self.paused = False
        self.game_over = False
        self.quit_requested = False

    def get_snake(self):
        """Return the snake from the game state."""
        return self.entity_state.first_value

    def get_food_position(self) -> Product:
        """Return the food position."""
        return self.entity_state.second_value

    def get_score(self) -> int:
        """Return the current score."""
        return self.control_state.first_value

    def is_demo(self) -> bool:
        """Check demo mode."""
        return self.control_state.second_value

    def is_paused(self) -> bool:
        """Check whether the game is paused."""
        return self.paused

    def is_game_over(self) -> bool:
        """Check whether the game is over."""
        return self.game_over

    def is_quit_requested(self) -> bool:
        """Check whether quitting was requested."""
        return self.quit_requested

    def with_new_snake(self, new_snake):
        """Create a state with an updated snake."""
        new_state = GameState(
            new_snake,
            self.get_food_position(),
            self.get_score(),
            self.is_demo(),
        )
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state

    def with_new_food(self, new_food_position: Product):
        """
        Create a state with an updated food position.
        """
        new_state = GameState(
            self.get_snake(),
            new_food_position,
            self.get_score(),
            self.is_demo(),
        )
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state

    def with_incremented_score(self, points: int = 1):
        """Create a state with an incremented score."""
        new_score = self.get_score() + points
        new_state = GameState(
            self.get_snake(),
            self.get_food_position(),
            new_score,
            self.is_demo(),
        )
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state

    def with_toggled_pause(self):
        """
        Create a state with the pause flag toggled.
        """
        new_state = GameState(
            self.get_snake(),
            self.get_food_position(),
            self.get_score(),
            self.is_demo(),
        )
        new_state.paused = not self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state

    def with_game_over(self, is_game_over: bool = True):
        """
        Create a state with the game-over flag set.
        """
        new_state = GameState(
            self.get_snake(),
            self.get_food_position(),
            self.get_score(),
            self.is_demo(),
        )
        new_state.paused = self.paused
        new_state.game_over = is_game_over
        new_state.quit_requested = self.quit_requested
        return new_state

    def with_quit_flag(self, should_quit: bool = True):
        """
        Create a state with the quit flag set.
        """
        new_state = GameState(
            self.get_snake(),
            self.get_food_position(),
            self.get_score(),
            self.is_demo(),
        )
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = should_quit
        return new_state

    def with_demo_mode(self, is_demo: bool):
        """Create a state with an updated demo-mode flag."""
        new_state = GameState(
            self.get_snake(),
            self.get_food_position(),
            self.get_score(),
            is_demo,
        )
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state


class InputHandler:
    """
    Handle user input using the HoTT Pi type.

    Map key presses to game-state transformations.
    """

    def __init__(self, initial_state: GameState, game_field=None):
        """
        Initialize the input handler with the initial game state.

        Args:
            initial_state: Initial game state.
        """
        self.initial_state = initial_state
        self.game_field = game_field
        self.key_mapping = self._create_key_mapping()
        self.demo_strategy = self._create_demo_strategy()

    def _create_key_mapping(self) -> Pi:
        """
        Create a Pi mapping from keys to state transformation functions.

        Returns:
            Pi mapping from keys to functions.
        """
        # Define the domain and codomain for this Pi type.
        # Domain: possible input keys.
        # Codomain: functions GameState -> GameState.
        return Pi(
            domain=str,  # Key input as string.
            codomain=lambda _: Callable[[GameState], GameState],
            # Functions that transform game state.
            function=lambda key: {
                "KEY_UP": lambda state: self._change_direction(state, Direction.up()),
                "KEY_DOWN": lambda state: self._change_direction(
                    state, Direction.down()
                ),
                "KEY_LEFT": lambda state: self._change_direction(
                    state, Direction.left()
                ),
                "KEY_RIGHT": lambda state: self._change_direction(
                    state, Direction.right()
                ),
                "q": lambda state: self._set_quit_flag(state),
                "p": lambda state: self._toggle_pause_flag(state),
                # Default case: return state unchanged.
                "default": lambda state: state,
            }.get(key, lambda state: state),  # Default: identity function.
        )

    def _create_demo_strategy(self) -> Pi:
        """
        Create a Pi strategy from GameState to Direction for demo mode.
        """
        return Pi(
            domain=GameState,
            codomain=lambda _: Sum,
            function=lambda state: self._choose_demo_direction(state),
        )

    def _choose_demo_direction(self, state: GameState) -> Sum:
        if self.game_field is None:
            return state.get_snake().get_direction()

        trajectory = self.game_field.calculate_shortest_path_to_food(
            state.get_snake(),
            state.get_food_position(),
        )
        directions = trajectory.second_value

        if directions:
            return directions[0]

        return state.get_snake().get_direction()

    def _change_direction(self, state: GameState, direction: Sum) -> GameState:
        snake = state.get_snake()
        new_snake = snake.set_direction(direction)
        return state.with_new_snake(new_snake)

    def _apply_demo_strategy(self, state: GameState) -> GameState:
        direction = self.demo_strategy(state)

        return self._change_direction(state, direction)

    def _toggle_pause_flag(self, state: GameState) -> GameState:
        """
        Create a new game state with the pause flag toggled.

        Args:
            state: Current game state.

        Returns:
            New state with toggled pause flag.
        """
        return state.with_toggled_pause()

    def _set_quit_flag(self, state: GameState) -> GameState:
        """
        Create a new game state with the quit flag set.

        Args:
            state: Current game state.

        Returns:
            New state with quit flag set.
        """
        return state.with_quit_flag(True)

    def handle_input(self, key: str, state: GameState) -> GameState:
        """
        Handle user input and return the updated game state.

        Args:
            key: User-pressed key.
            state: Current game state.

        Returns:
            Updated game state.
        """
        if state.is_demo():
            return self._apply_demo_strategy(state)

        # Use the Pi type to get the function matching this key.
        transform_function = self.key_mapping(key)

        # Apply the function to the current state.
        return transform_function(state)


def positions_equal(pos1: Product, pos2: Product) -> bool:
    """Check whether two Product positions are equal."""
    return (
        pos1.first_value == pos2.first_value and pos1.second_value == pos2.second_value
    )


def position_is_in(position: Product, positions: List[Product]) -> bool:
    """Check whether a position appears in a position list."""
    return any(positions_equal(position, candidate) for candidate in positions)


def move_snake(
    snake: Snake,
    direction: Sum,
    game_field: GameField,
    grow: bool,
) -> Product:
    """
    Move the snake by one cell and keep torus movement evidence.

    Returns:
        Product(new_snake, torus_movement), where torus_movement =
        Product(new_head_position, torus_path).
    """
    dx, dy = Direction.get_delta(direction)
    movement = game_field.move_on_torus(snake.get_head(), dx, dy)
    new_head = movement.first_value
    current_body = snake.get_body()
    next_body = [new_head] + current_body

    if not grow:
        next_body = next_body[:-1]

    new_snake = Snake(direction, next_body)

    return Product(new_snake, movement)


def snake_would_collide_with_body(
    snake: Snake,
    next_head: Product,
    grow: bool,
) -> bool:
    """
    Check self-collision for the next head position.

    If the snake is not growing, the last tail cell is allowed because it moves away.
    """
    blocked_body = snake.get_body()[1:]

    if not grow:
        blocked_body = blocked_body[:-1]

    return any(
        positions_equal(next_head, body_position) for body_position in blocked_body
    )


def find_next_food_position(game_field: GameField, snake: Snake) -> Sum:
    """
    Find a free field cell for food.

    Returns:
        Sum.left(position, "FOOD_AVAILABLE") or
        Sum.right("NO_FREE_CELL", unit).
    """
    return find_next_food_position_avoiding(game_field, snake, [])


def find_next_food_position_avoiding(
    game_field: GameField,
    snake: Snake,
    avoided_positions: List[Product],
) -> Sum:
    """
    Find a free food position while preferring cells far from the snake head.
    """
    candidates = get_food_candidates(game_field, snake, avoided_positions)

    if candidates:
        return Sum.left(
            select_food_candidate(game_field, snake, candidates),
            "FOOD_AVAILABLE",
        )

    fallback_candidates = get_food_candidates(game_field, snake, [])

    if fallback_candidates:
        return Sum.left(
            select_food_candidate(game_field, snake, fallback_candidates),
            "FOOD_AVAILABLE",
        )

    return Sum.right("NO_FREE_CELL", unit)


def get_food_candidates(
    game_field: GameField,
    snake: Snake,
    avoided_positions: List[Product],
) -> List[Product]:
    """
    Return field cells that are not occupied by the snake or explicitly avoided.
    """
    width, height = game_field.get_dimensions()
    candidates = []

    for y in range(height):
        for x in range(width):
            candidate = game_field.create_position(x, y)

            if snake.contains_position(candidate):
                continue

            if position_is_in(candidate, avoided_positions):
                continue

            candidates.append(candidate)

    return candidates


def select_food_candidate(
    game_field: GameField,
    snake: Snake,
    candidates: List[Product],
) -> Product:
    """
    Select the farthest candidate by shortest torus trajectory length.
    """
    return max(
        candidates,
        key=lambda candidate: (
            len(
                game_field.calculate_shortest_path_to_food(
                    snake, candidate
                ).second_value
            ),
            candidate.second_value,
            candidate.first_value,
        ),
    )


def calculate_next_head_position(snake: Snake, game_field: GameField) -> Product:
    """
    Calculate the next head position for the snake's current direction.
    """
    dx, dy = Direction.get_delta(snake.get_direction())

    return game_field.move_position(snake.get_head(), dx, dy)


def create_initial_state(game_field: GameField, is_demo: bool) -> GameState:
    """
    Create a small initial state for the terminal loop.
    """
    width, height = game_field.get_dimensions()
    head = game_field.create_position(width // 2, height // 2)
    tail = game_field.create_position(width // 2 - 1, height // 2)
    snake = Snake(Direction.right(), [head, tail])
    food_choice = find_next_food_position(game_field, snake)

    if food_choice.is_left_active:
        return GameState(snake, food_choice.left_value, 0, is_demo)

    return GameState(snake, head, 0, is_demo).with_game_over(True)


def apply_demo_strategy(state: GameState, game_field: GameField) -> GameState:
    """
    Apply the Pi-typed demo strategy when demo mode is enabled.
    """
    if not state.is_demo():
        return state

    handler = InputHandler(state, game_field)

    return handler.handle_input("", state)


def apply_loop_key(state: GameState, game_field: GameField, key: str) -> GameState:
    """
    Apply terminal shell controls before regular input handling.
    """
    if key == "":
        return state

    if key == "q":
        return state.with_quit_flag(True)

    if key == "p":
        return state.with_toggled_pause()

    if key == "d":
        return state.with_demo_mode(not state.is_demo())

    handler = InputHandler(state, game_field)

    return handler.handle_input(key, state)


def advance_game_state(state: GameState, game_field: GameField) -> Product:
    """
    Advance the game by one tick.

    Returns:
        Product(next_state, game_event).
    """
    if state.is_paused() or state.is_game_over() or state.is_quit_requested():
        return Product(state, GameEvent.continue_game())

    snake = state.get_snake()
    direction = snake.get_direction()
    dx, dy = Direction.get_delta(direction)
    next_head = game_field.move_position(snake.get_head(), dx, dy)
    grows = positions_equal(next_head, state.get_food_position())
    collided = snake_would_collide_with_body(snake, next_head, grows)

    if collided:
        return Product(state.with_game_over(True), GameEvent.collision_detected())

    movement = move_snake(snake, direction, game_field, grows)
    moved_snake = movement.first_value
    moved_state = state.with_new_snake(moved_snake)

    if not grows:
        return Product(moved_state, GameEvent.continue_game())

    avoided_food_positions = [
        calculate_next_head_position(moved_snake, game_field),
    ]
    food_choice = find_next_food_position_avoiding(
        game_field,
        moved_snake,
        avoided_food_positions,
    )
    scored_state = moved_state.with_incremented_score()

    if food_choice.is_left_active:
        return Product(
            scored_state.with_new_food(food_choice.left_value),
            GameEvent.food_collected(),
        )

    return Product(
        scored_state.with_game_over(True),
        GameEvent.food_collected(),
    )


class Renderer:
    def __init__(self, term, game_field):
        """Initialize the renderer with a terminal and game field."""
        self.term = term
        self.game_field = game_field
        self.width, self.height = game_field.get_dimensions()

    def render(self, game_state: GameState, game_over: bool, paused: bool) -> None:
        """Render the game state."""
        home = getattr(self.term, "home", "")
        clear = getattr(self.term, "clear", "")

        if home or clear:
            print(f"{home}{clear}", end="")
        else:
            print(self.term.move(0, 0), end="")

        # Get render data.
        snake = game_state.get_snake()
        food_position = game_state.get_food_position()
        score = game_state.get_score()

        # Build the screen as lines.
        screen = []

        # Top border.
        screen.append("+" + "-" * (self.width * 2) + "+")

        # Game field with snake and food.
        for y in range(self.height):
            line = "|"
            for x in range(self.width):
                position = self.game_field.create_position(x, y)

                # Snake rendering.
                if snake.contains_position(position):
                    head_position = snake.get_head()
                    if (
                        position.first_value == head_position.first_value
                        and position.second_value == head_position.second_value
                    ):
                        line += self.term.green("@@")  # Head.
                    else:
                        line += self.term.green("##")  # Body.
                # Food rendering.
                elif (
                    position.first_value == food_position.first_value
                    and position.second_value == food_position.second_value
                ):
                    line += self.term.red("()")
                else:
                    line += "  "  # Empty space.
            line += "|"
            screen.append(line)

        # Bottom border.
        screen.append("+" + "-" * (self.width * 2) + "+")

        # Game info.
        screen.append(f"Score: {score}")
        screen.append(f"Mode: {'DEMO' if game_state.is_demo() else 'MANUAL'}")

        # Game status.
        if game_over:
            screen.append(self.term.red(f"Game Over! Final Score: {score}"))
            screen.append(self.term.yellow("Press 'q' to quit, 'd' to toggle demo."))
        elif paused:
            screen.append(
                self.term.yellow(
                    "Game Paused. Press 'p' to resume, 'd' for demo, 'q' to quit."
                )
            )
        else:
            screen.append("Arrows move, 'd' toggles demo, 'p' pauses, 'q' quits.")

        # Print the whole screen.
        print("\n".join(screen), flush=True)


def normalize_terminal_key(key) -> str:
    """
    Normalize a blessed key object into the strings used by InputHandler.
    """
    if not key:
        return ""

    if getattr(key, "is_sequence", False):
        return key.name

    return str(key)


def run_blessed_game() -> None:
    """
    Run the interactive blessed terminal loop.
    """
    from blessed import Terminal

    term = Terminal()
    game_field = GameField(20, 12)
    state = create_initial_state(game_field, True)
    renderer = Renderer(term, game_field)
    tick_seconds = 0.12

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        renderer.render(state, state.is_game_over(), state.is_paused())

        while not state.is_quit_requested():
            key = normalize_terminal_key(term.inkey(timeout=tick_seconds))
            state = apply_loop_key(state, game_field, key)
            state = apply_demo_strategy(state, game_field)
            tick = advance_game_state(state, game_field)
            state = tick.first_value
            renderer.render(state, state.is_game_over(), state.is_paused())


if __name__ == "__main__":
    run_blessed_game()
