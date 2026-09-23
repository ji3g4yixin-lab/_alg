#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sat.py — 以「系統性列舉真值表」解決 SAT 布林滿足問題 (Brute-force SAT Solver)

方法：對 n 個變數，依二進位順序 00..0 → 11..1 系統性列舉全部 2^n 種賦值，
逐列求值，若公式為真則為一組解 (model)。時間複雜度 O(2^n * m)，
其中 m 為公式求值成本；空間複雜度 O(n)。

支援兩種輸入：
  1. 布林運算式字串 (一般 SAT)：例如 "(A and B) or (not A and C)"
     支援運算子：and/&/&& , or/|/|| , not/~/! , ^ (xor), -> (蘊含), <-> (等值)
  2. CNF 子句集 (串列格式)：例如 [[1, -2], [-1, 2]] (DIMACS 整數編碼)
     或 [["A", "-B"], ["-A", "B"]]

主要函數：
  solve(expr)            -> 回傳所有滿足賦值 (list[dict])
  is_satisfiable(expr)   -> 是否可滿足 (bool)
  find_one(expr)         -> 回傳一組解或 None
  solve_cnf(clauses, ...) -> 解 CNF
  print_truth_table(expr) -> 印出完整真值表

CLI 範例：
  python sat.py "(A or B) and (not A or C)"
  python sat.py "(A -> B) and A" --table
  python sat.py --cnf "[[1,-2],[-1,2,3]]" --vars "A B C"
  python sat.py --demo
