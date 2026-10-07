def sym_diff(expr, var="x"):
    """使用遞迴計算符號數學表示式 expr 對變數 var 的導函數。

    :param expr: 數學表示式（常數、變數或 tuple 結構）
    :param var: 微分目標變數（預設為 'x'）
    :return: 微分後的符號表示式 (tuple / 數值 / 字串)
    """
    # ---------------- 基準條件 (Base Cases) ----------------
    # 1. 常數微分為 0
    if isinstance(expr, (int, float)):
        return 0

    # 2. 單一變數微分：對自己微分為 1，對其他獨立變數微分為 0
    if isinstance(expr, str):
        return 1 if expr == var else 0

    # ---------------- 遞迴步驟 (Recursive Cases) ----------------
    op = expr[0]

    # 加法與減法規則: (u ± v)' = u' ± v'
    if op == "+":
        u, v = expr[1], expr[2]
        return ("+", sym_diff(u, var), sym_diff(v, var))

    if op == "-":
        if len(expr) == 2:  # 單元負號: (-u)' = -u'
            return ("-", sym_diff(expr[1], var))
        u, v = expr[1], expr[2]
        return ("-", sym_diff(u, var), sym_diff(v, var))

    # 乘法規則 (Product Rule): (u * v)' = u' * v + u * v'
    if op == "*":
        u, v = expr[1], expr[2]
        du = sym_diff(u, var)
        dv = sym_diff(v, var)
        return ("+", ("*", du, v), ("*", u, dv))

    # 除法規則 (Quotient Rule): (u / v)' = (u' * v - u * v') / (v ^ 2)
    if op == "/":
        u, v = expr[1], expr[2]
        du = sym_diff(u, var)
        dv = sym_diff(v, var)
        return ("/", ("-", ("*", du, v), ("*", u, dv)), ("^", v, 2))

    # 次方規則 (Power Rule + 連鎖律)
    if op == "^":
        u, v = expr[1], expr[2]
        du = sym_diff(u, var)
        # 若指數為常數 n: (u^n)' = n * u^(n-1) * u'
        if isinstance(v, (int, float)):
            return ("*", ("*", v, ("^", u, v - 1)), du)
        # 一般情況 (u^v)' = u^v * (v' * ln(u) + v * u' / u)
        dv = sym_diff(v, var)
        return (
            "*",
            ("^", u, v),
            ("+", ("*", dv, ("ln", u)), ("/", ("*", v, du), u)),
        )

    # 三角與超越函數（結合連鎖律 Chain Rule: f(u)' = f'(u) * u'）
    if op == "sin":
        u = expr[1]
        return ("*", ("cos", u), sym_diff(u, var))

    if op == "cos":
        u = expr[1]
        return ("*", ("-", ("sin", u)), sym_diff(u, var))

    if op == "exp":
        u = expr[1]
        return ("*", ("exp", u), sym_diff(u, var))

    if op == "ln":
        u = expr[1]
        return ("/", sym_diff(u, var), u)

    raise ValueError(f"未知的運算子: {op}")


# ================= 輔助模組：簡化與列印 =================


def simplify(expr):
    """遞迴簡化符號表示式（消除 0, 1 與常數折疊）"""
    if isinstance(expr, (int, float, str)):
        return expr

    op = expr[0]
    if len(expr) == 2:
        arg = simplify(expr[1])
        if op == "-" and isinstance(arg, (int, float)):
            return -arg
        return (op, arg)

    u = simplify(expr[1])
    v = simplify(expr[2])

    # 1. 常數折疊 (Constant Folding)
    if isinstance(u, (int, float)) and isinstance(v, (int, float)):
        if op == "+":
            return u + v
        if op == "-":
            return u - v
        if op == "*":
            return u * v
        if op == "/" and v != 0:
            return u / v if u % v != 0 else u // v
        if op == "^":
            return u**v

    # 2. 算術恆等式化簡
    if op == "+":
        if u == 0:
            return v
        if v == 0:
            return u
    elif op == "-":
        if v == 0:
            return u
        if u == 0:
            return ("-", v)
    elif op == "*":
        if u == 0 or v == 0:
            return 0
        if u == 1:
            return v
        if v == 1:
            return u
    elif op == "/":
        if u == 0:
            return 0
        if v == 1:
            return u
    elif op == "^":
        if v == 0:
            return 1
        if v == 1:
            return u

    return (op, u, v)


def to_str(expr):
    """將語法樹轉換為易讀的數學字串"""
    if isinstance(expr, (int, float, str)):
        return str(expr)
    op = expr[0]
    if len(expr) == 2:
        return f"{op}({to_str(expr[1])})"
    return f"({to_str(expr[1])} {op} {to_str(expr[2])})"


# ================= 測試範例 =================
if __name__ == "__main__":
    # 範例 1: f(x) = x^3 + 5*x
    # 表示法: ('+', ('^', 'x', 3), ('*', 5, 'x'))
    f1 = ("+", ("^", "x", 3), ("*", 5, "x"))
    df1_raw = sym_diff(f1, "x")
    df1_simplified = simplify(df1_raw)
    print("【範例 1】")
    print(f"原式   : {to_str(f1)}")
    print(f"導函數 : {to_str(df1_simplified)}\n")

    # 範例 2: f(x) = sin(x^2)
    # 表示法: ('sin', ('^', 'x', 2))
    f2 = ("sin", ("^", "x", 2))
    df2_raw = sym_diff(f2, "x")
    df2_simplified = simplify(df2_raw)
    print("【範例 2】")
    print(f"原式   : {to_str(f2)}")
    print(f"導函數 : {to_str(df2_simplified)}\n")

    # 範例 3: f(x) = exp(x) / x
    # 表示法: ('/', ('exp', 'x'), 'x')
    f3 = ("/", ("exp", "x"), "x")
    df3_raw = sym_diff(f3, "x")
    df3_simplified = simplify(df3_raw)
    print("【範例 3】")
    print(f"原式   : {to_str(f3)}")
    print(f"導函數 : {to_str(df3_simplified)}")