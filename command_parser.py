import operator
import numpy as np
from typing import Tuple, List

VALID_CHARACTERS = {'d', '-', '+', '*', '/', '(', ')'}
RNG = np.random.default_rng()


def roll(dice: int, count: int = 1, start_from_zero: bool = False) -> np.array:
    if start_from_zero:
        return RNG.integers(0, dice, size=count)
    else:
        return RNG.integers(1, dice, size=count, endpoint=True)


def execute_dice_cmd(cmd: str) -> Tuple[int, List[int]]:
    program = parse_dice_command(cmd)
    return execute_expr(program)


def execute_expr(program) -> Tuple[int, List[int]]:
    stack = []
    rolls_made = []
    OPS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.floordiv
    }

    for op in program:
        if isinstance(op, int):
            stack.append(op)
        elif isinstance(op, tuple):
            dice_count, dice_limit = op
            rolls = roll(dice_limit, dice_count)
            rolls_made += rolls.tolist()
            stack.append(np.sum(rolls))
        else:
            right = stack.pop()
            left = stack.pop()
            stack.append(OPS[op](left, right))

    return stack[-1], rolls_made


def parse_dice_command(cmd: str):
    # CMD: EXPR
    # EXPR: ADD_EXPR
    # ADD_EXPR: MUL_EXPR [["+" | "-"] MUL_EXPR]*
    # MUL_EXPR: PRIM [["*" | "/"] PRIM]*
    # PRIM: NUMBER | ROLL_EXPR | "(" EXPR ")"
    # ROLL_EXPR: NUMBER "d" NUMBER
    # NUMBER: [0-9]+

    tokens = tokenize_cmd(cmd)
    prog = Parser().parse_cmd(tokens)
    return prog


class Parser:
    def __init__(self):
        self.tokens = None
        self.pos = 0
        self.parsed = None

    def parse_cmd(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.parsed = []

        self.add_expr()
        return self.parsed

    def add_expr(self):
        self.mul_expr()

        while self.look_ahead(0) in {"+", "-"}:
            op = self.look_ahead(0)
            self.advance()
            self.mul_expr()
            self.emit(op)

    def mul_expr(self):
        self.prim()

        while self.look_ahead(0) in {"*", "/"}:
            op = self.look_ahead(0)
            self.advance()
            self.prim()
            self.emit(op)

    def prim(self):
        tok = self.look_ahead(0)

        if tok == "(":
            self.advance()
            self.add_expr()
            self.consume(")")

        elif self.look_ahead(1) == "d":
            self.roll_expr()

        else:
            self.emit(self.number())

    def roll_expr(self):
        dices_num = self.number()
        self.consume("d")
        limit_num = self.number()

        self.emit((dices_num, limit_num))

    def number(self):
        num = int(self.look_ahead(0))
        self.advance()
        return num

    def look_ahead(self, n: int) -> str:
        if self.pos + n < len(self.tokens):
            return self.tokens[self.pos + n]
        else:
            return ""

    def emit(self, op):
        self.parsed.append(op)

    def advance(self):
        self.pos += 1

    def consume(self, expected: str):
        if self.look_ahead(0) != expected:
            raise Exception()

        self.advance()


def tokenize_cmd(cmd: str):
    tokens = []
    for raw_part in cmd.split():
        pos = 0

        while pos < len(raw_part):
            if raw_part[pos] == '\\':
                pos += 1

            elif raw_part[pos] in VALID_CHARACTERS:
                tokens.append(raw_part[pos])
                pos += 1

            else:
                num, pos = number(raw_part, pos)
                tokens.append(num)

    return tokens


def number(s: str, pos: int):
    start = pos

    while pos < len(s) and s[pos].isnumeric():
        pos += 1

    return s[start:pos], pos
