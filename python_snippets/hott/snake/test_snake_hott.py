import io
import unittest
from contextlib import redirect_stdout

from core.base_types import Path, Product
from snake_hott import (
    Direction,
    GameField,
    GameState,
    InputHandler,
    Renderer,
    Snake,
    SnakeBody,
    advance_game_state,
    apply_demo_strategy,
    apply_loop_key,
    create_initial_state,
    find_next_food_position,
    find_next_food_position_avoiding,
    move_snake,
)


class PlainTerm:
    def move(self, x, y):
        return ""

    def green(self, value):
        return value

    def red(self, value):
        return value

    def yellow(self, value):
        return value


def make_field() -> GameField:
    return GameField(10, 5)


def make_snake(field: GameField) -> Snake:
    return Snake(
        Direction.right(),
        [
            field.create_position(2, 1),
            field.create_position(1, 1),
        ],
    )


class SnakeTests(unittest.TestCase):
    def test_snake_body_is_non_empty_product_container(self):
        field = make_field()
        head = field.create_position(2, 1)
        tail = field.create_position(1, 1)
        body = SnakeBody([head, tail])

        self.assertEqual(body.state, Product(head, [tail]))
        self.assertEqual(body.get_head(), head)
        self.assertEqual(body.get_tail(), [tail])
        self.assertEqual(body.get_positions(), [head, tail])
        self.assertTrue(body.contains_position(head))

    def test_snake_body_rejects_empty_or_non_position_body(self):
        field = make_field()
        head = field.create_position(2, 1)

        with self.assertRaises(ValueError):
            SnakeBody([])

        with self.assertRaises(TypeError):
            SnakeBody([head, None])

    def test_snake_is_product_of_direction_and_body_container(self):
        field = make_field()
        snake = make_snake(field)
        changed_snake = snake.set_direction(Direction.up())

        self.assertIsInstance(snake.state, Product)
        self.assertIsInstance(snake.get_body_container(), SnakeBody)
        self.assertEqual(snake.get_head(), field.create_position(2, 1))
        self.assertTrue(snake.contains_position(field.create_position(1, 1)))
        self.assertEqual(changed_snake.get_body(), snake.get_body())
        self.assertEqual(Direction.get_delta(changed_snake.get_direction()), (0, -1))

    def test_game_state_matches_assignment_product_shape(self):
        field = make_field()
        snake = make_snake(field)
        food = field.create_position(8, 3)
        state = GameState(snake, food, 7, True)

        self.assertEqual(state.entity_state, Product(snake, food))
        self.assertEqual(state.control_state, Product(7, True))
        self.assertEqual(
            state.state,
            Product(
                Product(snake, food),
                Product(7, True),
            ),
        )
        self.assertEqual(state.get_score(), 7)
        self.assertTrue(state.is_demo())

    def test_game_state_transformations_preserve_demo_mode(self):
        field = make_field()
        snake = make_snake(field)
        food = field.create_position(8, 3)
        state = GameState(snake, food, 7, True)
        scored_state = state.with_incremented_score()
        manual_state = scored_state.with_demo_mode(False)

        self.assertEqual(scored_state.get_score(), 8)
        self.assertTrue(scored_state.is_demo())
        self.assertFalse(manual_state.is_demo())
        self.assertEqual(manual_state.get_score(), 8)

    def test_game_field_exposes_two_torus_structure(self):
        field = make_field()

        self.assertEqual(field.get_torus().dimension(), 2)
        self.assertEqual(field.get_horizontal_loop().dimension_index, 0)
        self.assertEqual(field.get_vertical_loop().dimension_index, 1)

    def test_game_field_normalizes_positions_to_unit_square(self):
        field = make_field()
        position = field.create_position(5, 4)

        self.assertEqual(field.normalize_position(position), Product(0.5, 0.8))

    def test_game_field_calculates_torus_path_with_loop_count(self):
        field = make_field()
        examples = [
            ((2, 2), (4, 2), (0, 0)),
            ((9, 3), (0, 3), (1, 0)),
            ((0, 3), (9, 3), (-1, 0)),
            ((2, 4), (2, 0), (0, 1)),
            ((2, 0), (2, 4), (0, -1)),
        ]

        for start, end, expected_loop_count in examples:
            with self.subTest(start=start, end=end):
                start_position = field.create_position(*start)
                end_position = field.create_position(*end)
                torus_path = field.calculate_torus_path(start_position, end_position)
                base_path = torus_path.first_value
                loop_count = torus_path.second_value

                self.assertIsInstance(base_path, Path)
                self.assertEqual(
                    base_path.start,
                    field.normalize_position(start_position),
                )
                self.assertEqual(
                    base_path.end,
                    field.normalize_position(end_position),
                )
                self.assertEqual(loop_count, Product(*expected_loop_count))

    def test_game_field_moves_on_torus_with_path_evidence(self):
        field = make_field()
        start = field.create_position(9, 3)
        movement = field.move_on_torus(start, 1, 0)
        new_position = movement.first_value
        torus_path = movement.second_value
        base_path = torus_path.first_value
        loop_count = torus_path.second_value

        self.assertEqual(new_position, field.create_position(0, 3))
        self.assertEqual(base_path.start, field.normalize_position(start))
        self.assertEqual(base_path.end, field.normalize_position(new_position))
        self.assertEqual(loop_count, Product(1, 0))

    def test_game_field_moves_on_torus_without_wrap(self):
        field = make_field()
        start = field.create_position(2, 3)
        movement = field.move_on_torus(start, 1, 0)
        new_position = movement.first_value
        torus_path = movement.second_value

        self.assertEqual(new_position, field.create_position(3, 3))
        self.assertEqual(torus_path.second_value, Product(0, 0))

    def test_game_field_calculates_shortest_corner_trajectory(self):
        field = make_field()
        start = field.create_position(0, 0)
        end = field.create_position(9, 4)
        trajectory = field.calculate_shortest_trajectory(start, end)
        torus_path = trajectory.first_value
        directions = trajectory.second_value

        self.assertEqual(torus_path.second_value, Product(-1, -1))
        self.assertEqual(
            [Direction.get_delta(direction) for direction in directions],
            [(-1, 0), (0, -1)],
        )

    def test_game_field_prefers_body_safe_turn_order(self):
        field = make_field()
        snake = Snake(
            Direction.right(),
            [
                field.create_position(0, 0),
                field.create_position(9, 0),
            ],
        )
        food = field.create_position(9, 4)
        trajectory = field.calculate_shortest_path_to_food(snake, food)
        torus_path = trajectory.first_value
        directions = trajectory.second_value

        self.assertEqual(torus_path.second_value, Product(-1, -1))
        self.assertEqual(
            [Direction.get_delta(direction) for direction in directions],
            [(0, -1), (-1, 0)],
        )

    def test_demo_mode_uses_pi_strategy_and_ignores_key_direction(self):
        field = make_field()
        snake = Snake(
            Direction.right(),
            [
                field.create_position(0, 0),
                field.create_position(9, 0),
            ],
        )
        state = GameState(snake, field.create_position(9, 4), 0, True)
        handler = InputHandler(state, field)
        next_state = handler.handle_input("KEY_DOWN", state)

        self.assertTrue(next_state.is_demo())
        self.assertEqual(
            Direction.get_delta(next_state.get_snake().get_direction()),
            (0, -1),
        )

    def test_input_handler_and_renderer_still_work_with_strengthened_model(self):
        field = GameField(4, 3)
        snake = Snake(
            Direction.right(),
            [
                field.create_position(1, 1),
                field.create_position(0, 1),
            ],
        )
        state = GameState(snake, field.create_position(3, 2), 0, False)
        handler = InputHandler(state, field)
        next_state = handler.handle_input("KEY_UP", state)
        renderer = Renderer(PlainTerm(), field)
        stream = io.StringIO()

        with redirect_stdout(stream):
            renderer.render(
                next_state,
                next_state.is_game_over(),
                next_state.is_paused(),
            )

        output = stream.getvalue()

        self.assertFalse(next_state.is_demo())
        self.assertEqual(
            Direction.get_delta(next_state.get_snake().get_direction()),
            (0, -1),
        )
        self.assertIn("+--------+", output)
        self.assertIn("|##@@    |", output)

    def test_move_snake_returns_torus_movement_evidence(self):
        field = make_field()
        snake = Snake(
            Direction.right(),
            [
                field.create_position(9, 1),
                field.create_position(8, 1),
            ],
        )
        result = move_snake(snake, Direction.right(), field, False)
        moved_snake = result.first_value
        movement = result.second_value
        torus_path = movement.second_value

        self.assertEqual(moved_snake.get_head(), field.create_position(0, 1))
        self.assertEqual(moved_snake.get_body()[1], field.create_position(9, 1))
        self.assertEqual(torus_path.second_value, Product(1, 0))

    def test_advance_game_state_moves_snake_one_tick(self):
        field = make_field()
        state = GameState(
            make_snake(field),
            field.create_position(8, 3),
            0,
            False,
        )
        tick = advance_game_state(state, field)
        next_state = tick.first_value

        self.assertEqual(next_state.get_snake().get_head(), field.create_position(3, 1))
        self.assertEqual(next_state.get_score(), 0)

    def test_advance_game_state_collects_food_and_scores(self):
        field = make_field()
        state = GameState(
            make_snake(field),
            field.create_position(3, 1),
            0,
            False,
        )
        tick = advance_game_state(state, field)
        next_state = tick.first_value

        self.assertEqual(next_state.get_snake().get_head(), field.create_position(3, 1))
        self.assertEqual(next_state.get_score(), 1)
        self.assertEqual(len(next_state.get_snake().get_body()), 3)
        self.assertFalse(
            next_state.get_snake().contains_position(next_state.get_food_position())
        )

    def test_food_search_uses_sum_for_full_field_case(self):
        field = GameField(2, 1)
        snake = Snake(
            Direction.right(),
            [
                field.create_position(0, 0),
                field.create_position(1, 0),
            ],
        )
        food_choice = find_next_food_position(field, snake)

        self.assertFalse(food_choice.is_left_active)
        self.assertEqual(food_choice.right_value, "NO_FREE_CELL")

    def test_food_search_avoids_next_head_position_when_possible(self):
        field = GameField(5, 1)
        snake = Snake(
            Direction.right(),
            [
                field.create_position(1, 0),
                field.create_position(0, 0),
                field.create_position(4, 0),
            ],
        )
        immediate_next_head = field.create_position(2, 0)
        food_choice = find_next_food_position_avoiding(
            field,
            snake,
            [immediate_next_head],
        )

        self.assertTrue(food_choice.is_left_active)
        self.assertEqual(food_choice.left_value, field.create_position(3, 0))

    def test_advance_game_state_does_not_place_food_before_head_after_eating(self):
        field = GameField(5, 1)
        snake = Snake(
            Direction.right(),
            [
                field.create_position(0, 0),
                field.create_position(4, 0),
            ],
        )
        state = GameState(
            snake,
            field.create_position(1, 0),
            0,
            True,
        )
        tick = advance_game_state(state, field)
        next_state = tick.first_value

        self.assertEqual(next_state.get_score(), 1)
        self.assertEqual(next_state.get_snake().get_head(), field.create_position(1, 0))
        self.assertNotEqual(next_state.get_food_position(), field.create_position(2, 0))
        self.assertEqual(next_state.get_food_position(), field.create_position(3, 0))

    def test_demo_strategy_and_tick_move_toward_food(self):
        field = make_field()
        snake = Snake(
            Direction.right(),
            [
                field.create_position(0, 0),
                field.create_position(9, 0),
            ],
        )
        state = GameState(snake, field.create_position(9, 4), 0, True)
        directed_state = apply_demo_strategy(state, field)
        tick = advance_game_state(directed_state, field)
        next_state = tick.first_value

        self.assertEqual(
            Direction.get_delta(directed_state.get_snake().get_direction()),
            (0, -1),
        )
        self.assertEqual(next_state.get_snake().get_head(), field.create_position(0, 4))

    def test_loop_key_toggles_demo_without_using_demo_strategy(self):
        field = make_field()
        state = GameState(
            make_snake(field),
            field.create_position(8, 3),
            0,
            False,
        )

        self.assertTrue(apply_loop_key(state, field, "d").is_demo())

    def test_initial_state_starts_in_demo_mode_when_requested(self):
        field = make_field()
        state = create_initial_state(field, True)

        self.assertTrue(state.is_demo())
        self.assertFalse(state.get_snake().contains_position(state.get_food_position()))


if __name__ == "__main__":
    unittest.main()
