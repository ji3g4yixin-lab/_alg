import re

# ==========================================
# 1. AST 定義
# ==========================================
class Term:
    def free_vars(self):
        raise NotImplementedError

    def substitute(self, var, replacement):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class Var(Term):
    def __init__(self, name: str):
        self.name = name

    def free_vars(self):
        return {self.name}

    def substitute(self, var: str, replacement: Term):
        return replacement if self.name == var else self

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name


class Abs(Term):
    def __init__(self, param: str, body: Term):
        self.param = param
        self.body = body

    def free_vars(self):
        return self.body.free_vars() - {self.param}

    def substitute(self, var: str, replacement: Term):
        # 1. 若綁定變數與替換目標相同，不需深入替換
        if self.param == var:
            return self

        # 2. 避免變數捕獲（Variable Capture）：若當前參數出現在 replacement 的自由變數中，需做 alpha-轉換
        if self.param in replacement.free_vars():
            new_param = self._fresh_var(self.body.free_vars() | replacement.free_vars() | {var})
            renamed_body = self.body.substitute(self.param, Var(new_param))
            return Abs(new_param, renamed_body.substitute(var, replacement))

        return Abs(self.param, self.body.substitute(var, replacement))

    def _fresh_var(self, used_vars):
        base = self.param.rstrip("0123456789'")
        i = 1
        while f"{base}'{i}" in used_vars or f"{base}{i}" in used_vars:
            i += 1
        return f"{base}{i}"

    def __str__(self):
        return f"(λ{self.param}. {self.body})"

    def __eq__(self, other):
        return isinstance(other, Abs) and self.param == other.param and self.body == other.body


class App(Term):
    def __init__(self, left: Term, right: Term):
        self.left = left
        self.right = right

    def free_vars(self):
        return self.left.free_vars() | self.right.free_vars()

    def substitute(self, var: str, replacement: Term):
        return App(self.left.substitute(var, replacement), self.right.substitute(var, replacement))

    def __str__(self):
        l_str = str(self.left)
        r_str = str(self.right)
        return f"({l_str} {r_str})"

    def __eq__(self, other):
        return isinstance(other, App) and self.left == other.left and self.right == other.right


# ==========================================
# 2. Tokenizer & Parser
# ==========================================
def tokenize(code: str):
    token_spec = [
        ("LAMBDA", r"\\|λ"),
        ("DOT", r"\."),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_']*"),
        ("WS", r"\s+"),
    ]
    regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
    tokens = []
    for match in re.finditer(regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind != "WS":
            tokens.append((kind, value))
    tokens.append(("EOF", ""))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_kind=None):
        kind, val = self.peek()
        if expected_kind and kind != expected_kind:
            raise SyntaxError(f"預期為 {expected_kind}，卻收到 {kind} ('{val}')")
        self.pos += 1
        return val

    def parse(self) -> Term:
        term = self.parse_expression()
        if self.peek()[0] != "EOF":
            raise SyntaxError(f"語法錯誤，未解析完畢: {self.peek()[1]}")
        return term

    def parse_expression(self) -> Term:
        # expression ::= application
        return self.parse_application()

    def parse_application(self) -> Term:
        # application ::= atom+
        terms = [self.parse_atom()]
        while self.peek()[0] in ("IDENT", "LAMBDA", "LPAREN"):
            terms.append(self.parse_atom())

        res = terms[0]
        for t in terms[1:]:
            res = App(res, t)
        return res

    def parse_atom(self) -> Term:
        kind, val = self.peek()
        if kind == "IDENT":
            self.consume("IDENT")
            return Var(val)
        elif kind == "LAMBDA":
            self.consume("LAMBDA")
            params = []
            while self.peek()[0] == "IDENT":
                params.append(self.consume("IDENT"))
            if not params:
                raise SyntaxError("λ 後面必須有至少一個參數")
            self.consume("DOT")
            body = self.parse_expression()
            for p in reversed(params):
                body = Abs(p, body)
            return body
        elif kind == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr
        else:
            raise SyntaxError(f"無法解析的符號: {val}")


def parse(code: str) -> Term:
    return Parser(tokenize(code)).parse()


# ==========================================
# 3. 歸約引擎（Normal-Order Reduction）
# ==========================================
def reduce_step(term: Term):
    """
    執行單步正規順序歸約 (Normal-Order Step)。
    優先化簡最左、最外的 Redex。
    回傳: (新的 Term, 是否發生了歸約, 步驟描述)
    """
    # 規則 1: 最外層已是 (λx. M) N 形式 -> 直接 β-歸約
    if isinstance(term, App) and isinstance(term.left, Abs):
        param = term.left.param
        body = term.left.body
        arg = term.right
        new_term = body.substitute(param, arg)
        return new_term, True, f"β-reduction: ({term.left} {arg})  ==>  [{param} ↦ {arg}]"

    # 規則 2: 若是一般 App(L, R)，先嘗試對左側 L 歸約
    if isinstance(term, App):
        reduced_left, changed, note = reduce_step(term.left)
        if changed:
            return App(reduced_left, term.right), True, note
        # 左側無法歸約，再嘗試對右側 R 歸約
        reduced_right, changed, note = reduce_step(term.right)
        if changed:
            return App(term.left, reduced_right), True, note

    # 規則 3: 若是 Abs(x, M)，嘗試對內部 body 歸約
    if isinstance(term, Abs):
        reduced_body, changed, note = reduce_step(term.body)
        if changed:
            return Abs(term.param, reduced_body), True, note

    # 無法再歸約（已達 Normal Form）
    return term, False, ""


def evaluate(code: str, max_steps: int = 50):
    """解析並完整輸出計算歷程"""
    print(f"{'='*60}")
    print(f"輸入表達式: {code}")
    print(f"{'='*60}")

    term = parse(code)
    step = 0
    print(f"初始 AST: {term}\n")

    while step < max_steps:
        next_term, changed, note = reduce_step(term)
        if not changed:
            print(f"--> 已達到正規形式 (Normal Form)！")
            print(f"最終結果: {term}\n")
            return term

        step += 1
        print(f"Step {step}:")
        print(f"  規則: {note}")
        print(f"  結果: {next_term}\n")
        term = next_term

    print(f"達到最大步數上限 ({max_steps})，可能存在無限循環或未收斂項。")
    return term


if __name__ == "__main__":
    # 範例 1：布林運算 (NOT TRUE)
    # TRUE = \x y. x
    # NOT = \b. b (\x y. y) (\x y. x)
    evaluate(r"(\b. b (\x y. y) (\x y. x)) (\x y. x)")

    # 範例 2：防止變數捕獲 (Alpha-conversion)
    # (\x y. x y) y -> 若不重新命名 y，會變成 \y. y y（造成捕獲）
    evaluate(r"(\x y. x y) y")

    # 範例 3：後繼函數 (SUCC 0 = 1)
    # 0 = \f x. x
    # SUCC = \n f x. f (n f x)
    evaluate(r"(\n f x. f (n f x)) (\f x. x)")