import re

# ==============================================================================
# 1. 抽象語法樹 (Abstract Syntax Tree)
# ==============================================================================

class Term:
    def free_vars(self) -> set:
        """回傳當前項中的自由變數集合"""
        raise NotImplementedError

    def substitute(self, var: str, replacement: "Term") -> "Term":
        """執行代換 [var ↦ replacement]，具備變數捕獲防護 (Alpha-conversion)"""
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class Var(Term):
    def __init__(self, name: str):
        self.name = name

    def free_vars(self) -> set:
        return {self.name}

    def substitute(self, var: str, replacement: Term) -> Term:
        return replacement if self.name == var else self

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name


class Abs(Term):
    def __init__(self, param: str, body: Term):
        self.param = param
        self.body = body

    def free_vars(self) -> set:
        return self.body.free_vars() - {self.param}

    def substitute(self, var: str, replacement: Term) -> Term:
        # 1. 若綁定變數與被替換目標相同，遮蔽外層，不需深入替換
        if self.param == var:
            return self

        # 2. 避免變數捕獲 (Variable Capture)：
        # 若參數名出現在 replacement 的自由變數中，需重新命名參數 (Alpha-conversion)
        if self.param in replacement.free_vars():
            new_param = self._fresh_var(self.body.free_vars() | replacement.free_vars() | {var})
            renamed_body = self.body.substitute(self.param, Var(new_param))
            return Abs(new_param, renamed_body.substitute(var, replacement))

        return Abs(self.param, self.body.substitute(var, replacement))

    def _fresh_var(self, used_vars: set) -> str:
        base = self.param.rstrip("0123456789'")
        i = 1
        while f"{base}{i}" in used_vars or f"{base}'{i}" in used_vars:
            i += 1
        return f"{base}{i}"

    def __str__(self) -> str:
        return f"(λ{self.param}. {self.body})"

    def __eq__(self, other):
        return isinstance(other, Abs) and self.param == other.param and self.body == other.body


class App(Term):
    def __init__(self, left: Term, right: Term):
        self.left = left
        self.right = right

    def free_vars(self) -> set:
        return self.left.free_vars() | self.right.free_vars()

    def substitute(self, var: str, replacement: Term) -> Term:
        return App(self.left.substitute(var, replacement), self.right.substitute(var, replacement))

    def __str__(self) -> str:
        return f"({self.left} {self.right})"

    def __eq__(self, other):
        return isinstance(other, App) and self.left == other.left and self.right == other.right


# ==============================================================================
# 2. 詞法分析 (Lexer) 與 語法分析 (Parser)
# ==============================================================================

