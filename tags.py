import asyncio
import json
import random
import urllib.parse
from typing import Any, Dict, List, Optional


class ScriptSyntaxError(Exception):
    """スクリプトの構文エラーを示す例外クラス"""

    pass


class Parser:

    def __init__(self, globals_dict: Optional[Dict[str, Any]] = None):
        # 外部から与えられる組み込み変数 (文字列化して保持)
        self.globals: Dict[str, str] = (
            {k: str(v) for k, v in globals_dict.items()}
            if globals_dict
            else {}
        )

        # ユーザー定義変数
        self.variables: Dict[str, str] = {}

        # 関数定義: {関数名: (引数名のリスト, 未評価のプログラム文字列)}
        self.functions: Dict[str, tuple[List[str], str]] = {}
        self.default_functions: Dict[str, Any] = {}

        # ローカルスコープ（関数実行時の引数などを保持するスタック）
        self.local_scopes: List[Dict[str, str]] = []

    async def parse(self, text: str) -> str:
        """テキストを解析・実行し、最終的な文字列を返します。"""
        # 実行ごとにユーザー変数とスコープをリセット（必要に応じて初期化制御してください）
        self.variables = {}
        self.local_scopes = []

        # 1. 括弧の対応関係チェック
        self._check_brackets(text)

        # 2. 構文木（トークンツリー）の構築
        ast = self._build_ast(text)

        # 3. 構文木の評価
        return await self._evaluate_ast(ast)

    def _check_brackets(self, text: str) -> None:
        """括弧の対応チェック（SyntaxErrorのハンドリング）"""
        count = 0
        for char in text:
            if char == "{":
                count += 1
            elif char == "}":
                count -= 1
                if count < 0:
                    raise ScriptSyntaxError(
                        "閉じ括弧 '}' が開き括弧 '{' より先に現れました。"
                    )
        if count != 0:
            raise ScriptSyntaxError(
                f"括弧の対応が取れていません。開き括弧が {count} 個多く存在します。"
            )

    def _build_ast(self, text: str) -> List[Any]:
        """テキストを解析し、プレーンテキストと式 `{...}` のネスト構造木（AST）に変換します。"""
        stack: List[List[Any]] = [[]]
        i = 0
        n = len(text)

        while i < n:
            if text[i] == "{":
                # 新しい式の階層を開始
                stack.append([])
                i += 1
            elif text[i] == "}":
                # 現在の式の階層が終了
                if len(stack) <= 1:
                    raise ScriptSyntaxError("不正な閉じ括弧です。")
                completed_expr = stack.pop()
                # 親の階層に「式オブジェクト」として追加
                stack[-1].append({"type": "expression", "content": completed_expr})
                i += 1
            else:
                # プレーンテキストの収集
                start = i
                while i < n and text[i] != "{" and text[i] != "}":
                    i += 1
                stack[-1].append(text[start:i])

        return stack[0]

    async def _evaluate_ast(self, ast: List[Any]) -> str:
        """構築されたASTを順番に評価（実行）して文字列を結合します。"""
        result = []
        for node in ast:
            if isinstance(node, str):
                # パススルーテキスト
                result.append(node)
            elif isinstance(node, dict) and node.get("type") == "expression":
                # 式の評価
                result.append(await self._execute_expression(node["content"]))
        try:
            return "".join(result)
        except TypeError:
            return ""

    def _clean_token(self, text: str) -> str:
        """区切り文字前後の改行やタブ、不要な空白を除去します。"""
        return text.strip()

    def _split_arguments(self, tokens: List[Any]) -> List[List[Any]]:
        """パイプライン `|` でトークンリストを引数ごとに分割します。
        トップレベルにある `|` のみを対象とします。
        """
        args = []
        current_arg = []
        for token in tokens:
            if isinstance(token, str) and "|" in token:
                # 文字列内にパイプがある場合、分割して処理
                parts = token.split("|")
                for j, part in enumerate(parts):
                    if j > 0:
                        args.append(current_arg)
                        current_arg = []
                    current_arg.append(part)
            else:
                current_arg.append(token)
        if current_arg:
            args.append(current_arg)
        return args

    def add_func(self, name: str, func):
        self.default_functions[name] = func

    def _eval_condition(self, cond_str: str) -> bool:
        operators = [">=", "<=", "==", "!=", ">", "<"]
        op_found = None
        
        for op in operators:
            if op in cond_str:
                op_found = op
                break
                
        if not op_found:
            return bool(self._clean_token(cond_str))
            
        left_raw, right_raw = cond_str.split(op_found, 1)
        left = self._clean_token(left_raw)
        right = self._clean_token(right_raw)
        
        if op_found in [">=", "<=", ">", "<"]:
            try:
                l_num = float(left)
                r_num = float(right)
                
                if op_found == ">=": return l_num >= r_num
                if op_found == "<=": return l_num <= r_num
                if op_found == ">":  return l_num > r_num
                if op_found == "<":  return l_num < r_num
            except ValueError:
                return False
                
        if op_found == "==":
            return left == right
        if op_found == "!=":
            return left != right
            
        return False

    async def _execute_expression(self, tokens: List[Any]) -> str:
        """`{...}` の内部を評価します。"""
        # 1. まず、引数の区切り `|` を基準にトップレベルで分割する
        raw_args = self._split_arguments(tokens)

        # 2. 各引数の「最初の文字列トークン」に含まれる `:` を処理し、コマンドや変数名を抽出
        if not raw_args:
            return ""

        first_arg_tokens = raw_args[0]
        first_token_str = ""
        for t in first_arg_tokens:
            if isinstance(t, str):
                first_token_str += t
            else:
                first_token_str += await self._evaluate_ast([t])

        first_token_str = self._clean_token(first_token_str)

        # --- 各種構文の分岐処理 ---

        # A. コマンド付きの構文 (コロン `:` を含む場合)
        if ":" in first_token_str:
            command, main_arg = first_token_str.split(":", 1)
            command = self._clean_token(command)
            main_arg = self._clean_token(main_arg)

            # =========================================================
            # 【修正点】以前ここにあった evaluated_tail_args の一括評価を削除。
            # if と func では中身を実行してはいけないため、下の else ブロック内へ移動します。
            # =========================================================

            if command == "if":
                # 最初のみ main_arg が最初の条件式になる
                current_cond = (await self._evaluate_ast(first_arg_tokens)).split(":", 1)[1]
                
                # 最初(if)の条件を評価
                if self._eval_condition(current_cond):
                    return await self._evaluate_ast(raw_args[1]) if len(raw_args) > 1 else ""
                
                # マッチしなかった場合、以降の elif / else を探す
                idx = 2
                while idx < len(raw_args):
                    block_head = await self._evaluate_ast(raw_args[idx])
                    cleaned_head = self._clean_token(block_head)
                    
                    if cleaned_head.startswith("elif:"):
                        cond_part = cleaned_head.split(":", 1)[1]
                        if self._eval_condition(cond_part):
                            if idx + 1 < len(raw_args):
                                return await self._evaluate_ast(raw_args[idx + 1])
                            return ""
                        idx += 2
                    elif cleaned_head == "else":
                        if idx + 1 < len(raw_args):
                            return await self._evaluate_ast(raw_args[idx + 1])
                        return ""
                    else:
                        idx += 1
                return ""

            # 関数定義: {func:関数名|引数1,引数2|{プログラム}} ※遅延評価
            elif command == "func":
                func_name = main_arg
                arg_names = []
                func_body_tokens = []

                if len(raw_args) >= 3:
                    raw_arg_names = await self._evaluate_ast(raw_args[1])
                    arg_names = [
                        self._clean_token(a) for a in raw_arg_names.split(",") if a
                    ]
                    func_body_tokens = raw_args[2]
                elif len(raw_args) == 2:
                    func_body_tokens = raw_args[1]

                self.functions[func_name] = (arg_names, func_body_tokens)
                return ""

            else:
                # =========================================================
                # 【修正点】if と func 以外のコマンドの時のみ、後続の引数を評価する
                # =========================================================
                evaluated_tail_args = [
                    (await self._evaluate_ast(arg)).strip() for arg in raw_args[1:]
                ]

                if command == "set":
                    val = evaluated_tail_args[0] if evaluated_tail_args else ""
                    self.variables[main_arg] = val
                    return ""

                # 変数の取得: {get:変数名}
                elif command == "get":
                    return self._get_variable(main_arg)

                # 関数呼び出し: {call:関数名|引数1|引数2|...}
                elif command == "call":
                    func_name = main_arg
                    if func_name not in self.functions:
                        return ""

                    arg_names, body_tokens = self.functions[func_name]
                    call_args = evaluated_tail_args

                    local_scope = {}
                    for idx, name in enumerate(arg_names):
                        local_scope[name] = (
                            call_args[idx] if idx < len(call_args) else ""
                        )

                    self.local_scopes.append(local_scope)
                    try:
                        result = await self._evaluate_ast(body_tokens)
                    finally:
                        self.local_scopes.pop()
                    return result

                # 組み込み関数: {random:最小値~最大値}
                elif command == "random":
                    try:
                        low, high = map(int, main_arg.split("~"))
                        return str(random.randint(low, high))
                    except Exception:
                        return ""

                # 組み込み関数: {choice:選択肢1|選択肢2}
                elif command == "choice":
                    choices = [main_arg] + evaluated_tail_args
                    choices = [c for c in choices if c]
                    return random.choice(choices) if choices else ""

                # 組み込み関数: {urlencode:文字列}
                elif command == "urlencode":
                    return urllib.parse.quote(main_arg)

                else:
                    if not self.default_functions.get(command):
                        return ""
                    try:
                        return await self.default_functions.get(command)(self.globals, [main_arg] + evaluated_tail_args)
                    except:
                        return ""

        # B. 変数参照・引数参照の構文: {変数名} (コロン `:` を含まない場合)
        else:
            var_name = first_token_str
            return self._get_variable(var_name)

        return ""

    def _get_variable(self, name: str) -> str:
        """ローカル引数 -> ユーザー定義変数 -> 組み込み変数 の順で変数を探索します。"""
        # 1. 関数内ローカルスコープ（引数）を直近（スタックの最上位）から探索
        if self.local_scopes:
            for scope in reversed(self.local_scopes):
                if name in scope:
                    return scope[name]

        # 2. ユーザー定義変数
        if name in self.variables:
            return self.variables[name]

        # 3. システム組み込み変数
        if name in self.globals:
            return self.globals[name]

        # 未定義の場合は空文字列
        return ""
    
if __name__ == "__main__":
    async def embed(globals, args):
        if not args:
            return ""

        _dict = {}
        for _ in " ".join(args).split(","):
            data = _.split("=", 1)
            _dict[data[0]] = data[1]
        
        return str(_dict)

    text = """
{embed:title=test,a=a}
"""

    async def run():
        parser1 = Parser()
        parser1.add_func("embed", embed)

        print((await parser1.parse(text)).strip())

    asyncio.run(run())