"""

import argparse
import itertools
import re
import sys


# ---------- 1. 運算式前處理 ----------

_KEYWORDS = {"and", "or", "not", "True", "False", "xor"}

def extract_variables(expr: str) -> list:
    """從運算式中取出變數名稱 (排序後回傳，確保列舉順序固定)。"""
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)
    vars_ = sorted({t for t in tokens if t not in _KEYWORDS})
    return vars_


def normalize_expr(expr: str) -> str:
    """把各種寫法統一轉成 Python 可 eval 的布林運算式。

    支援：
      && -> and,  || -> or,  ! -> not (但 != 保留),
      & -> and,   | -> or,   ~ -> not,  ^ -> xor,
      A -> B  (蘊含, 等價於 (not A) or B),
      A <-> B (等值, 等價於 (A == B))
      True/False 大小寫皆可；TRUE/FALSE 轉成 True/False
    """
    s = expr.strip()

    # TRUE/FALSE 統一大小寫 (避免誤傷變數內含此子字串：只取代完整單字)
    s = re.sub(r"\bTRUE\b", "True", s, flags=re.IGNORECASE)
    s = re.sub(r"\bFALSE\b", "False", s, flags=re.IGNORECASE)
    # XOR 關鍵字轉成 ^ 以便後續處理
    s = re.sub(r"\bxor\b", "^", s, flags=re.IGNORECASE)

    # 先把 && || & | 轉成 and/or，以便後續遞迴能以單一寫法切分
    s = s.replace("&&", " and ").replace("||", " or ")
    s = s.replace("!=", "\x00NE\x00").replace("==", "\x00EQ\x00")
    s = s.replace("<=", "\x00LE\x00").replace(">=", "\x00GE\x00")
    s = s.replace("&", " and ").replace("|", " or ")
    s = s.replace("\x00NE\x00", "!=").replace("\x00EQ\x00", "==")
    s = s.replace("\x00LE\x00", "<=").replace("\x00GE\x00", ">=")

    # 改寫 -> / <-> (支援巢狀括號與 and/or/not 內任意位置出現)
    # 策略：A <-> B 轉成 ((A) __EQ__ (B))；A -> B 轉成 ((not (A)) or (B))
    s = _rewrite_arrows(s)

    # 剩餘符號轉 Python 關鍵字 (此時已無 -> / <->)
    # ~ 與 ! 轉 not (!= 已被保護，不受影響)
    s = s.replace("~", " not ")
    s = re.sub(r"!(?!=)", " not ", s)
    # ^ 轉成 != (布林 xor：True/False 相異即為真)
    s = re.sub(r"\^", " != ", s)
    # __EQ__ 還原為 Python 語法
    s = s.replace("__EQ__", "==")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _split_top_level(s: str, ops: tuple) -> list:
    """以頂層 (括號深度 0) 的運算子切分字串，回傳 [運算元, 運算子, 運算元, ...]。"""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(s):
        if s[i] == "(":
            depth += 1
            cur += s[i]
            i += 1
        elif s[i] == ")":
            depth -= 1
            cur += s[i]
            i += 1
        elif depth == 0:
            matched = None
            for op in sorted(ops, key=len, reverse=True):
                if s.startswith(op, i):
                    # -> 不可誤判 <-> 的前半；呼叫端保證已先處理 <->，此處只做保險
                    matched = op
                    break
            if matched:
                parts.append(cur.strip())
                parts.append(matched)
                cur = ""
                i += len(matched)
            else:
                cur += s[i]
                i += 1
        else:
            cur += s[i]
            i += 1
    parts.append(cur.strip())
    return parts


def _strip_outer_parens(s: str):
    """若整個字串被一對括號包住，回傳內層；否則回傳 None。"""
    s = s.strip()
    if len(s) < 2 or s[0] != "(" or s[-1] != ")":
        return None
    depth = 0
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and i != len(s) - 1:
                return None  # 首個 '(' 在結尾前就關閉，非整體包覆
    return s[1:-1]


def _split_top_level_word(s: str, word: str):
    """以頂層的單字運算子 (and/or) 切分，回傳運算元串列；無切分則回傳 [s]。"""
    parts, depth, cur, i = [], 0, "", 0
    wlen = len(word)
    while i < len(s):
        if s[i] == "(":
            depth += 1
            cur += s[i]
            i += 1
        elif s[i] == ")":
            depth -= 1
            cur += s[i]
            i += 1
        elif depth == 0 and s[i:i + wlen].lower() == word:
            before = s[i - 1] if i > 0 else " "
            after = s[i + wlen] if i + wlen < len(s) else " "
            if not (before.isalnum() or before == "_") and not (after.isalnum() or after == "_"):
                parts.append(cur)
                cur = ""
                i += wlen
                continue
            cur += s[i]
            i += 1
        else:
            cur += s[i]
            i += 1
    parts.append(cur)
    return parts


def _rewrite_arrows(s: str) -> str:
    """遞迴改寫任意深度的 <-> 與 ->。

    A <-> B  =>  ((A) __EQ__ (B))，之後 __EQ__ 還原為 ==
    A -> B   =>  ((not (A)) or (B))，直接展開為 Python 語法
    多個鏈式 (A -> B -> C) 視為右結合：A -> (B -> C)。
    透過遞迴深入 and/or/not/括號內層，確保巢狀如 "(A -> B) and C" 也能改寫。
    """
    s = s.strip()
    # 先處理 <-> (優先級最低)
    parts = _split_top_level(s, ("<->",))
    if len(parts) > 1:
        operands = [_rewrite_arrows(p) for p in parts[::2]]
        out = operands[0]
        for q in operands[1:]:
            out = f"(({out}) __EQ__ ({q}))"
        return out
    # 再處理 ->
    parts = _split_top_level(s, ("->", "=>"))
    if len(parts) > 1:
        operands = [_rewrite_arrows(p) for p in parts[::2]]
        # 右結合
        out = operands[-1]
        for p in reversed(operands[:-1]):
            out = f"((not ({p})) or ({out}))"
        return out
    # 深入 and / or 內層
    for word in ("and", "or"):
        parts = _split_top_level_word(s, word)
        if len(parts) > 1:
            return f" {word} ".join(f"({_rewrite_arrows(p)})" for p in parts)
    # 前綴 not
    m = re.match(r"(?i)^\s*not\s+(.*)$", s, re.DOTALL)
    if m:
        return f"not ({_rewrite_arrows(m.group(1))})"
    # 整體括號：剝掉一層後繼續深入
    inner = _strip_outer_parens(s)
    if inner is not None:
        return f"({_rewrite_arrows(inner)})"
    return s


def _safe_eval(py_expr: str, assignment: dict) -> bool:
    """以受限環境求值：只允許變數名與 and/or/not/True/False/==/!=/括號。"""
    allowed_names = set(assignment.keys()) | {"True", "False"}
    code = compile(py_expr, "<sat-expr>", "eval")
    # 阻擋屬性存取、函數呼叫等：只允許 Name / BoolOp / UnaryOp / Compare / Constant
    import ast as _ast
    tree = _ast.parse(py_expr, mode="eval")
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Call):
            raise ValueError("運算式不允許函數呼叫")
        if isinstance(node, _ast.Attribute):
            raise ValueError("運算式不允許屬性存取")
        if isinstance(node, _ast.Name) and node.id not in allowed_names | {"and", "or", "not"}:
            raise ValueError(f"未知變數或關鍵字: {node.id}")
    return bool(eval(code, {"__builtins__": {}}, assignment))  # noqa: S307 (輸入為本地公式)


# ---------- 2. 真值表系統性列舉 ----------

def iter_truth_table(expr: str, variables: list = None):
    """系統性列舉真值表：依二進位計數 00..0 → 11..1 逐列產生 (assignment, value)。

    Yields:
        (dict, bool): (變數賦值, 公式在此賦值下的真值)
    """
    variables = variables if variables is not None else extract_variables(expr)
    py_expr = normalize_expr(expr)
    n = len(variables)
    for bits in itertools.product([False, True], repeat=n):
        assignment = dict(zip(variables, bits))
        yield assignment, _safe_eval(py_expr, assignment)


def print_truth_table(expr: str, variables: list = None, file=sys.stdout):
    """印出完整真值表，並回傳 (variables, rows)，rows 為 [(assignment, value)]。"""
    variables = variables if variables is not None else extract_variables(expr)
    rows = list(iter_truth_table(expr, variables))
    # 表頭
    header = " | ".join(variables + ["F"])
    print(header, file=file)
    print("-" * len(header), file=file)
    for assignment, value in rows:
        line = " | ".join("1" if assignment[v] else "0" for v in variables)
        line += " | " + ("1" if value else "0")
        print(line, file=file)
    return variables, rows


# ---------- 3. SAT 求解 ----------

def solve(expr: str, variables: list = None) -> list:
    """回傳所有滿足賦值 (models)。空串列代表 UNSAT。"""
    return [a for a, v in iter_truth_table(expr, variables) if v]


def find_one(expr: str, variables: list = None):
    """回傳一組滿足賦值；若 UNSAT 回傳 None (找到即停，不必列舉完全部)。"""
    for assignment, value in iter_truth_table(expr, variables):
        if value:
            return assignment
    return None


def is_satisfiable(expr: str, variables: list = None) -> bool:
    """公式是否可滿足 (SAT)。"""
    return find_one(expr, variables) is not None


def is_valid(expr: str, variables: list = None) -> bool:
    """公式是否為恆真式 (tautology)：所有列皆為真。"""
    return all(v for _, v in iter_truth_table(expr, variables))


def count_models(expr: str, variables: list = None) -> int:
    """計算滿足賦值的個數 (#SAT)。"""
    return sum(1 for _, v in iter_truth_table(expr, variables) if v)


# ---------- 4. CNF 求解 (子句集版本) ----------

def eval_cnf(clauses: list, assignment: dict) -> bool:
    """求值 CNF：clauses 為子句的串列，每個子句為 literal 串列。

    literal 可以是：
      - 字串："A" 表肯定，" -A" / "!A" / "~A" / "¬A" 表否定
      - 元組 (var, is_neg)：如 ("A", True)
    空子句為 False (UNSAT 核心)；空子句集為 True。
    """
    for clause in clauses:
        sat_clause = False
        for lit in clause:
            var, neg = parse_literal(lit)
            val = assignment.get(var, False)
            if neg:
                val = not val
            if val:
                sat_clause = True
                break
        if not sat_clause:
            return False
    return True


def parse_literal(lit) -> tuple:
    """回傳 (var, is_neg)。"""
    if isinstance(lit, tuple) and len(lit) == 2:
        return lit[0], bool(lit[1])
    if isinstance(lit, str):
        s = lit.strip()
        for prefix in ("-", "!", "~", "¬", "not "):
            if s.startswith(prefix):
                return s[len(prefix):].strip(), True
        return s, False
    raise ValueError(f"無法解析 literal: {lit!r}")


def cnf_variables(clauses: list) -> list:
    """取出 CNF 中所有變數 (排序)。"""
    vars_ = set()
    for clause in clauses:
        for lit in clause:
            var, _ = parse_literal(lit)
            vars_.add(var)
    return sorted(vars_)


def solve_cnf(clauses: list, variables: list = None, find_all: bool = True):
    """以真值表列舉解 CNF。

    Args:
        clauses: 子句集，如 [["A", "-B"], ["-A", "B"]]
        variables: 變數順序；None 則自動推導
        find_all: True 回傳全部解；False 只找一組 (找到即停)

    Returns:
        list[dict]：滿足賦值串列 (UNSAT 時為 [])
    """
    variables = variables if variables is not None else cnf_variables(clauses)
    n = len(variables)
    models = []
    for bits in itertools.product([False, True], repeat=n):
        assignment = dict(zip(variables, bits))
        if eval_cnf(clauses, assignment):
            models.append(dict(assignment))
            if not find_all:
                break
    return models


def solve_cnf_int(clauses_int: list, var_names: list = None):
    """以 DIMACS 風格整數編碼解 CNF。

    Args:
        clauses_int: 如 [[1, -2], [-1, 2, 3]]，數字為變數編號 (1-based)，負號表否定
        var_names: 編號對應的變數名，如 ["A", "B", "C"]；None 則用 "x1", "x2", ...

    Returns:
        (models, var_names)：models 為賦值 dict 的串列
    """
    max_var = 0
    for clause in clauses_int:
        for lit in clause:
            max_var = max(max_var, abs(int(lit)))
    if var_names is None:
        var_names = [f"x{i}" for i in range(1, max_var + 1)]
    assert len(var_names) >= max_var, "var_names 數量不足"
    str_clauses = []
    for clause in clauses_int:
        c = []
        for lit in clause:
            lit = int(lit)
            name = var_names[abs(lit) - 1]
            c.append(f"-{name}" if lit < 0 else name)
        str_clauses.append(c)
    return solve_cnf(str_clauses, var_names[:max_var]), var_names[:max_var]


def load_dimacs(path: str):
    """讀取 DIMACS CNF 檔案，回傳 (clauses_int, n_vars)。"""
    clauses, cur = [], []
    n_vars = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                # p cnf <n_vars> <n_clauses>
                n_vars = int(line.split()[2])
                continue
            for tok in line.split():
                lit = int(tok)
                if lit == 0:
                    clauses.append(cur)
                    cur = []
                else:
                    cur.append(lit)
    return clauses, n_vars


# ---------- 5. CLI ----------

def fmt_assignment(a: dict) -> str:
    return "{" + ", ".join(f"{k}={'1' if v else '0'}" for k, v in a.items()) + "}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="以真值表列舉解 SAT 布林滿足問題")
    ap.add_argument("expr", nargs="?", default=None, help="布林運算式，如 \"(A or B) and (not A or C)\"")
    ap.add_argument("--table", action="store_true", help="印出完整真值表")
    ap.add_argument("--cnf", default=None, help="CNF 整數子句集，如 \"[[1,-2],[-1,2]]\"")
    ap.add_argument("--vars", default=None, help="變數名，空白分隔，如 \"A B C\"")
    ap.add_argument("--dimacs", default=None, help="DIMACS CNF 檔案路徑")
    ap.add_argument("--demo", action="store_true", help="執行內建示範")
    args = ap.parse_args(argv)

    if args.demo or (args.expr is None and args.cnf is None and args.dimacs is None):
        demo()
        return 0

    if args.dimacs:
        clauses_int, n_vars = load_dimacs(args.dimacs)
        var_names = args.vars.split() if args.vars else None
        models, names = solve_cnf_int(clauses_int, var_names)
        print(f"變數: {names} (共 {len(names)} 個, 搜尋空間 2^{len(names)} = {2 ** len(names)})")
        print(f"子句數: {len(clauses_int)}")
        if models:
            print(f"SAT: 找到 {len(models)} 組解，例如 {fmt_assignment(models[0])}")
        else:
            print("UNSAT: 無滿足賦值")
        return 0

    if args.cnf:
        import ast as _ast
        clauses_int = _ast.literal_eval(args.cnf)
        var_names = args.vars.split() if args.vars else None
        models, names = solve_cnf_int(clauses_int, var_names)
        print(f"變數: {names} (共 {len(names)} 個, 搜尋空間 2^{len(names)} = {2 ** len(names)})")
        print(f"子句: {clauses_int}")
        if models:
            print(f"SAT: 共 {len(models)} 組解")
            for m in models:
                print("  " + fmt_assignment(m))
        else:
            print("UNSAT: 無滿足賦值")
        return 0

    expr = args.expr
    variables = args.vars.split() if args.vars else extract_variables(expr)
    if args.table:
        print_truth_table(expr, variables)
        print()
    models = solve(expr, variables)
    n = len(variables)
    print(f"公式: {expr}")
    print(f"變數: {variables} (共 {n} 個, 搜尋空間 2^{n} = {2 ** n})")
    if models:
        print(f"SAT: 共 {len(models)} 組解")
        for m in models:
            print("  " + fmt_assignment(m))
    else:
        print("UNSAT: 無滿足賦值")
    return 0


def demo():
    cases = [
        ("(A or B) and ((not A) or C)", "一般 SAT：應為 SAT"),
        ("A and (not A)", "UNSAT 經典例"),
        ("(A -> B) and A and (not B)", "蘊含 + Modus Ponens 反例 (UNSAT)"),
        ("(A <-> B) and (B <-> C) and (A and (not C))", "等值鏈矛盾 (UNSAT)"),
    ]
    for expr, note in cases:
        print(f"=== {note} ===")
        print(f"公式: {expr}")
        variables, _ = print_truth_table(expr)
        models = solve(expr, variables)
        if models:
            print(f"=> SAT，共 {len(models)} 組解，第一組: {fmt_assignment(models[0])}\n")
        else:
            print("=> UNSAT，無解\n")
    print("=== CNF 整數編碼範例 ===")
    clauses_int = [[1, -2], [-1, 2], [1, 2]]
    models, names = solve_cnf_int(clauses_int, ["A", "B"])
    print(f"子句: {clauses_int} (即 (A∨¬B) ∧ (¬A∨B) ∧ (A∨B))")
    print(f"=> {'SAT: ' + str([fmt_assignment(m) for m in models]) if models else 'UNSAT'}")


if __name__ == "__main__":
    sys.exit(main())