def tokenize(code: str):
    token_spec = [
        ("LAMBDA", r"\\|λ"),
        ("DOT",    r"\."),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("IDENT",  r"[a-zA-Z_][a-zA-Z0-9_']*"),
        ("WS",     r"\s+"),
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
            raise SyntaxError(f"語法錯誤：預期為 {expected_kind}，卻收到 {kind} ('{val}')")
        self.pos += 1
        return val

    def parse(self) -> Term:
        term = self.parse_application()
        if self.peek()[0] != "EOF":
            raise SyntaxError(f"語法錯誤：未解析完全部的符號: '{self.peek()[1]}'")
        return term

    def parse_application(self) -> Term:
        # application ::= atom+ (左結合)
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
                raise SyntaxError("λ 後面必須有至少一個參數名稱")
            self.consume("DOT")
            body = self.parse_application()
            # 支援多參數展開，例如 \x y. x 轉為 \x. \y. x
            for p in reversed(params):
                body = Abs(p, body)
            return body
        elif kind == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_application()
            self.consume("RPAREN")
            return expr
        else:
            raise SyntaxError(f"未預期的符號: '{val}'")


def parse(code: str) -> Term:
    return Parser(tokenize(code)).parse()


# ==============================================================================
# 3. 歸約引擎 (Normal-Order Reduction)
# ==============================================================================

def reduce_step(term: Term):
    """
    執行單步正規順序歸約 (Normal-Order Step)。
    優先化簡最左、最外層的 Redex。
    回傳值: (新的 Term, 是否發生了歸約, 步驟描述字串)
    """
    # 規則 1: 最外層已是 (λx. M) N 形式 -> 直接進行 β-歸約
    if isinstance(term, App) and isinstance(term.left, Abs):
        param = term.left.param
        body = term.left.body
        arg = term.right
        new_term = body.substitute(param, arg)
        return new_term, True, f"β-歸約: ({term.left} {arg})  ==>  [{param} ↦ {arg}]"

    # 規則 2: 若是一般應用 App(L, R)，先嘗試對左側 L 歸約
    if isinstance(term, App):
        reduced_left, changed, note = reduce_step(term.left)
        if changed:
            return App(reduced_left, term.right), True, note
        # 左側已無法歸約，再嘗試對右側 R 歸約
        reduced_right, changed, note = reduce_step(term.right)
        if changed:
            return App(term.left, reduced_right), True, note

    # 規則 3: 若是抽象 Abs(x, M)，嘗試對內部 body 歸約
    if isinstance(term, Abs):
        reduced_body, changed, note = reduce_step(term.body)
        if changed:
            return Abs(term.param, reduced_body), True, note

    # 規則 4: 無法再歸約（已達 Normal Form）
    return term, False, ""


def evaluate(code: str, max_steps: int = 50) -> Term:
    """剖析並逐步印出計算歷程"""
    print("-" * 65)
    print(f"輸入表達式: {code}")
    print("-" * 65)

    term = parse(code)
    step = 0
    print(f"初始 AST: {term}\n")

    while step < max_steps:
        next_term, changed, note = reduce_step(term)
        if not changed:
            print("--> 已達正規形式 (Normal Form)！")
            print(f"最終結果: {term}\n")
            return term

        step += 1
        print(f"Step {step}:")
        print(f"  規則: {note}")
        print(f"  結果: {next_term}\n")
        term = next_term

    print(f"達到最大步數上限 ({max_steps})，可能存在發散循環 (Divergence)。\n")
    return term


# ==============================================================================
# 4. 巨集環境 (Macro Environment)
# ==============================================================================

class Environment:
    """管理有名稱的 Lambda 表達式"""
    def __init__(self):
        self.macros = {}

    def define(self, name: str, code: str):
        # 先將已有的定義展開進去，確保巨集可互相引用
        expanded = self.expand_string(code)
        self.macros[name] = parse(expanded)

    def expand_string(self, code: str) -> str:
        # 依名稱長度遞減替換，避免名稱前綴覆蓋問題
        sorted_names = sorted(self.macros.keys(), key=len, reverse=True)
        res = code
        for name in sorted_names:
            res = re.sub(rf"\b{name}\b", f"({str(self.macros[name])})", res)
        return res

    def run_test(self, title: str, expression: str, max_steps: int = 50):
        print(f"\n{'='*75}")
        print(f"測試項目: {title}")
        print(f"求值表達式: {expression}")
        print(f"{'='*75}")
        expanded_code = self.expand_string(expression)
        evaluate(expanded_code, max_steps=max_steps)


# ==============================================================================
# 5. 測試套件執行
# ==============================================================================

def main():
    env = Environment()

    # --- 定義布林邏輯 ---
    env.define("TRUE",     r"\x y. x")
    env.define("FALSE",    r"\x y. y")
    env.define("AND",      r"\p q. p q p")
    env.define("OR",       r"\p q. p p q")
    env.define("NOT",      r"\p. p FALSE TRUE")
    env.define("IF",       r"\p a b. p a b")

    # --- 定義邱奇數 (Church Numerals) ---
    env.define("ZERO",     r"\f x. x")
    env.define("ONE",      r"\f x. f x")
    env.define("TWO",      r"\f x. f (f x)")
    env.define("THREE",    r"\f x. f (f (f x))")

    # --- 算術運算 ---
    env.define("SUCC",     r"\n f x. f (n f x)")
    env.define("PLUS",     r"\m n f x. m f (n f x)")
    env.define("MULT",     r"\m n f. m (n f)")

    # --- 資料結構：有序對 (Pair) ---
    env.define("PAIR",     r"\x y f. f x y")
    env.define("FIRST",    r"\p. p TRUE")
    env.define("REST",     r"\p. p FALSE")

    # --- 經典組合子 ---
    env.define("K",        r"\x y. x")
    env.define("OMEGA",    r"(\x. x x) (\x. x x)")

    # 執行測試 1: 布林運算 AND TRUE FALSE -> 應得 FALSE (\x y. y)
    env.run_test(
        title="1. 布林邏輯：AND TRUE FALSE",
        expression="AND TRUE FALSE"
    )

    # 執行測試 2: 邱奇數加法 PLUS ONE TWO -> 應得 THREE (\f x. f (f (f x)))
    env.run_test(
        title="2. 邱奇數加法：1 + 2 = 3",
        expression="PLUS ONE TWO"
    )

    # 執行測試 3: 有序對解構 FIRST (PAIR ONE TWO) -> 應得 ONE
    env.run_test(
        title="3. 有序對解構：FIRST (PAIR ONE TWO)",
        expression="FIRST (PAIR ONE TWO)"
    )

    # 執行測試 4: 變數捕獲防護 (Alpha-Conversion 驗證)
    # (\x y. x y) y -> 若直接替換會變成 \y. y y（y 被內部捕獲）；正確應重命名為 \y1. y y1
    env.run_test(
        title="4. 變數捕獲防護 (Alpha-conversion)",
        expression=r"(\x y. x y) y"
    )

    # 執行測試 5: 正規順序求值優勢 (遇到無限發散項仍可終止)
    # K ONE OMEGA -> 正規順序會優先把 OMEGA 整個丟棄，不需計算 OMEGA 即得 ONE
    env.run_test(
        title="5. 正規順序避免發散：K ONE OMEGA",
        expression="K ONE OMEGA",
        max_steps=10
    )


if __name__ == "__main__":
    main()
    