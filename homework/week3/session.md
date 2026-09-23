# sat.py 真值表解 SAT 布林滿足問題

**Session ID:** ses_f33e94b65ffep1SKsasSYMLqLy
**Created:** 9/23/2026, 10:27:15 AM
**Updated:** 9/23/2026, 11:19:49 AM

---

## User

請寫一個sat.py 可以系統性的列舉真值表，解決 SAT 布林滿足問題

---

## Assistant

_Thinking:_



真值表列舉解 SAT — 正在建立求解器。

**Tool: read**

**Input:**
```json
{
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3"
}
```

Read directory /Users/xueshengji4/Desktop/emma/_alg/homework/week3, entries 1-1
sat.py

---

## Assistant

**Tool: read**

**Input:**
```json
{
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py"
}
```

Read file /Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py, lines 1-1
1: print('hello')

---

## Assistant

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "path": "/Users/xueshengji4/Desktop/emma/_alg"
}
```

Read directory /Users/xueshengji4/Desktop/emma/_alg, entries 1-6
.git/
homework/
.DS_Store
.gitignore
LICENSE
README.md

---

## Assistant

**Tool: read**

**Input:**
```json
{
  "path": "/Users/xueshengji4/Desktop/emma/_alg/README.md"
}
```

Read file /Users/xueshengji4/Desktop/emma/_alg/README.md, lines 1-11
1: # 課程：演算法 --  學生作業與專案
2: 
3: 欄位 | 內容
4: -----|--------
5: 學期 | 115 學年上學期
6: 教師 | [陳鍾誠](https://www.nqu.edu.tw/educsie/index.php?act=blog&code=list&ids=4)
7: 學校 | [金門大學資訊工程系](https://www.nqu.edu.tw/educsie/index.php)
8: 學生 | xxx
9: 學號 | xx
10: 
11: 

**Tool: glob**

**Input:**
```json
{
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework",
  "pattern": "**/*"
}
```

/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py
/Users/xueshengji4/Desktop/emma/_alg/homework/README.md

---

## Assistant

**Tool: read**

**Input:**
```json
{
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/README.md"
}
```

Read file /Users/xueshengji4/Desktop/emma/_alg/homework/README.md, 0 lines

---

## Assistant

_Thinking:_



規格已確認 — 現在撰寫完整列舉版 SAT 求解器。

**Tool: write**

**Input:**
```json
{
  "content": "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\"\"\"\nsat.py — 以「系統性列舉真值表」解決 SAT 布林滿足問題 (Brute-force SAT Solver)\n\n方法：對 n 個變數，依二進位順序 00..0 → 11..1 系統性列舉全部 2^n 種賦值，\n逐列求值，若公式為真則為一組解 (model)。時間複雜度 O(2^n * m)，\n其中 m 為公式求值成本；空間複雜度 O(n)。\n\n支援兩種輸入：\n  1. 布林運算式字串 (一般 SAT)：例如 \"(A and B) or (not A and C)\"\n     支援運算子：and/&/&& , or/|/|| , not/~/! , ^ (xor), -> (蘊含), <-> (等值)\n  2. CNF 子句集 (串列格式)：例如 [[1, -2], [-1, 2]] (DIMACS 整數編碼)\n     或 [[\"A\", \"-B\"], [\"-A\", \"B\"]]\n\n主要函數：\n  solve(expr)            -> 回傳所有滿足賦值 (list[dict])\n  is_satisfiable(expr)   -> 是否可滿足 (bool)\n  find_one(expr)         -> 回傳一組解或 None\n  solve_cnf(clauses, ...) -> 解 CNF\n  print_truth_table(expr) -> 印出完整真值表\n\nCLI 範例：\n  python sat.py \"(A or B) and (not A or C)\"\n  python sat.py \"(A -> B) and A\" --table\n  python sat.py --cnf \"[[1,-2],[-1,2,3]]\" --vars \"A B C\"\n  python sat.py --demo\n\"\"\"\n\nimport argparse\nimport itertools\nimport re\nimport sys\n\n\n# ---------- 1. 運算式前處理 ----------\n\n_KEYWORDS = {\"and\", \"or\", \"not\", \"True\", \"False\", \"xor\"}\n\ndef extract_variables(expr: str) -> list:\n    \"\"\"從運算式中取出變數名稱 (排序後回傳，確保列舉順序固定)。\"\"\"\n    tokens = re.findall(r\"[A-Za-z_][A-Za-z0-9_]*\", expr)\n    vars_ = sorted({t for t in tokens if t not in _KEYWORDS})\n    return vars_\n\n\ndef normalize_expr(expr: str) -> str:\n    \"\"\"把各種寫法統一轉成 Python 可 eval 的布林運算式。\n\n    支援：\n      && -> and,  || -> or,  ! -> not (但 != 保留),\n      & -> and,   | -> or,   ~ -> not,  ^ -> xor,\n      A -> B  (蘊含, 等價於 (not A) or B),\n      A <-> B (等值, 等價於 (A == B))\n      True/False 大小寫皆可；TRUE/FALSE 轉成 True/False\n    \"\"\"\n    s = expr.strip()\n\n    # TRUE/FALSE 統一大小寫 (避免誤傷變數內含此子字串：只取代完整單字)\n    s = re.sub(r\"\\bTRUE\\b\", \"True\", s, flags=re.IGNORECASE)\n    s = re.sub(r\"\\bFALSE\\b\", \"False\", s, flags=re.IGNORECASE)\n    # XOR 關鍵字轉成 ^ 以便後續處理\n    s = re.sub(r\"\\bxor\\b\", \"^\", s, flags=re.IGNORECASE)\n\n    # 先處理 <-> (等值)，再處理 -> (蘊含)，避免互相干擾。\n    # 用佔位符保護已轉換的片段，最後再還原為 Python 語法。\n    # 策略：把 \"P <-> Q\" 轉成 \"__EQ__(P,Q)\"，把 \"P -> Q\" 轉成 \"__IMP__(P,Q)\"，\n    # 其中 P, Q 為「不含頂層 -> / <-> 的運算元」。為簡化，只支援以\n    # 變數/常數/括號運算式作為運算元的鏈式寫法，括號會被正確配對。\n    s = _rewrite_arrows(s)\n\n    # 剩餘符號轉 Python 關鍵字 (此時已無 -> / <->)\n    s = s.replace(\"&&\", \" and \").replace(\"||\", \" or \")\n    # 單個 & | 轉 and/or，但保留 != == <= >= 不被破壞：\n    # Python 布林式不會出現位元運算，所以可直接取代單符號\n    # 先保護 != / == / <= / >=\n    s = s.replace(\"!=\", \"\\x00NE\\x00\").replace(\"==\", \"\\x00EQ\\x00\")\n    s = s.replace(\"<=\", \"\\x00LE\\x00\").replace(\">=\", \"\\x00GE\\x00\")\n    s = s.replace(\"&\", \" and \").replace(\"|\", \" or \")\n    s = s.replace(\"\\x00NE\\x00\", \"!=\").replace(\"\\x00EQ\\x00\", \"==\")\n    s = s.replace(\"\\x00LE\\x00\", \"<=\").replace(\"\\x00GE\\x00\", \">=\")\n    # ~ 與 ! 轉 not (!= 已被保護，不受影響)\n    s = s.replace(\"~\", \" not \")\n    s = re.sub(r\"!(?!=)\", \" not \", s)\n    # ^ 轉成 != (布林 xor：True/False 相異即為真)\n    s = re.sub(r\"\\^\", \" != \", s)\n    # __IMP__ / __EQ__ 還原為 Python 語法\n    s = s.replace(\"__IMP__\", \" or not \")  # 呼叫端已轉成 (not P) or Q 形式？見 _rewrite_arrows\n    s = s.replace(\"__EQ__\", \"==\")\n    s = re.sub(r\"\\s+\", \" \", s).strip()\n    return s\n\n\ndef _split_top_level(s: str, ops: tuple) -> list:\n    \"\"\"以頂層 (括號深度 0) 的運算子切分字串，回傳 [運算元, 運算子, 運算元, ...]。\"\"\"\n    parts, depth, cur, i = [], 0, \"\", 0\n    while i < len(s):\n        if s[i] == \"(\":\n            depth += 1\n            cur += s[i]\n            i += 1\n        elif s[i] == \")\":\n            depth -= 1\n            cur += s[i]\n            i += 1\n        elif depth == 0:\n            matched = None\n            for op in sorted(ops, key=len, reverse=True):\n                if s.startswith(op, i):\n                    # -> 不可誤判 <-> 的前半；呼叫端保證已先處理 <->，此處只做保險\n                    matched = op\n                    break\n            if matched:\n                parts.append(cur.strip())\n                parts.append(matched)\n                cur = \"\"\n                i += len(matched)\n            else:\n                cur += s[i]\n                i += 1\n        else:\n            cur += s[i]\n            i += 1\n    parts.append(cur.strip())\n    return parts\n\n\ndef _rewrite_arrows(s: str) -> str:\n    \"\"\"遞迴改寫頂層的 <-> 與 ->。\n\n    A <-> B  =>  ((A) __EQ__ (B))，之後 __EQ__ 還原為 ==\n    A -> B   =>  ((not (A)) or (B))，直接展開為 Python 語法\n    多個鏈式 (A -> B -> C) 視為右結合：A -> (B -> C)。\n    \"\"\"\n    # 先處理 <-> (優先級最低)\n    parts = _split_top_level(s, (\"<->\",))\n    if len(parts) > 1:\n        operands = [_rewrite_arrows(p) for p in parts[::2]]\n        out = operands[0]\n        for q in operands[1:]:\n            out = f\"(({out}) __EQ__ ({q}))\"\n        return out\n    # 再處理 ->\n    parts = _split_top_level(s, (\"->\", \"=>\"))\n    if len(parts) > 1:\n        ops = parts[1::2]\n        operands = [_rewrite_arrows(p) for p in parts[::2]]\n        # 右結合\n        out = operands[-1]\n        for p in reversed(operands[:-1]):\n            out = f\"((not ({p})) or ({out}))\"\n        return out\n    return s\n\n\ndef _safe_eval(py_expr: str, assignment: dict) -> bool:\n    \"\"\"以受限環境求值：只允許變數名與 and/or/not/True/False/==/!=/括號。\"\"\"\n    allowed_names = set(assignment.keys()) | {\"True\", \"False\"}\n    code = compile(py_expr, \"<sat-expr>\", \"eval\")\n    # 阻擋屬性存取、函數呼叫等：只允許 Name / BoolOp / UnaryOp / Compare / Constant\n    import ast as _ast\n    tree = _ast.parse(py_expr, mode=\"eval\")\n    for node in _ast.walk(tree):\n        if isinstance(node, _ast.Call):\n            raise ValueError(\"運算式不允許函數呼叫\")\n        if isinstance(node, _ast.Attribute):\n            raise ValueError(\"運算式不允許屬性存取\")\n        if isinstance(node, _ast.Name) and node.id not in allowed_names | {\"and\", \"or\", \"not\"}:\n            raise ValueError(f\"未知變數或關鍵字: {node.id}\")\n    return bool(eval(code, {\"__builtins__\": {}}, assignment))  # noqa: S307 (輸入為本地公式)\n\n\n# ---------- 2. 真值表系統性列舉 ----------\n\ndef iter_truth_table(expr: str, variables: list = None):\n    \"\"\"系統性列舉真值表：依二進位計數 00..0 → 11..1 逐列產生 (assignment, value)。\n\n    Yields:\n        (dict, bool): (變數賦值, 公式在此賦值下的真值)\n    \"\"\"\n    variables = variables if variables is not None else extract_variables(expr)\n    py_expr = normalize_expr(expr)\n    n = len(variables)\n    for bits in itertools.product([False, True], repeat=n):\n        assignment = dict(zip(variables, bits))\n        yield assignment, _safe_eval(py_expr, assignment)\n\n\ndef print_truth_table(expr: str, variables: list = None, file=sys.stdout):\n    \"\"\"印出完整真值表，並回傳 (variables, rows)，rows 為 [(assignment, value)]。\"\"\"\n    variables = variables if variables is not None else extract_variables(expr)\n    rows = list(iter_truth_table(expr, variables))\n    # 表頭\n    header = \" | \".join(variables + [\"F\"])\n    print(header, file=file)\n    print(\"-\" * len(header), file=file)\n    for assignment, value in rows:\n        line = \" | \".join(\"1\" if assignment[v] else \"0\" for v in variables)\n        line += \" | \" + (\"1\" if value else \"0\")\n        print(line, file=file)\n    return variables, rows\n\n\n# ---------- 3. SAT 求解 ----------\n\ndef solve(expr: str, variables: list = None) -> list:\n    \"\"\"回傳所有滿足賦值 (models)。空串列代表 UNSAT。\"\"\"\n    return [a for a, v in iter_truth_table(expr, variables) if v]\n\n\ndef find_one(expr: str, variables: list = None):\n    \"\"\"回傳一組滿足賦值；若 UNSAT 回傳 None (找到即停，不必列舉完全部)。\"\"\"\n    for assignment, value in iter_truth_table(expr, variables):\n        if value:\n            return assignment\n    return None\n\n\ndef is_satisfiable(expr: str, variables: list = None) -> bool:\n    \"\"\"公式是否可滿足 (SAT)。\"\"\"\n    return find_one(expr, variables) is not None\n\n\ndef is_valid(expr: str, variables: list = None) -> bool:\n    \"\"\"公式是否為恆真式 (tautology)：所有列皆為真。\"\"\"\n    return all(v for _, v in iter_truth_table(expr, variables))\n\n\ndef count_models(expr: str, variables: list = None) -> int:\n    \"\"\"計算滿足賦值的個數 (#SAT)。\"\"\"\n    return sum(1 for _, v in iter_truth_table(expr, variables) if v)\n\n\n# ---------- 4. CNF 求解 (子句集版本) ----------\n\ndef eval_cnf(clauses: list, assignment: dict) -> bool:\n    \"\"\"求值 CNF：clauses 為子句的串列，每個子句為 literal 串列。\n\n    literal 可以是：\n      - 字串：\"A\" 表肯定，\" -A\" / \"!A\" / \"~A\" / \"¬A\" 表否定\n      - 元組 (var, is_neg)：如 (\"A\", True)\n    空子句為 False (UNSAT 核心)；空子句集為 True。\n    \"\"\"\n    for clause in clauses:\n        sat_clause = False\n        for lit in clause:\n            var, neg = parse_literal(lit)\n            val = assignment.get(var, False)\n            if neg:\n                val = not val\n            if val:\n                sat_clause = True\n                break\n        if not sat_clause:\n            return False\n    return True\n\n\ndef parse_literal(lit) -> tuple:\n    \"\"\"回傳 (var, is_neg)。\"\"\"\n    if isinstance(lit, tuple) and len(lit) == 2:\n        return lit[0], bool(lit[1])\n    if isinstance(lit, str):\n        s = lit.strip()\n        for prefix in (\"-\", \"!\", \"~\", \"¬\", \"not \"):\n            if s.startswith(prefix):\n                return s[len(prefix):].strip(), True\n        return s, False\n    raise ValueError(f\"無法解析 literal: {lit!r}\")\n\n\ndef cnf_variables(clauses: list) -> list:\n    \"\"\"取出 CNF 中所有變數 (排序)。\"\"\"\n    vars_ = set()\n    for clause in clauses:\n        for lit in clause:\n            var, _ = parse_literal(lit)\n            vars_.add(var)\n    return sorted(vars_)\n\n\ndef solve_cnf(clauses: list, variables: list = None, find_all: bool = True):\n    \"\"\"以真值表列舉解 CNF。\n\n    Args:\n        clauses: 子句集，如 [[\"A\", \"-B\"], [\"-A\", \"B\"]]\n        variables: 變數順序；None 則自動推導\n        find_all: True 回傳全部解；False 只找一組 (找到即停)\n\n    Returns:\n        list[dict]：滿足賦值串列 (UNSAT 時為 [])\n    \"\"\"\n    variables = variables if variables is not None else cnf_variables(clauses)\n    n = len(variables)\n    models = []\n    for bits in itertools.product([False, True], repeat=n):\n        assignment = dict(zip(variables, bits))\n        if eval_cnf(clauses, assignment):\n            models.append(dict(assignment))\n            if not find_all:\n                break\n    return models\n\n\ndef solve_cnf_int(clauses_int: list, var_names: list = None):\n    \"\"\"以 DIMACS 風格整數編碼解 CNF。\n\n    Args:\n        clauses_int: 如 [[1, -2], [-1, 2, 3]]，數字為變數編號 (1-based)，負號表否定\n        var_names: 編號對應的變數名，如 [\"A\", \"B\", \"C\"]；None 則用 \"x1\", \"x2\", ...\n\n    Returns:\n        (models, var_names)：models 為賦值 dict 的串列\n    \"\"\"\n    max_var = 0\n    for clause in clauses_int:\n        for lit in clause:\n            max_var = max(max_var, abs(int(lit)))\n    if var_names is None:\n        var_names = [f\"x{i}\" for i in range(1, max_var + 1)]\n    assert len(var_names) >= max_var, \"var_names 數量不足\"\n    str_clauses = []\n    for clause in clauses_int:\n        c = []\n        for lit in clause:\n            lit = int(lit)\n            name = var_names[abs(lit) - 1]\n            c.append(f\"-{name}\" if lit < 0 else name)\n        str_clauses.append(c)\n    return solve_cnf(str_clauses, var_names[:max_var]), var_names[:max_var]\n\n\ndef load_dimacs(path: str):\n    \"\"\"讀取 DIMACS CNF 檔案，回傳 (clauses_int, n_vars)。\"\"\"\n    clauses, cur = [], []\n    n_vars = 0\n    with open(path, encoding=\"utf-8\") as f:\n        for line in f:\n            line = line.strip()\n            if not line or line.startswith(\"c\"):\n                continue\n            if line.startswith(\"p\"):\n                # p cnf <n_vars> <n_clauses>\n                n_vars = int(line.split()[2])\n                continue\n            for tok in line.split():\n                lit = int(tok)\n                if lit == 0:\n                    clauses.append(cur)\n                    cur = []\n                else:\n                    cur.append(lit)\n    return clauses, n_vars\n\n\n# ---------- 5. CLI ----------\n\ndef fmt_assignment(a: dict) -> str:\n    return \"{\" + \", \".join(f\"{k}={'1' if v else '0'}\" for k, v in a.items()) + \"}\"\n\n\ndef main(argv=None) -> int:\n    ap = argparse.ArgumentParser(description=\"以真值表列舉解 SAT 布林滿足問題\")\n    ap.add_argument(\"expr\", nargs=\"?\", default=None, help=\"布林運算式，如 \\\"(A or B) and (not A or C)\\\"\")\n    ap.add_argument(\"--table\", action=\"store_true\", help=\"印出完整真值表\")\n    ap.add_argument(\"--cnf\", default=None, help=\"CNF 整數子句集，如 \\\"[[1,-2],[-1,2]]\\\"\")\n    ap.add_argument(\"--vars\", default=None, help=\"變數名，空白分隔，如 \\\"A B C\\\"\")\n    ap.add_argument(\"--dimacs\", default=None, help=\"DIMACS CNF 檔案路徑\")\n    ap.add_argument(\"--demo\", action=\"store_true\", help=\"執行內建示範\")\n    args = ap.parse_args(argv)\n\n    if args.demo or (args.expr is None and args.cnf is None and args.dimacs is None):\n        demo()\n        return 0\n\n    if args.dimacs:\n        clauses_int, n_vars = load_dimacs(args.dimacs)\n        var_names = args.vars.split() if args.vars else None\n        models, names = solve_cnf_int(clauses_int, var_names)\n        print(f\"變數: {names} (共 {len(names)} 個, 搜尋空間 2^{len(names)} = {2 ** len(names)})\")\n        print(f\"子句數: {len(clauses_int)}\")\n        if models:\n            print(f\"SAT: 找到 {len(models)} 組解，例如 {fmt_assignment(models[0])}\")\n        else:\n            print(\"UNSAT: 無滿足賦值\")\n        return 0\n\n    if args.cnf:\n        import ast as _ast\n        clauses_int = _ast.literal_eval(args.cnf)\n        var_names = args.vars.split() if args.vars else None\n        models, names = solve_cnf_int(clauses_int, var_names)\n        print(f\"變數: {names} (共 {len(names)} 個, 搜尋空間 2^{len(names)} = {2 ** len(names)})\")\n        print(f\"子句: {clauses_int}\")\n        if models:\n            print(f\"SAT: 共 {len(models)} 組解\")\n            for m in models:\n                print(\"  \" + fmt_assignment(m))\n        else:\n            print(\"UNSAT: 無滿足賦值\")\n        return 0\n\n    expr = args.expr\n    variables = args.vars.split() if args.vars else extract_variables(expr)\n    if args.table:\n        print_truth_table(expr, variables)\n        print()\n    models = solve(expr, variables)\n    n = len(variables)\n    print(f\"公式: {expr}\")\n    print(f\"變數: {variables} (共 {n} 個, 搜尋空間 2^{n} = {2 ** n})\")\n    if models:\n        print(f\"SAT: 共 {len(models)} 組解\")\n        for m in models:\n            print(\"  \" + fmt_assignment(m))\n    else:\n        print(\"UNSAT: 無滿足賦值\")\n    return 0\n\n\ndef demo():\n    cases = [\n        (\"(A or B) and ((not A) or C)\", \"一般 SAT：應為 SAT\"),\n        (\"A and (not A)\", \"UNSAT 經典例\"),\n        (\"(A -> B) and A and (not B)\", \"蘊含 + Modus Ponens 反例 (UNSAT)\"),\n        (\"(A <-> B) and (B <-> C) and (A and (not C))\", \"等值鏈矛盾 (UNSAT)\"),\n    ]\n    for expr, note in cases:\n        print(f\"=== {note} ===\")\n        print(f\"公式: {expr}\")\n        variables, _ = print_truth_table(expr)\n        models = solve(expr, variables)\n        if models:\n            print(f\"=> SAT，共 {len(models)} 組解，第一組: {fmt_assignment(models[0])}\\n\")\n        else:\n            print(\"=> UNSAT，無解\\n\")\n    print(\"=== CNF 整數編碼範例 ===\")\n    clauses_int = [[1, -2], [-1, 2], [1, 2]]\n    models, names = solve_cnf_int(clauses_int, [\"A\", \"B\"])\n    print(f\"子句: {clauses_int} (即 (A∨¬B) ∧ (¬A∨B) ∧ (A∨B))\")\n    print(f\"=> {'SAT: ' + str([fmt_assignment(m) for m in models]) if models else 'UNSAT'}\")\n\n\nif __name__ == \"__main__\":\n    sys.exit(main())\n",
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py"
}
```

Wrote file successfully: sat.py

---

## Assistant

_Thinking:_



**Tool: shell**

**Input:**
```json
{
  "command": "python3 sat.py --demo && echo \"----\" && python3 sat.py \"(A or B) and ((not A) or C)\" --table && echo \"----\" && python3 sat.py --cnf \"[[1,-2],[-1,2]]\" --vars \"A B\" && echo \"----\" && python3 -c \"import sat; print(sat.is_satisfiable('A and (not A)')); print(sat.is_satisfiable('(A or B) and (not A)')); print(sat.find_one('(A or B) and (not A)')); print(sat.count_models('A or B')); print(sat.solve_cnf([['A','-B'],['-A','B']])); print(sat.is_valid('A or (not A)'))\"",
  "workdir": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3"
}
```

=== 一般 SAT：應為 SAT ===
公式: (A or B) and ((not A) or C)
A | B | C | F
-------------
0 | 0 | 0 | 0
0 | 0 | 1 | 0
0 | 1 | 0 | 1
0 | 1 | 1 | 1
1 | 0 | 0 | 0
1 | 0 | 1 | 1
1 | 1 | 0 | 0
1 | 1 | 1 | 1
=> SAT，共 4 組解，第一組: {A=0, B=1, C=0}

=== UNSAT 經典例 ===
公式: A and (not A)
A | F
-----
0 | 0
1 | 0
=> UNSAT，無解

=== 蘊含 + Modus Ponens 反例 (UNSAT) ===
公式: (A -> B) and A and (not B)
Traceback (most recent call last):
  File "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py", line 445, in <module>
    sys.exit(main())
  File "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py", line 373, in main
    demo()
  File "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py", line 431, in demo
    variables, _ = print_truth_table(expr)
  File "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py", line 192, in print_truth_table
    rows = list(iter_truth_table(expr, variables))
  File "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py", line 186, in iter_truth_table
    yield assignment, _safe_eval(py_expr, assignment)
  File "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py", line 159, in _safe_eval
    code = compile(py_expr, "<sat-expr>", "eval")
  File "<sat-expr>", line 1
    (A -> B) and A and (not B)
       ^
SyntaxError: invalid syntax

Command exited with code 1.

---

## Assistant

_Thinking:_



發現蘊含式巢狀括號的解析問題 — 正在修復。

**Tool: read**

**Input:**
```json
{
  "limit": 120,
  "offset": 50,
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py"
}
```

Read file /Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py, lines 50-169
50:     支援：
51:       && -> and,  || -> or,  ! -> not (但 != 保留),
52:       & -> and,   | -> or,   ~ -> not,  ^ -> xor,
53:       A -> B  (蘊含, 等價於 (not A) or B),
54:       A <-> B (等值, 等價於 (A == B))
55:       True/False 大小寫皆可；TRUE/FALSE 轉成 True/False
56:     """
57:     s = expr.strip()
58: 
59:     # TRUE/FALSE 統一大小寫 (避免誤傷變數內含此子字串：只取代完整單字)
60:     s = re.sub(r"\bTRUE\b", "True", s, flags=re.IGNORECASE)
61:     s = re.sub(r"\bFALSE\b", "False", s, flags=re.IGNORECASE)
62:     # XOR 關鍵字轉成 ^ 以便後續處理
63:     s = re.sub(r"\bxor\b", "^", s, flags=re.IGNORECASE)
64: 
65:     # 先處理 <-> (等值)，再處理 -> (蘊含)，避免互相干擾。
66:     # 用佔位符保護已轉換的片段，最後再還原為 Python 語法。
67:     # 策略：把 "P <-> Q" 轉成 "__EQ__(P,Q)"，把 "P -> Q" 轉成 "__IMP__(P,Q)"，
68:     # 其中 P, Q 為「不含頂層 -> / <-> 的運算元」。為簡化，只支援以
69:     # 變數/常數/括號運算式作為運算元的鏈式寫法，括號會被正確配對。
70:     s = _rewrite_arrows(s)
71: 
72:     # 剩餘符號轉 Python 關鍵字 (此時已無 -> / <->)
73:     s = s.replace("&&", " and ").replace("||", " or ")
74:     # 單個 & | 轉 and/or，但保留 != == <= >= 不被破壞：
75:     # Python 布林式不會出現位元運算，所以可直接取代單符號
76:     # 先保護 != / == / <= / >=
77:     s = s.replace("!=", "\x00NE\x00").replace("==", "\x00EQ\x00")
78:     s = s.replace("<=", "\x00LE\x00").replace(">=", "\x00GE\x00")
79:     s = s.replace("&", " and ").replace("|", " or ")
80:     s = s.replace("\x00NE\x00", "!=").replace("\x00EQ\x00", "==")
81:     s = s.replace("\x00LE\x00", "<=").replace("\x00GE\x00", ">=")
82:     # ~ 與 ! 轉 not (!= 已被保護，不受影響)
83:     s = s.replace("~", " not ")
84:     s = re.sub(r"!(?!=)", " not ", s)
85:     # ^ 轉成 != (布林 xor：True/False 相異即為真)
86:     s = re.sub(r"\^", " != ", s)
87:     # __IMP__ / __EQ__ 還原為 Python 語法
88:     s = s.replace("__IMP__", " or not ")  # 呼叫端已轉成 (not P) or Q 形式？見 _rewrite_arrows
89:     s = s.replace("__EQ__", "==")
90:     s = re.sub(r"\s+", " ", s).strip()
91:     return s
92: 
93: 
94: def _split_top_level(s: str, ops: tuple) -> list:
95:     """以頂層 (括號深度 0) 的運算子切分字串，回傳 [運算元, 運算子, 運算元, ...]。"""
96:     parts, depth, cur, i = [], 0, "", 0
97:     while i < len(s):
98:         if s[i] == "(":
99:             depth += 1
100:             cur += s[i]
101:             i += 1
102:         elif s[i] == ")":
103:             depth -= 1
104:             cur += s[i]
105:             i += 1
106:         elif depth == 0:
107:             matched = None
108:             for op in sorted(ops, key=len, reverse=True):
109:                 if s.startswith(op, i):
110:                     # -> 不可誤判 <-> 的前半；呼叫端保證已先處理 <->，此處只做保險
111:                     matched = op
112:                     break
113:             if matched:
114:                 parts.append(cur.strip())
115:                 parts.append(matched)
116:                 cur = ""
117:                 i += len(matched)
118:             else:
119:                 cur += s[i]
120:                 i += 1
121:         else:
122:             cur += s[i]
123:             i += 1
124:     parts.append(cur.strip())
125:     return parts
126: 
127: 
128: def _rewrite_arrows(s: str) -> str:
129:     """遞迴改寫頂層的 <-> 與 ->。
130: 
131:     A <-> B  =>  ((A) __EQ__ (B))，之後 __EQ__ 還原為 ==
132:     A -> B   =>  ((not (A)) or (B))，直接展開為 Python 語法
133:     多個鏈式 (A -> B -> C) 視為右結合：A -> (B -> C)。
134:     """
135:     # 先處理 <-> (優先級最低)
136:     parts = _split_top_level(s, ("<->",))
137:     if len(parts) > 1:
138:         operands = [_rewrite_arrows(p) for p in parts[::2]]
139:         out = operands[0]
140:         for q in operands[1:]:
141:             out = f"(({out}) __EQ__ ({q}))"
142:         return out
143:     # 再處理 ->
144:     parts = _split_top_level(s, ("->", "=>"))
145:     if len(parts) > 1:
146:         ops = parts[1::2]
147:         operands = [_rewrite_arrows(p) for p in parts[::2]]
148:         # 右結合
149:         out = operands[-1]
150:         for p in reversed(operands[:-1]):
151:             out = f"((not ({p})) or ({out}))"
152:         return out
153:     return s
154: 
155: 
156: def _safe_eval(py_expr: str, assignment: dict) -> bool:
157:     """以受限環境求值：只允許變數名與 and/or/not/True/False/==/!=/括號。"""
158:     allowed_names = set(assignment.keys()) | {"True", "False"}
159:     code = compile(py_expr, "<sat-expr>", "eval")
160:     # 阻擋屬性存取、函數呼叫等：只允許 Name / BoolOp / UnaryOp / Compare / Constant
161:     import ast as _ast
162:     tree = _ast.parse(py_expr, mode="eval")
163:     for node in _ast.walk(tree):
164:         if isinstance(node, _ast.Call):
165:             raise ValueError("運算式不允許函數呼叫")
166:         if isinstance(node, _ast.Attribute):
167:             raise ValueError("運算式不允許屬性存取")
168:         if isinstance(node, _ast.Name) and node.id not in allowed_names | {"and", "or", "not"}:
169:             raise ValueError(f"未知變數或關鍵字: {node.id}")
[Output truncated. Continue reading with offset: 170]

---

## Assistant

**Tool: edit**

**Input:**
```json
{
  "newString": "    # 先把 && || & | 轉成 and/or，以便後續遞迴能以單一寫法切分\n    s = s.replace(\"&&\", \" and \").replace(\"||\", \" or \")\n    s = s.replace(\"!=\", \"\\x00NE\\x00\").replace(\"==\", \"\\x00EQ\\x00\")\n    s = s.replace(\"<=\", \"\\x00LE\\x00\").replace(\">=\", \"\\x00GE\\x00\")\n    s = s.replace(\"&\", \" and \").replace(\"|\", \" or \")\n    s = s.replace(\"\\x00NE\\x00\", \"!=\").replace(\"\\x00EQ\\x00\", \"==\")\n    s = s.replace(\"\\x00LE\\x00\", \"<=\").replace(\"\\x00GE\\x00\", \">=\")\n\n    # 改寫 -> / <-> (支援巢狀括號與 and/or/not 內任意位置出現)\n    # 策略：A <-> B 轉成 ((A) __EQ__ (B))；A -> B 轉成 ((not (A)) or (B))\n    s = _rewrite_arrows(s)\n\n    # 剩餘符號轉 Python 關鍵字 (此時已無 -> / <->)\n    # ~ 與 ! 轉 not (!= 已被保護，不受影響)\n    s = s.replace(\"~\", \" not \")\n    s = re.sub(r\"!(?!=)\", \" not \", s)\n    # ^ 轉成 != (布林 xor：True/False 相異即為真)\n    s = re.sub(r\"\\^\", \" != \", s)\n    # __EQ__ 還原為 Python 語法\n    s = s.replace(\"__EQ__\", \"==\")\n    s = re.sub(r\"\\s+\", \" \", s).strip()\n    return s",
  "oldString": "    # 先處理 <-> (等值)，再處理 -> (蘊含)，避免互相干擾。\n    # 用佔位符保護已轉換的片段，最後再還原為 Python 語法。\n    # 策略：把 \"P <-> Q\" 轉成 \"__EQ__(P,Q)\"，把 \"P -> Q\" 轉成 \"__IMP__(P,Q)\"，\n    # 其中 P, Q 為「不含頂層 -> / <-> 的運算元」。為簡化，只支援以\n    # 變數/常數/括號運算式作為運算元的鏈式寫法，括號會被正確配對。\n    s = _rewrite_arrows(s)\n\n    # 剩餘符號轉 Python 關鍵字 (此時已無 -> / <->)\n    s = s.replace(\"&&\", \" and \").replace(\"||\", \" or \")\n    # 單個 & | 轉 and/or，但保留 != == <= >= 不被破壞：\n    # Python 布林式不會出現位元運算，所以可直接取代單符號\n    # 先保護 != / == / <= / >=\n    s = s.replace(\"!=\", \"\\x00NE\\x00\").replace(\"==\", \"\\x00EQ\\x00\")\n    s = s.replace(\"<=\", \"\\x00LE\\x00\").replace(\">=\", \"\\x00GE\\x00\")\n    s = s.replace(\"&\", \" and \").replace(\"|\", \" or \")\n    s = s.replace(\"\\x00NE\\x00\", \"!=\").replace(\"\\x00EQ\\x00\", \"==\")\n    s = s.replace(\"\\x00LE\\x00\", \"<=\").replace(\"\\x00GE\\x00\", \">=\")\n    # ~ 與 ! 轉 not (!= 已被保護，不受影響)\n    s = s.replace(\"~\", \" not \")\n    s = re.sub(r\"!(?!=)\", \" not \", s)\n    # ^ 轉成 != (布林 xor：True/False 相異即為真)\n    s = re.sub(r\"\\^\", \" != \", s)\n    # __IMP__ / __EQ__ 還原為 Python 語法\n    s = s.replace(\"__IMP__\", \" or not \")  # 呼叫端已轉成 (not P) or Q 形式？見 _rewrite_arrows\n    s = s.replace(\"__EQ__\", \"==\")\n    s = re.sub(r\"\\s+\", \" \", s).strip()\n    return s",
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py"
}
```

Edited sat.py (1 replacement)

---

## Assistant

**Tool: edit**

**Input:**
```json
{
  "newString": "def _strip_outer_parens(s: str):\n    \"\"\"若整個字串被一對括號包住，回傳內層；否則回傳 None。\"\"\"\n    s = s.strip()\n    if len(s) < 2 or s[0] != \"(\" or s[-1] != \")\":\n        return None\n    depth = 0\n    for i, ch in enumerate(s):\n        if ch == \"(\":\n            depth += 1\n        elif ch == \")\":\n            depth -= 1\n            if depth == 0 and i != len(s) - 1:\n                return None  # 首個 '(' 在結尾前就關閉，非整體包覆\n    return s[1:-1]\n\n\ndef _split_top_level_word(s: str, word: str):\n    \"\"\"以頂層的單字運算子 (and/or) 切分，回傳運算元串列；無切分則回傳 [s]。\"\"\"\n    parts, depth, cur, i = [], 0, \"\", 0\n    wlen = len(word)\n    while i < len(s):\n        if s[i] == \"(\":\n            depth += 1\n            cur += s[i]\n            i += 1\n        elif s[i] == \")\":\n            depth -= 1\n            cur += s[i]\n            i += 1\n        elif depth == 0 and s[i:i + wlen].lower() == word:\n            before = s[i - 1] if i > 0 else \" \"\n            after = s[i + wlen] if i + wlen < len(s) else \" \"\n            if not (before.isalnum() or before == \"_\") and not (after.isalnum() or after == \"_\"):\n                parts.append(cur)\n                cur = \"\"\n                i += wlen\n                continue\n            cur += s[i]\n            i += 1\n        else:\n            cur += s[i]\n            i += 1\n    parts.append(cur)\n    return parts\n\n\ndef _rewrite_arrows(s: str) -> str:\n    \"\"\"遞迴改寫任意深度的 <-> 與 ->。\n\n    A <-> B  =>  ((A) __EQ__ (B))，之後 __EQ__ 還原為 ==\n    A -> B   =>  ((not (A)) or (B))，直接展開為 Python 語法\n    多個鏈式 (A -> B -> C) 視為右結合：A -> (B -> C)。\n    透過遞迴深入 and/or/not/括號內層，確保巢狀如 \"(A -> B) and C\" 也能改寫。\n    \"\"\"\n    s = s.strip()\n    # 先處理 <-> (優先級最低)\n    parts = _split_top_level(s, (\"<->\",))\n    if len(parts) > 1:\n        operands = [_rewrite_arrows(p) for p in parts[::2]]\n        out = operands[0]\n        for q in operands[1:]:\n            out = f\"(({out}) __EQ__ ({q}))\"\n        return out\n    # 再處理 ->\n    parts = _split_top_level(s, (\"->\", \"=>\"))\n    if len(parts) > 1:\n        operands = [_rewrite_arrows(p) for p in parts[::2]]\n        # 右結合\n        out = operands[-1]\n        for p in reversed(operands[:-1]):\n            out = f\"((not ({p})) or ({out}))\"\n        return out\n    # 深入 and / or 內層\n    for word in (\"and\", \"or\"):\n        parts = _split_top_level_word(s, word)\n        if len(parts) > 1:\n            return f\" {word} \".join(f\"({_rewrite_arrows(p)})\" for p in parts)\n    # 前綴 not\n    m = re.match(r\"(?i)^\\s*not\\s+(.*)$\", s, re.DOTALL)\n    if m:\n        return f\"not ({_rewrite_arrows(m.group(1))})\"\n    # 整體括號：剝掉一層後繼續深入\n    inner = _strip_outer_parens(s)\n    if inner is not None:\n        return f\"({_rewrite_arrows(inner)})\"\n    return s",
  "oldString": "def _rewrite_arrows(s: str) -> str:\n    \"\"\"遞迴改寫頂層的 <-> 與 ->。\n\n    A <-> B  =>  ((A) __EQ__ (B))，之後 __EQ__ 還原為 ==\n    A -> B   =>  ((not (A)) or (B))，直接展開為 Python 語法\n    多個鏈式 (A -> B -> C) 視為右結合：A -> (B -> C)。\n    \"\"\"\n    # 先處理 <-> (優先級最低)\n    parts = _split_top_level(s, (\"<->\",))\n    if len(parts) > 1:\n        operands = [_rewrite_arrows(p) for p in parts[::2]]\n        out = operands[0]\n        for q in operands[1:]:\n            out = f\"(({out}) __EQ__ ({q}))\"\n        return out\n    # 再處理 ->\n    parts = _split_top_level(s, (\"->\", \"=>\"))\n    if len(parts) > 1:\n        ops = parts[1::2]\n        operands = [_rewrite_arrows(p) for p in parts[::2]]\n        # 右結合\n        out = operands[-1]\n        for p in reversed(operands[:-1]):\n            out = f\"((not ({p})) or ({out}))\"\n        return out\n    return s",
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py"
}
```

Edited sat.py (1 replacement)

---

## Assistant

**Tool: shell**

**Input:**
```json
{
  "command": "python3 sat.py --demo && echo \"==== OK ====\" && python3 sat.py \"(A or B) and ((not A) or C)\" --table && echo \"----\" && python3 sat.py --cnf \"[[1,-2],[-1,2]]\" --vars \"A B\" && echo \"----\" && python3 -c \"import sat; print(sat.is_satisfiable('A and (not A)')); print(sat.is_satisfiable('(A or B) and (not A)')); print(sat.find_one('(A or B) and (not A)')); print(sat.count_models('A or B')); print(sat.solve_cnf([['A','-B'],['-A','B']])); print(sat.is_valid('A or (not A)')); print(sat.normalize_expr('(A -> B) and A and (not B)')); print(sat.normalize_expr('(A <-> B) and B'))\"",
  "workdir": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3"
}
```

=== 一般 SAT：應為 SAT ===
公式: (A or B) and ((not A) or C)
A | B | C | F
-------------
0 | 0 | 0 | 0
0 | 0 | 1 | 0
0 | 1 | 0 | 1
0 | 1 | 1 | 1
1 | 0 | 0 | 0
1 | 0 | 1 | 1
1 | 1 | 0 | 0
1 | 1 | 1 | 1
=> SAT，共 4 組解，第一組: {A=0, B=1, C=0}

=== UNSAT 經典例 ===
公式: A and (not A)
A | F
-----
0 | 0
1 | 0
=> UNSAT，無解

=== 蘊含 + Modus Ponens 反例 (UNSAT) ===
公式: (A -> B) and A and (not B)
A | B | F
---------
0 | 0 | 0
0 | 1 | 0
1 | 0 | 0
1 | 1 | 0
=> UNSAT，無解

=== 等值鏈矛盾 (UNSAT) ===
公式: (A <-> B) and (B <-> C) and (A and (not C))
A | B | C | F
-------------
0 | 0 | 0 | 0
0 | 0 | 1 | 0
0 | 1 | 0 | 0
0 | 1 | 1 | 0
1 | 0 | 0 | 0
1 | 0 | 1 | 0
1 | 1 | 0 | 0
1 | 1 | 1 | 0
=> UNSAT，無解

=== CNF 整數編碼範例 ===
子句: [[1, -2], [-1, 2], [1, 2]] (即 (A∨¬B) ∧ (¬A∨B) ∧ (A∨B))
=> SAT: ['{A=1, B=1}']
==== OK ====
A | B | C | F
-------------
0 | 0 | 0 | 0
0 | 0 | 1 | 0
0 | 1 | 0 | 1
0 | 1 | 1 | 1
1 | 0 | 0 | 0
1 | 0 | 1 | 1
1 | 1 | 0 | 0
1 | 1 | 1 | 1

公式: (A or B) and ((not A) or C)
變數: ['A', 'B', 'C'] (共 3 個, 搜尋空間 2^3 = 8)
SAT: 共 4 組解
  {A=0, B=1, C=0}
  {A=0, B=1, C=1}
  {A=1, B=0, C=1}
  {A=1, B=1, C=1}
----
變數: ['A', 'B'] (共 2 個, 搜尋空間 2^2 = 4)
子句: [[1, -2], [-1, 2]]
SAT: 共 2 組解
  {A=0, B=0}
  {A=1, B=1}
----
False
True
{'A': False, 'B': True}
3
[{'A': False, 'B': False}, {'A': True, 'B': True}]
True
((((not (A)) or (B)))) and (A) and ((not (B)))
((((A) == (B)))) and (B)

Command exited with code 0.

---

## Assistant

_Thinking:_



**Tool: shell**

**Input:**
```json
{
  "command": "python3 -c \"\nimport sat\ntests = [\n  ('A & B', {'A':True,'B':True}, True),\n  ('A & B', {'A':True,'B':False}, False),\n  ('A | B', {'A':False,'B':False}, False),\n  ('~A', {'A':False}, True),\n  ('!A', {'A':False}, True),\n  ('A ^ B', {'A':True,'B':False}, True),\n  ('A ^ B', {'A':True,'B':True}, False),\n  ('A -> B', {'A':True,'B':False}, False),\n  ('A -> B', {'A':False,'B':False}, True),\n  ('A <-> B', {'A':True,'B':True}, True),\n  ('A <-> B', {'A':True,'B':False}, False),\n]\nfrom sat import normalize_expr, _safe_eval\nfor expr, asg, exp in tests:\n    got = _safe_eval(normalize_expr(expr), asg)\n    assert got==exp, (expr, asg, got, exp)\n    print(f'OK {expr} {asg} -> {got}')\nprint('all symbol tests passed')\n\"",
  "workdir": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3"
}
```

OK A & B {'A': True, 'B': True} -> True
OK A & B {'A': True, 'B': False} -> False
OK A | B {'A': False, 'B': False} -> False
OK ~A {'A': False} -> True
OK !A {'A': False} -> True
OK A ^ B {'A': True, 'B': False} -> True
OK A ^ B {'A': True, 'B': True} -> False
OK A -> B {'A': True, 'B': False} -> False
OK A -> B {'A': False, 'B': False} -> True
OK A <-> B {'A': True, 'B': True} -> True
OK A <-> B {'A': True, 'B': False} -> False
all symbol tests passed

Command exited with code 0.

---

## Assistant

_Thinking:_



已寫好 `week3/sat.py` 並驗證通過。

做法：對 n 個變數依二進位 `00..0 → 11..1` 系統性列舉全部 `2^n` 列，逐列求值，公式為真即為一組解。複雜度 `O(2^n * m)`。

功能：
- `solve / find_one / is_satisfiable / is_valid / count_models`：一般布林式求解
- `print_truth_table / iter_truth_table`：印出完整真值表
- `solve_cnf / solve_cnf_int / load_dimacs`：CNF 子句集、DIMACS 整數編碼
- 運算子支援：`and/&/&&`、`or/|/||`、`not/~/!`、`^/xor`、`->/=>`、`\<->`、`True/False`

用法：
```bash
python sat.py "(A or B) and ((not A) or C)" --table
python sat.py "(A -> B) and A and (not B)"
python sat.py --cnf "[[1,-2],[-1,2]]" --vars "A B"
python sat.py --demo
```

---

## User

/export ./session.md

---

## Assistant

_Thinking:_



正在匯出對話紀錄。

**Tool: skill**

**Input:**
```json
{
  "id": "opencode"
}
```

<skill_content name="OpenCode">
# Skill: OpenCode

# OpenCode

Use this guide as the starting point for work involving OpenCode itself. It
covers the core concepts needed to configure and customize OpenCode, extend it
with plugins, and build integrations with the OpenCode SDK, clients, and API.

Full documentation is available at <https://opencode.ai/v2/docs/>. This overview is
only an index of core concepts. Before answering a question about a topic below,
fetch the URL named in that section and use the full page as the source of
truth. Follow links from that page when the question needs more detail. Fetch
<https://opencode.ai/v2/docs/> first when you need to discover the relevant
documentation page.

A machine-readable documentation index is available at
<https://opencode.ai/v2/llms.txt>.

## Version policy

Always answer for OpenCode V2 unless the user explicitly asks about V1,
legacy OpenCode, or migrating from V1.

Use only <https://opencode.ai/v2/docs/> documentation as the source of truth for V2.
Do not use <https://opencode.ai/docs/>, which documents V1, and do not use
general web search to resolve a V2 documentation question when the V2 docs or
linked pages cover it. The schema served from
<https://opencode.ai/config.json> may describe V1 even though V2 configuration
files include that URL for editor integration. Never use it to infer V2 field
names or shapes. If V2 documentation is missing or contradictory, state the
uncertainty or ask for clarification instead of falling back to V1.

V1 documentation and syntax may be consulted only when the user explicitly
asks about V1 or when needed as migration input. Outputs and recommendations
must still use V2 unless the user specifically requests a V1 result.

## [CLI](https://opencode.ai/v2/docs/cli)

For questions about the terminal interface, command-line invocation, `run`,
`mini`, terminal providers, or other CLI behavior, fetch the
[CLI guide](https://opencode.ai/v2/docs/cli) and the relevant page linked from
that section.

CLI and TUI preferences are separate from OpenCode's server and project
configuration. They live in the global `~/.config/opencode/cli.json`, or
`$XDG_CONFIG_HOME/opencode/cli.json` when `XDG_CONFIG_HOME` is set. There is no
project-local CLI configuration. Set `OPENCODE_CLI_CONFIG_CONTENT` to merge
inline JSON over the global settings. Most preferences can also be changed from
the TUI by pressing `Ctrl+P` and selecting **Open settings**.

### [Settings](https://opencode.ai/v2/docs/cli/config)

Fetch the full [CLI settings reference](https://opencode.ai/v2/docs/cli/config)
before editing `cli.json`. It documents every terminal-only setting, accepted
values, and examples, including themes, input, sessions, tabs, diffs, alerts,
Mini, keybindings, terminal plugins, and debugging. Do not put these settings
in `opencode.json(c)`.

### [Keybinds](https://opencode.ai/v2/docs/cli/keybinds)

Configure keybindings under `keybinds` in `cli.json`. The leader key is the
`keybinds.leader` entry; leader timing is configured separately under
`leader.timeout`. Bindings can use a string, an array of strings, or an object
when event behavior such as `preventDefault` is required. Disable a binding
with `"none"` or `false`.

Never guess a command ID, default binding, or accepted key syntax. Fetch the
full [keybind reference](https://opencode.ai/v2/docs/cli/keybinds), which lists
the current IDs and defaults, before answering or editing a binding.

## [OpenCode configuration](https://opencode.ai/v2/docs/config)

OpenCode's server and project configuration uses JSON or JSONC. Include the
published schema so the user's editor can validate fields and provide
autocomplete:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
}
```

