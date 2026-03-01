import re

FORMAT_RX = re.compile(r"^[a-h][0-9]{2}$")


class ksort:
    items: list[str | None] = []

    def __init__(self):
        self.items = [None] * 800

    @staticmethod
    def is_valid_string(s: str) -> bool:
        return bool(FORMAT_RX.fullmatch(s))

    def index(self, s: str) -> int:
        if not self.is_valid_string(s):
            return -1

        # we need to make a shift "to zero"
        # so our indexes will fit into 0...799
        letter = ord(s[0]) - ord("a")
        number = int(s[1:])

        # every code-string has 100 combinations
        return letter * 100 + number

    def add(self, s: str) -> bool:
        idx = self.index(s)
        if idx < 0:
            return False
        else:
            self.items[idx] = s
            return True