Global configuration lives at `~/.config/opencode/opencode.json(c)` and applies
to every project for that user. Project configuration can live in any directory
as `opencode.json(c)` or `.opencode/opencode.json(c)`, including nested packages
in a monorepo.

During ordinary project discovery, OpenCode searches the current Location
directory and every ancestor through the filesystem root, including directories
above the detected project or repository root. It merges direct
`opencode.json(c)` files from the farthest ancestor to the current directory,
then does the same for `.opencode/opencode.json(c)` files. This means every
discovered `.opencode` config overrides every discovered direct config. Global
filesystem configuration has lower precedence than these discovered documents.

Common configuration fields include `model`, `default_agent`, `permissions`,
`agents`, `commands`, `plugins`, `providers`, `mcp`, `skills`, `instructions`,
`references`, `formatter`, and `lsp`.

This configuration is distinct from `cli.json`. Use the
[CLI settings reference](https://opencode.ai/v2/docs/cli/config) for terminal
preferences, especially themes and keybindings.

Do not guess field names or shapes. Fetch the V2 configuration guide and its
linked topic guide as the source of truth, and preserve unrelated settings when
editing an existing file. Keep the published `$schema` URL in configuration
examples, but do not fetch it to determine the V2 configuration shape.

See the [full configuration guide](https://opencode.ai/v2/docs/config) for
every field, examples, config locations, and links to dedicated feature guides.

## [MCP servers](https://opencode.ai/v2/docs/mcp-servers)

Configure MCP servers under `mcp.servers`. Prefer the CLI because it preserves
unrelated configuration. Use `--global` when the user asks to set up a service
for themselves without limiting it to the current project; omit it when they
explicitly want project-local configuration.

```sh
opencode mcp add <name> --global --url <remote-url>
opencode mcp list
```

Remote servers use OAuth by default. If `mcp list` reports that a server needs
authentication, tell the user to run `/mcps`, select the server, and sign in.
Do not run `opencode mcp auth` through the shell tool: it starts an interactive
flow whose authorization link can be hidden in background process output.
Use the user-facing MCP interface instead.

Report the server as configured but awaiting sign-in until its connection
status confirms it is connected.

OAuth credentials are stored outside the OpenCode configuration. Do not ask for or
store an API key when the server supports OAuth. Use header-based credentials
only when OAuth is unavailable or the user explicitly requires them, and use an
environment substitution such as `{env:MCP_API_KEY}` instead of writing a
secret into configuration.

## [V1 to V2 migration](https://opencode.ai/v2/docs/migrate-v1)

For any request to migrate OpenCode configuration, agents, commands, skills,
plugins, integrations, or other behavior from V1 to V2, read the full
[migration guide](https://opencode.ai/v2/docs/migrate-v1) before acting. In
the repository, its source is `services/www/src/docs/content/migrate-v1.mdx`.

V1 config files and `.opencode/` definitions are intended to remain compatible.
The only intentional breaking changes are the server API and plugin API. Native
V2 config uses more ergonomic shapes, but conversion is optional. When the user
requests conversion, inspect the complete configuration, preserve behavior and
unrelated settings, and apply only the relevant migrations from the guide. For
plugin migrations, fetch and follow both the migration guide and the full
[plugins guide](https://opencode.ai/v2/docs/build/plugins). If non-API V1
functionality fails in V2, use the `report` skill to file it as a compatibility
bug.

## [Plugins](https://opencode.ai/v2/docs/build/plugins)

For questions about creating, configuring, loading, publishing, or migrating
plugins, fetch the full [plugins guide](https://opencode.ai/v2/docs/build/plugins)
before answering. Refer to this guide when the user wants to build a plugin. It
covers hooks, transforms, tools, plugin context capabilities, and package
entrypoints. Plugins can also extend the TUI; for those, fetch the
[CLI plugin guide](https://opencode.ai/v2/docs/build/plugins/cli).
For custom methods and events shared with other plugins or clients, fetch the
[RPC guide](https://opencode.ai/v2/docs/build/plugins/rpc).

## [Service](https://opencode.ai/v2/docs/troubleshooting#check-the-background-service)

OpenCode uses a client-server architecture. Interfaces such as the TUI connect
to a background OpenCode service, which owns sessions, configuration, plugins,
permissions, and tool execution.

OpenCode normally discovers or starts the shared background service
automatically. If the service is stuck or unhealthy, restart it:

```sh
opencode service restart
```

Check its status after restarting:

```sh
opencode service status
```

## [API](https://opencode.ai/v2/docs/api)

OpenCode exposes an HTTP API from its server. The API is described by an
OpenAPI document available from the running server at `/openapi.json`.

Use OpenCode's built-in `api` command for local requests. It uses the same
discovery and authentication flow as the TUI and may start the background
service when no compatible healthy service is available. It accepts either an
HTTP method and path or an OpenAPI operation ID.

Call an endpoint with an HTTP method and path:

```sh
opencode api get /api/info
```

Pass a request body with `--data` or `-d`, and additional headers with
`--header` or `-H`:

```sh
opencode api post /api/example --data '{"key":"value"}'
opencode api get /api/example --header 'X-Example:value'
```

Request bodies default to `Content-Type: application/json`. When OpenCode is
connected to an explicit server instead of its managed background service, use
the same configured server and authentication context rather than constructing
an unauthenticated request separately.

See the [full API reference](https://opencode.ai/v2/docs/api) for available
endpoints, parameters, request bodies, and response schemas. The
raw [OpenAPI specification](https://opencode.ai/v2/openapi.json) is also
available for code generation and other tooling.

## [Client](https://opencode.ai/v2/docs/build/client)

For questions about connecting an application to OpenCode over the network,
fetch the full [client guide](https://opencode.ai/v2/docs/build/client) before
answering.

`@opencode/client` is the generated TypeScript client for the OpenCode HTTP
API. Its methods and types come from the same contract as the API reference.
The default entrypoint exposes Promise-based resource clients and async
iterables for streaming endpoints. The `@opencode/client/effect` entrypoint
exposes typed Effects, Streams, and decoded OpenCode schema values. Its
`Service` API can discover, start, stop, and authenticate with the local
background service from a Node application.

## [SDK](https://opencode.ai/v2/docs/build/sdk)

For questions about embedding OpenCode directly in an application, fetch the
full [SDK guide](https://opencode.ai/v2/docs/build/sdk) before answering. The SDK
hosts OpenCode in the application without opening an HTTP listener.

Use the [Effect SDK guide](https://opencode.ai/v2/docs/build/sdk/effect) for
Effect applications. For Cloudflare Durable Objects, use the
[Cloudflare SDK guide](https://opencode.ai/v2/docs/build/sdk/cloudflare).

## [Troubleshooting](https://opencode.ai/v2/docs/troubleshooting)

OpenCode runs a client and a background server. Start by determining whether a
problem belongs to the client, the shared server, or one project.

- Check the service with `opencode service status` and verify the API with
  `opencode api get /api/info`.
- Compare with `opencode --standalone`, which runs the TUI with a private
  server, to isolate shared-service issues.
- Inspect `~/.local/share/opencode/log/opencode.log`. Filter `role=cli` for
  client startup and `role=server` for sessions, providers, plugins,
  permissions, and tools.
- Run one reproduction with `OPENCODE_LOG_LEVEL=DEBUG` when normal logs are not
  sufficient.
- Do not delete or edit the database, service registration, or service config
  while diagnosing a problem. Back up persistent data before inspecting it
  with external tools.
- Redact API keys, authorization headers, prompts, file contents, and other
  sensitive data before sharing diagnostics.

See the [full troubleshooting guide](https://opencode.ai/v2/docs/troubleshooting)
for service lifecycle commands, API inspection, log locations, explicit server
connections, issue-reporting details, and local development paths.

Base directory for this skill: /builtin
Relative paths in this skill (e.g., scripts/, reference/) are relative to this base directory.
Note: file list is sampled.

<skill_files>
</skill_files>
</skill_content>

---

## Assistant

_Thinking:_



匯出指令收到 — 正在查找可用的匯出方式。

**Tool: execute**

**Input:**
```json
{
  "code": "const r = search({query: \"export session\"});\nreturn r;"
}
```

{
  "items": [
    {
      "path": "tools.opencode.session_move",
      "description": "Move a session to another directory, or omit sessionID to move the current session. The current session moves at the next safe boundary; do not run destination-dependent tools in the same execute call.",
      "signature": "tools.opencode.session_move({\n  /** Omit to move the current session. @pattern ^ses */\n  sessionID?: string,\n  /** Destination directory, relative to the target session's directory or absolute. Supports ~. @minLength 1 */\n  directory: string,\n}): Promise<{\n  /** @pattern ^ses */\n  sessionID: string,\n  directory: string,\n}>"
    },
    {
      "path": "tools.opencode.session_rename",
      "description": "Rename a session, or omit sessionID to rename the current session. Use a short, specific title that summarizes the work being done.",
      "signature": "tools.opencode.session_rename({\n  /** Omit to rename the current session. @pattern ^ses */\n  sessionID?: string,\n  /** New session title. @minLength 1 */\n  title: string,\n}): Promise<{\n  /** @pattern ^ses */\n  sessionID: string,\n  title: string,\n}>"
    },
    {
      "path": "tools.browser.tabs.list",
      "description": "List this session's browser tabs and the focused tab. Use returned IDs for all page operations.",
      "signature": "tools.browser.tabs.list(): Promise<{\n  tabs: Array<{\n      /** @pattern ^tab_[a-f0-9-]{36}$ */\n      id: string,\n      /** @maxLength 16384 */\n      url: string,\n      /** @maxLength 2048 */\n      title: string,\n      loading: boolean,\n      /** @maxLength 2048 */\n      loadError?: string,\n      canGoBack: boolean,\n      canGoForward: boolean,\n      /** @integer @minimum 0 */\n      generation: number,\n    }>,\n  focusedTabID: string | null,\n}>"
    },
    {
      "path": "tools.opencode.models",
      "description": "Search the models available to use. Use this to turn a model name the user mentions into an exact reference before running a subagent on it. Check your own provider first.",
      "signature": "tools.opencode.models({\n  /** Text to search for in model names and IDs. */\n  query?: string,\n  /** Provider ID or name to filter by. Try your own provider first. */\n  provider?: string,\n  /** Include older versions of each model family. By default only the newest version is listed. */\n  all?: boolean,\n  /** Maximum number of models to return. Defaults to 20. @integer @minimum 1 @maximum 100 */\n  limit?: number,\n  /** Number of models to skip, for paging through results. @integer @minimum 0 */\n  offset?: number,\n}): Promise<{\n  /** Matching models grouped by provider. Your own provider comes first. */\n  providers: Array<{\n      id: string,\n      name: string,\n      /** Newest first. */\n      models: Array<{\n          /** providerID/modelID */\n          id: string,\n          name: string,\n          /** Release date as a Unix timestamp in milliseconds, or 0 when unknown. */\n          released: number,\n          variants: Array<string>,\n          /** Pricing in USD per million tokens. */\n          cost: Array<{\n              tier?: {\n                type: \"context\",\n                /** @integer */\n                size: number,\n              },\n              input: number,\n              output: number,\n              cache: {\n                read: number,\n                write: number,\n              },\n            }>,\n          status: \"alpha\" | \"beta\" | \"deprecated\" | \"active\",\n        }>,\n    }>,\n  /** Number of matching models across all pages. @integer */\n  total: number,\n  /** Offset of the next page, or null on the last page. */\n  next: number | null,\n}>"
    }
  ],
  "remaining": 0,
  "next": null
}

---

## Assistant

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py"
}
```

Read file /Users/xueshengji4/Desktop/emma/_alg/homework/week3/sat.py, lines 1-500
1: #!/usr/bin/env python3
2: # -*- coding: utf-8 -*-
3: """
4: sat.py — 以「系統性列舉真值表」解決 SAT 布林滿足問題 (Brute-force SAT Solver)
5: 
6: 方法：對 n 個變數，依二進位順序 00..0 → 11..1 系統性列舉全部 2^n 種賦值，
7: 逐列求值，若公式為真則為一組解 (model)。時間複雜度 O(2^n * m)，
8: 其中 m 為公式求值成本；空間複雜度 O(n)。
9: 
10: 支援兩種輸入：
11:   1. 布林運算式字串 (一般 SAT)：例如 "(A and B) or (not A and C)"
12:      支援運算子：and/&/&& , or/|/|| , not/~/! , ^ (xor), -> (蘊含), <-> (等值)
13:   2. CNF 子句集 (串列格式)：例如 [[1, -2], [-1, 2]] (DIMACS 整數編碼)
14:      或 [["A", "-B"], ["-A", "B"]]
15: 
16: 主要函數：
17:   solve(expr)            -> 回傳所有滿足賦值 (list[dict])
18:   is_satisfiable(expr)   -> 是否可滿足 (bool)
19:   find_one(expr)         -> 回傳一組解或 None
20:   solve_cnf(clauses, ...) -> 解 CNF
21:   print_truth_table(expr) -> 印出完整真值表
22: 
23: CLI 範例：
24:   python sat.py "(A or B) and (not A or C)"
25:   python sat.py "(A -> B) and A" --table
26:   python sat.py --cnf "[[1,-2],[-1,2,3]]" --vars "A B C"
27:   python sat.py --demo
28: """
29: 
30: import argparse
31: import itertools
32: import re
33: import sys
34: 
35: 
36: # ---------- 1. 運算式前處理 ----------
37: 
38: _KEYWORDS = {"and", "or", "not", "True", "False", "xor"}
39: 
40: def extract_variables(expr: str) -> list:
41:     """從運算式中取出變數名稱 (排序後回傳，確保列舉順序固定)。"""
42:     tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)
43:     vars_ = sorted({t for t in tokens if t not in _KEYWORDS})
44:     return vars_
45: 
46: 
47: def normalize_expr(expr: str) -> str:
48:     """把各種寫法統一轉成 Python 可 eval 的布林運算式。
49: 
50:     支援：
51:       && -> and,  || -> or,  ! -> not (但 != 保留),
52:       & -> and,   | -> or,   ~ -> not,  ^ -> xor,
53:       A -> B  (蘊含, 等價於 (not A) or B),
54:       A <-> B (等值, 等價於 (A == B))
55:       True/False 大小寫皆可；TRUE/FALSE 轉成 True/False
56:     """
57:     s = expr.strip()
58: 
59:     # TRUE/FALSE 統一大小寫 (避免誤傷變數內含此子字串：只取代完整單字)
60:     s = re.sub(r"\bTRUE\b", "True", s, flags=re.IGNORECASE)
61:     s = re.sub(r"\bFALSE\b", "False", s, flags=re.IGNORECASE)
62:     # XOR 關鍵字轉成 ^ 以便後續處理
63:     s = re.sub(r"\bxor\b", "^", s, flags=re.IGNORECASE)
64: 
65:     # 先把 && || & | 轉成 and/or，以便後續遞迴能以單一寫法切分
66:     s = s.replace("&&", " and ").replace("||", " or ")
67:     s = s.replace("!=", "\x00NE\x00").replace("==", "\x00EQ\x00")
68:     s = s.replace("<=", "\x00LE\x00").replace(">=", "\x00GE\x00")
69:     s = s.replace("&", " and ").replace("|", " or ")
70:     s = s.replace("\x00NE\x00", "!=").replace("\x00EQ\x00", "==")
71:     s = s.replace("\x00LE\x00", "<=").replace("\x00GE\x00", ">=")
72: 
73:     # 改寫 -> / <-> (支援巢狀括號與 and/or/not 內任意位置出現)
74:     # 策略：A <-> B 轉成 ((A) __EQ__ (B))；A -> B 轉成 ((not (A)) or (B))
75:     s = _rewrite_arrows(s)
76: 
77:     # 剩餘符號轉 Python 關鍵字 (此時已無 -> / <->)
78:     # ~ 與 ! 轉 not (!= 已被保護，不受影響)
79:     s = s.replace("~", " not ")
80:     s = re.sub(r"!(?!=)", " not ", s)
81:     # ^ 轉成 != (布林 xor：True/False 相異即為真)
82:     s = re.sub(r"\^", " != ", s)
83:     # __EQ__ 還原為 Python 語法
84:     s = s.replace("__EQ__", "==")
85:     s = re.sub(r"\s+", " ", s).strip()
86:     return s
87: 
88: 
89: def _split_top_level(s: str, ops: tuple) -> list:
90:     """以頂層 (括號深度 0) 的運算子切分字串，回傳 [運算元, 運算子, 運算元, ...]。"""
91:     parts, depth, cur, i = [], 0, "", 0
92:     while i < len(s):
93:         if s[i] == "(":
94:             depth += 1
95:             cur += s[i]
96:             i += 1
97:         elif s[i] == ")":
98:             depth -= 1
99:             cur += s[i]
100:             i += 1
101:         elif depth == 0:
102:             matched = None
103:             for op in sorted(ops, key=len, reverse=True):
104:                 if s.startswith(op, i):
105:                     # -> 不可誤判 <-> 的前半；呼叫端保證已先處理 <->，此處只做保險
106:                     matched = op
107:                     break
108:             if matched:
109:                 parts.append(cur.strip())
110:                 parts.append(matched)
111:                 cur = ""
112:                 i += len(matched)
113:             else:
114:                 cur += s[i]
115:                 i += 1
116:         else:
117:             cur += s[i]
118:             i += 1
119:     parts.append(cur.strip())
120:     return parts
121: 
122: 
123: def _strip_outer_parens(s: str):
124:     """若整個字串被一對括號包住，回傳內層；否則回傳 None。"""
125:     s = s.strip()
126:     if len(s) < 2 or s[0] != "(" or s[-1] != ")":
127:         return None
128:     depth = 0
129:     for i, ch in enumerate(s):
130:         if ch == "(":
131:             depth += 1
132:         elif ch == ")":
133:             depth -= 1
134:             if depth == 0 and i != len(s) - 1:
135:                 return None  # 首個 '(' 在結尾前就關閉，非整體包覆
136:     return s[1:-1]
137: 
138: 
139: def _split_top_level_word(s: str, word: str):
140:     """以頂層的單字運算子 (and/or) 切分，回傳運算元串列；無切分則回傳 [s]。"""
141:     parts, depth, cur, i = [], 0, "", 0
142:     wlen = len(word)
143:     while i < len(s):
144:         if s[i] == "(":
145:             depth += 1
146:             cur += s[i]
147:             i += 1
148:         elif s[i] == ")":
149:             depth -= 1
150:             cur += s[i]
151:             i += 1
152:         elif depth == 0 and s[i:i + wlen].lower() == word:
153:             before = s[i - 1] if i > 0 else " "
154:             after = s[i + wlen] if i + wlen < len(s) else " "
155:             if not (before.isalnum() or before == "_") and not (after.isalnum() or after == "_"):
156:                 parts.append(cur)
157:                 cur = ""
158:                 i += wlen
159:                 continue
160:             cur += s[i]
161:             i += 1
162:         else:
163:             cur += s[i]
164:             i += 1
165:     parts.append(cur)
166:     return parts
167: 
168: 
169: def _rewrite_arrows(s: str) -> str:
170:     """遞迴改寫任意深度的 <-> 與 ->。
171: 
172:     A <-> B  =>  ((A) __EQ__ (B))，之後 __EQ__ 還原為 ==
173:     A -> B   =>  ((not (A)) or (B))，直接展開為 Python 語法
174:     多個鏈式 (A -> B -> C) 視為右結合：A -> (B -> C)。
175:     透過遞迴深入 and/or/not/括號內層，確保巢狀如 "(A -> B) and C" 也能改寫。
176:     """
177:     s = s.strip()
178:     # 先處理 <-> (優先級最低)
179:     parts = _split_top_level(s, ("<->",))
180:     if len(parts) > 1:
181:         operands = [_rewrite_arrows(p) for p in parts[::2]]
182:         out = operands[0]
183:         for q in operands[1:]:
184:             out = f"(({out}) __EQ__ ({q}))"
185:         return out
186:     # 再處理 ->
187:     parts = _split_top_level(s, ("->", "=>"))
188:     if len(parts) > 1:
189:         operands = [_rewrite_arrows(p) for p in parts[::2]]
190:         # 右結合
191:         out = operands[-1]
192:         for p in reversed(operands[:-1]):
193:             out = f"((not ({p})) or ({out}))"
194:         return out
195:     # 深入 and / or 內層
196:     for word in ("and", "or"):
197:         parts = _split_top_level_word(s, word)
198:         if len(parts) > 1:
199:             return f" {word} ".join(f"({_rewrite_arrows(p)})" for p in parts)
200:     # 前綴 not
201:     m = re.match(r"(?i)^\s*not\s+(.*)$", s, re.DOTALL)
202:     if m:
203:         return f"not ({_rewrite_arrows(m.group(1))})"
204:     # 整體括號：剝掉一層後繼續深入
205:     inner = _strip_outer_parens(s)
206:     if inner is not None:
207:         return f"({_rewrite_arrows(inner)})"
208:     return s
209: 
210: 
211: def _safe_eval(py_expr: str, assignment: dict) -> bool:
212:     """以受限環境求值：只允許變數名與 and/or/not/True/False/==/!=/括號。"""
213:     allowed_names = set(assignment.keys()) | {"True", "False"}
214:     code = compile(py_expr, "<sat-expr>", "eval")
215:     # 阻擋屬性存取、函數呼叫等：只允許 Name / BoolOp / UnaryOp / Compare / Constant
216:     import ast as _ast
217:     tree = _ast.parse(py_expr, mode="eval")
218:     for node in _ast.walk(tree):
219:         if isinstance(node, _ast.Call):
220:             raise ValueError("運算式不允許函數呼叫")
221:         if isinstance(node, _ast.Attribute):
222:             raise ValueError("運算式不允許屬性存取")
223:         if isinstance(node, _ast.Name) and node.id not in allowed_names | {"and", "or", "not"}:
224:             raise ValueError(f"未知變數或關鍵字: {node.id}")
225:     return bool(eval(code, {"__builtins__": {}}, assignment))  # noqa: S307 (輸入為本地公式)
226: 
227: 
228: # ---------- 2. 真值表系統性列舉 ----------
229: 
230: def iter_truth_table(expr: str, variables: list = None):
231:     """系統性列舉真值表：依二進位計數 00..0 → 11..1 逐列產生 (assignment, value)。
232: 
233:     Yields:
234:         (dict, bool): (變數賦值, 公式在此賦值下的真值)
235:     """
236:     variables = variables if variables is not None else extract_variables(expr)
237:     py_expr = normalize_expr(expr)
238:     n = len(variables)
239:     for bits in itertools.product([False, True], repeat=n):
240:         assignment = dict(zip(variables, bits))
241:         yield assignment, _safe_eval(py_expr, assignment)
242: 
243: 
244: def print_truth_table(expr: str, variables: list = None, file=sys.stdout):
245:     """印出完整真值表，並回傳 (variables, rows)，rows 為 [(assignment, value)]。"""
246:     variables = variables if variables is not None else extract_variables(expr)
247:     rows = list(iter_truth_table(expr, variables))
248:     # 表頭
249:     header = " | ".join(variables + ["F"])
250:     print(header, file=file)
251:     print("-" * len(header), file=file)
252:     for assignment, value in rows:
253:         line = " | ".join("1" if assignment[v] else "0" for v in variables)
254:         line += " | " + ("1" if value else "0")
255:         print(line, file=file)
256:     return variables, rows
257: 
258: 
259: # ---------- 3. SAT 求解 ----------
260: 
261: def solve(expr: str, variables: list = None) -> list:
262:     """回傳所有滿足賦值 (models)。空串列代表 UNSAT。"""
263:     return [a for a, v in iter_truth_table(expr, variables) if v]
264: 
265: 
266: def find_one(expr: str, variables: list = None):
267:     """回傳一組滿足賦值；若 UNSAT 回傳 None (找到即停，不必列舉完全部)。"""
268:     for assignment, value in iter_truth_table(expr, variables):
269:         if value:
270:             return assignment
271:     return None
272: 
273: 
274: def is_satisfiable(expr: str, variables: list = None) -> bool:
275:     """公式是否可滿足 (SAT)。"""
276:     return find_one(expr, variables) is not None
277: 
278: 
279: def is_valid(expr: str, variables: list = None) -> bool:
280:     """公式是否為恆真式 (tautology)：所有列皆為真。"""
281:     return all(v for _, v in iter_truth_table(expr, variables))
282: 
283: 
284: def count_models(expr: str, variables: list = None) -> int:
285:     """計算滿足賦值的個數 (#SAT)。"""
286:     return sum(1 for _, v in iter_truth_table(expr, variables) if v)
287: 
288: 
289: # ---------- 4. CNF 求解 (子句集版本) ----------
290: 
291: def eval_cnf(clauses: list, assignment: dict) -> bool:
292:     """求值 CNF：clauses 為子句的串列，每個子句為 literal 串列。
293: 
294:     literal 可以是：
295:       - 字串："A" 表肯定，" -A" / "!A" / "~A" / "¬A" 表否定
296:       - 元組 (var, is_neg)：如 ("A", True)
297:     空子句為 False (UNSAT 核心)；空子句集為 True。
298:     """
299:     for clause in clauses:
300:         sat_clause = False
301:         for lit in clause:
302:             var, neg = parse_literal(lit)
303:             val = assignment.get(var, False)
304:             if neg:
305:                 val = not val
306:             if val:
307:                 sat_clause = True
308:                 break
309:         if not sat_clause:
310:             return False
311:     return True
312: 
313: 
314: def parse_literal(lit) -> tuple:
315:     """回傳 (var, is_neg)。"""
316:     if isinstance(lit, tuple) and len(lit) == 2:
317:         return lit[0], bool(lit[1])
318:     if isinstance(lit, str):
319:         s = lit.strip()
320:         for prefix in ("-", "!", "~", "¬", "not "):
321:             if s.startswith(prefix):
322:                 return s[len(prefix):].strip(), True
323:         return s, False
324:     raise ValueError(f"無法解析 literal: {lit!r}")
325: 
326: 
327: def cnf_variables(clauses: list) -> list:
328:     """取出 CNF 中所有變數 (排序)。"""
329:     vars_ = set()
330:     for clause in clauses:
331:         for lit in clause:
332:             var, _ = parse_literal(lit)
333:             vars_.add(var)
334:     return sorted(vars_)
335: 
336: 
337: def solve_cnf(clauses: list, variables: list = None, find_all: bool = True):
338:     """以真值表列舉解 CNF。
339: 
340:     Args:
341:         clauses: 子句集，如 [["A", "-B"], ["-A", "B"]]
342:         variables: 變數順序；None 則自動推導
343:         find_all: True 回傳全部解；False 只找一組 (找到即停)
344: 
345:     Returns:
346:         list[dict]：滿足賦值串列 (UNSAT 時為 [])
347:     """
348:     variables = variables if variables is not None else cnf_variables(clauses)
349:     n = len(variables)
350:     models = []
351:     for bits in itertools.product([False, True], repeat=n):
352:         assignment = dict(zip(variables, bits))
353:         if eval_cnf(clauses, assignment):
354:             models.append(dict(assignment))
355:             if not find_all:
356:                 break
357:     return models
358: 
359: 
360: def solve_cnf_int(clauses_int: list, var_names: list = None):
361:     """以 DIMACS 風格整數編碼解 CNF。
362: 
363:     Args:
364:         clauses_int: 如 [[1, -2], [-1, 2, 3]]，數字為變數編號 (1-based)，負號表否定
365:         var_names: 編號對應的變數名，如 ["A", "B", "C"]；None 則用 "x1", "x2", ...
366: 
367:     Returns:
368:         (models, var_names)：models 為賦值 dict 的串列
369:     """
370:     max_var = 0
371:     for clause in clauses_int:
372:         for lit in clause:
373:             max_var = max(max_var, abs(int(lit)))
374:     if var_names is None:
375:         var_names = [f"x{i}" for i in range(1, max_var + 1)]
376:     assert len(var_names) >= max_var, "var_names 數量不足"
377:     str_clauses = []
378:     for clause in clauses_int:
379:         c = []
380:         for lit in clause:
381:             lit = int(lit)
382:             name = var_names[abs(lit) - 1]
383:             c.append(f"-{name}" if lit < 0 else name)
384:         str_clauses.append(c)
385:     return solve_cnf(str_clauses, var_names[:max_var]), var_names[:max_var]
386: 
387: 
388: def load_dimacs(path: str):
389:     """讀取 DIMACS CNF 檔案，回傳 (clauses_int, n_vars)。"""
390:     clauses, cur = [], []
391:     n_vars = 0
392:     with open(path, encoding="utf-8") as f:
393:         for line in f:
394:             line = line.strip()
395:             if not line or line.startswith("c"):
396:                 continue
397:             if line.startswith("p"):
398:                 # p cnf <n_vars> <n_clauses>
399:                 n_vars = int(line.split()[2])
400:                 continue
401:             for tok in line.split():
402:                 lit = int(tok)
403:                 if lit == 0:
404:                     clauses.append(cur)
405:                     cur = []
406:                 else:
407:                     cur.append(lit)
408:     return clauses, n_vars
409: 
410: 
411: # ---------- 5. CLI ----------
412: 
413: def fmt_assignment(a: dict) -> str:
414:     return "{" + ", ".join(f"{k}={'1' if v else '0'}" for k, v in a.items()) + "}"
415: 
416: 
417: def main(argv=None) -> int:
418:     ap = argparse.ArgumentParser(description="以真值表列舉解 SAT 布林滿足問題")
419:     ap.add_argument("expr", nargs="?", default=None, help="布林運算式，如 \"(A or B) and (not A or C)\"")
420:     ap.add_argument("--table", action="store_true", help="印出完整真值表")
421:     ap.add_argument("--cnf", default=None, help="CNF 整數子句集，如 \"[[1,-2],[-1,2]]\"")
422:     ap.add_argument("--vars", default=None, help="變數名，空白分隔，如 \"A B C\"")
423:     ap.add_argument("--dimacs", default=None, help="DIMACS CNF 檔案路徑")
424:     ap.add_argument("--demo", action="store_true", help="執行內建示範")
425:     args = ap.parse_args(argv)
426: 
427:     if args.demo or (args.expr is None and args.cnf is None and args.dimacs is None):
428:         demo()
429:         return 0
430: 
431:     if args.dimacs:
432:         clauses_int, n_vars = load_dimacs(args.dimacs)
433:         var_names = args.vars.split() if args.vars else None
434:         models, names = solve_cnf_int(clauses_int, var_names)
435:         print(f"變數: {names} (共 {len(names)} 個, 搜尋空間 2^{len(names)} = {2 ** len(names)})")
436:         print(f"子句數: {len(clauses_int)}")
437:         if models:
438:             print(f"SAT: 找到 {len(models)} 組解，例如 {fmt_assignment(models[0])}")
439:         else:
440:             print("UNSAT: 無滿足賦值")
441:         return 0
442: 
443:     if args.cnf:
444:         import ast as _ast
445:         clauses_int = _ast.literal_eval(args.cnf)
446:         var_names = args.vars.split() if args.vars else None
447:         models, names = solve_cnf_int(clauses_int, var_names)
448:         print(f"變數: {names} (共 {len(names)} 個, 搜尋空間 2^{len(names)} = {2 ** len(names)})")
449:         print(f"子句: {clauses_int}")
450:         if models:
451:             print(f"SAT: 共 {len(models)} 組解")
452:             for m in models:
453:                 print("  " + fmt_assignment(m))
454:         else:
455:             print("UNSAT: 無滿足賦值")
456:         return 0
457: 
458:     expr = args.expr
459:     variables = args.vars.split() if args.vars else extract_variables(expr)
460:     if args.table:
461:         print_truth_table(expr, variables)
462:         print()
463:     models = solve(expr, variables)
464:     n = len(variables)
465:     print(f"公式: {expr}")
466:     print(f"變數: {variables} (共 {n} 個, 搜尋空間 2^{n} = {2 ** n})")
467:     if models:
468:         print(f"SAT: 共 {len(models)} 組解")
469:         for m in models:
470:             print("  " + fmt_assignment(m))
471:     else:
472:         print("UNSAT: 無滿足賦值")
473:     return 0
474: 
475: 
476: def demo():
477:     cases = [
478:         ("(A or B) and ((not A) or C)", "一般 SAT：應為 SAT"),
479:         ("A and (not A)", "UNSAT 經典例"),
480:         ("(A -> B) and A and (not B)", "蘊含 + Modus Ponens 反例 (UNSAT)"),
481:         ("(A <-> B) and (B <-> C) and (A and (not C))", "等值鏈矛盾 (UNSAT)"),
482:     ]
483:     for expr, note in cases:
484:         print(f"=== {note} ===")
485:         print(f"公式: {expr}")
486:         variables, _ = print_truth_table(expr)
487:         models = solve(expr, variables)
488:         if models:
489:             print(f"=> SAT，共 {len(models)} 組解，第一組: {fmt_assignment(models[0])}\n")
490:         else:
491:             print("=> UNSAT，無解\n")
492:     print("=== CNF 整數編碼範例 ===")
493:     clauses_int = [[1, -2], [-1, 2], [1, 2]]
494:     models, names = solve_cnf_int(clauses_int, ["A", "B"])
495:     print(f"子句: {clauses_int} (即 (A∨¬B) ∧ (¬A∨B) ∧ (A∨B))")
496:     print(f"=> {'SAT: ' + str([fmt_assignment(m) for m in models]) if models else 'UNSAT'}")
497: 
498: 
499: if __name__ == "__main__":
500:     sys.exit(main())

---

## Assistant

_Thinking:_



**Tool: write**

**Input:**
```json
{
  "content": "# Session Export — SAT 真值表求解器\n\n- Date (UTC): 2026-09-23\n- Workdir: `/Users/xueshengji4/Desktop/emma/_alg/homework/week3`\n- Session: ses_f33e94b65ffep1SKsasSYMLqLy\n\n## 1. 使用者需求\n\n> 請寫一個sat.py 可以系統性的列舉真值表，解決 SAT 布林滿足問題\n\n## 2. 實作內容 (`sat.py`)\n\n以 Brute-force 系統性列舉 `00..0 → 11..1` 共 `2^n` 列，逐列求值。\n\n- 時間複雜度：`O(2^n * m)`，空間：`O(n)`\n- 支援運算子：`and/&/&&`, `or/|/||`, `not/~/!`, `^/xor`, `->/=>`, `<->`, `True/False`\n- 核心函數：\n  - `extract_variables(expr)`\n  - `normalize_expr(expr)` + `_rewrite_arrows(s)` + `_safe_eval`\n  - `iter_truth_table(expr)` / `print_truth_table(expr)`\n  - `solve(expr)` / `find_one(expr)` / `is_satisfiable(expr)` / `is_valid(expr)` / `count_models(expr)`\n  - CNF: `eval_cnf`, `parse_literal`, `solve_cnf`, `solve_cnf_int`, `load_dimacs`\n  - CLI: `main()` + `demo()`\n\n### CLI 用法\n\n```bash\npython sat.py \"(A or B) and ((not A) or C)\" --table\npython sat.py \"(A -> B) and A and (not B)\"\npython sat.py --cnf \"[[1,-2],[-1,2]]\" --vars \"A B\"\npython sat.py --demo\n```\n\n## 3. 開發過程問題與修正\n\n- 問題：`(A -> B) and A and (not B)` 出現 `SyntaxError`，因 `_rewrite_arrows` 只處理頂層 `->`，括號內的蘊含未被改寫。\n- 修正：\n  1. `normalize_expr` 先統一 `&&/||/&/|` → `and/or`，再呼叫 `_rewrite_arrows`\n  2. `_rewrite_arrows` 改為遞迴深入 `and/or/not/括號` 內層：\n     - 新增 `_strip_outer_parens()`、`_split_top_level_word()`\n     - 先處理 `<->`，再處理 `->/=>`（右結合），再遞迴 `and/or`、`not`、整體括號\n\n## 4. 驗證結果\n\n- `python sat.py --demo`：4 組一般 SAT/UNSAT + CNF 範例全過\n  - `(A or B) and ((not A) or C)` → SAT，4 組解\n  - `A and (not A)` → UNSAT\n  - `(A -> B) and A and (not B)` → UNSAT\n  - `(A <-> B) and (B <-> C) and (A and (not C))` → UNSAT\n  - `[[1,-2],[-1,2],[1,2]]` → SAT `{A=1,B=1}`\n- 符號測試全過：`&, |, ~, !, ^, ->, <->`\n- API 測試：\n  - `is_satisfiable('A and (not A)')` → `False`\n  - `find_one('(A or B) and (not A)')` → `{'A': False, 'B': True}`\n  - `count_models('A or B')` → `3`\n  - `solve_cnf([['A','-B'],['-A','B']])` → 2 組解\n  - `is_valid('A or (not A)')` → `True`\n\n## 5. 檔案狀態\n\n- `sat.py`: 已完成，約 500 行，無外部依賴\n- 本檔：`session.md`（會話匯出）\n",
  "path": "/Users/xueshengji4/Desktop/emma/_alg/homework/week3/session.md"
}
```

Created file successfully: session.md

---

## Assistant

_Thinking:_



已匯出至 `./session.md`（`week3/session.md`），內容包含需求、實作摘要、`->/<->` 巢狀修正、驗證結果與 CLI 用法。
