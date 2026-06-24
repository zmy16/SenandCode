class ParseError(SyntaxError):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected_kind=None):
        token = self.current_token()
        if not token:
            raise ParseError("Tak terduga: akhir dari puisi")
        if expected_kind and token[0] != expected_kind:
            line = token[2] if len(token) > 2 else "?"
            col = token[3] if len(token) > 3 else "?"
            raise ParseError(
                f"Baris {line}, kolom {col}: kuharap {expected_kind}, "
                f"namun kudapat {token[0]} '{token[1]}'"
            )
        self.pos += 1
        return token

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.tokens[idx] if 0 <= idx < len(self.tokens) else None

    def parse(self):
        stmts = []
        while self.current_token():
            stmt = self.statement()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def statement(self):
        tok = self.current_token()
        if not tok:
            return None
        k = tok[0]
        if k == "KEYWORD_DECLARE":
            return self.declare_stmt()
        elif k == "KEYWORD_PRINT":
            return self.print_stmt()
        elif k == "KEYWORD_IF":
            return self.if_stmt()
        elif k == "KEYWORD_FOR":
            return self.loop_stmt()
        elif k == "KEYWORD_WHILE":
            return self.while_stmt()
        elif k == "KEYWORD_BREAK":
            self.eat("KEYWORD_BREAK")
            self.eat("SEMICOLON")
            return ("break",)
        elif k == "KEYWORD_CONTINUE":
            self.eat("KEYWORD_CONTINUE")
            self.eat("SEMICOLON")
            return ("continue",)
        elif k == "KEYWORD_FUNC":
            return self.func_stmt()
        elif k == "KEYWORD_RETURN":
            return self.return_stmt()
        elif k == "KEYWORD_CLASS":
            return self.class_stmt()
        elif k == "KEYWORD_TRY":
            return self.try_stmt()
        elif k == "KEYWORD_THROW":
            self.eat("KEYWORD_THROW")
            e = self.expression()
            self.eat("SEMICOLON")
            return ("throw", e)
        elif k == "KEYWORD_INPUT":
            return self.input_stmt()
        elif k == "VARIABLE":
            if self.peek(1) and self.peek(1)[0] == "OPERATOR" and self.peek(1)[1] == "=":
                return self.assignment_stmt()
            if self.peek(1) and self.peek(1)[0] in ("DOT", "LBRACKET"):
                return self.member_assignment_stmt()
            return self.expr_stmt()
        elif k == "KEYWORD_THIS":
            if self.peek(1) and self.peek(1)[0] in ("DOT", "LBRACKET"):
                return self.member_assignment_stmt()
            return self.expr_stmt()
        elif k == "KEYWORD_END":
            self.eat("KEYWORD_END")
            return ("end_block",)
        else:
            return self.expr_stmt()

    def declare_stmt(self):
        """simpan <expr> dalam <target>;  (target = variable or member_get)"""
        self.eat("KEYWORD_DECLARE")
        expr = self.expression()
        self.eat("KEYWORD_IN")
        target = self.parse_assign_target()
        self.eat("SEMICOLON")
        if isinstance(target, tuple) and target[0] == "variable":
            return ("declare", target[1], expr)
        elif isinstance(target, tuple) and target[0] == "member_get":
            return ("member_assign", target, expr)
        raise ParseError("Target harus berupa variabel atau anggota kelas")

    def assignment_stmt(self):
        """<var> = <expr>;"""
        name = self.eat("VARIABLE")[1]
        self.eat("OPERATOR")
        expr = self.expression()
        self.eat("SEMICOLON")
        return ("assign", name, expr)

    def member_assignment_stmt(self):
        """<member_get|index_get> = <expr>;  OR just expr stmt with member/index access"""
        target = self.member_access()
        if self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] == "=":
            self.eat("OPERATOR")
            expr = self.expression()
            self.eat("SEMICOLON")
            if isinstance(target, tuple) and target[0] == "index_get":
                return ("index_assign", target[1], target[2], expr)
            return ("member_assign", target, expr)
        if self.current_token() and self.current_token()[0] == "SEMICOLON":
            self.eat("SEMICOLON")
        return ("expr", target)

    def print_stmt(self):
        """lukiskan <expr> (lalu <expr>)*;"""
        self.eat("KEYWORD_PRINT")
        exprs = [self.expression()]
        while self.current_token() and self.current_token()[0] == "KEYWORD_CONCAT":
            self.eat("KEYWORD_CONCAT")
            exprs.append(self.expression())
        self.eat("SEMICOLON")
        return ("print", exprs)

    def input_stmt(self):
        """dengarkan <var>;"""
        self.eat("KEYWORD_INPUT")
        name = self.eat("VARIABLE")[1]
        prompt = None
        if self.current_token() and self.current_token()[0] == "STRING":
            prompt = self.eat("STRING")[1][1:-1]
        self.eat("SEMICOLON")
        return ("input", name, prompt)

    def if_stmt(self):
        """seandainya <cond>: <body> (atau jika <cond>: <body>)* (jika tidak: <body>)? selesai"""
        self.eat("KEYWORD_IF")
        cond = self.expression()
        if self.current_token() and self.current_token()[0] == "KEYWORD_DO":
            self.eat("KEYWORD_DO")
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.block(stop_kinds={"KEYWORD_END", "KEYWORD_ELIF", "KEYWORD_ELSE"})
        branches = [("if", cond, body)]
        else_body = None
        while self.current_token():
            tok = self.current_token()
            if tok[0] == "KEYWORD_ELIF":
                self.eat("KEYWORD_ELIF")
                cond = self.expression()
                if self.current_token() and self.current_token()[0] == "KEYWORD_DO":
                    self.eat("KEYWORD_DO")
                if self.current_token() and self.current_token()[0] == "COLON":
                    self.eat("COLON")
                body = self.block(stop_kinds={"KEYWORD_END", "KEYWORD_ELIF", "KEYWORD_ELSE"})
                branches.append(("elif", cond, body))
            elif tok[0] == "KEYWORD_ELSE":
                self.eat("KEYWORD_ELSE")
                if self.current_token() and self.current_token()[0] == "COLON":
                    self.eat("COLON")
                body = self.block(stop_kinds={"KEYWORD_END"})
                else_body = body
                break
            else:
                break
        if self.current_token() and self.current_token()[0] == "KEYWORD_END":
            self.eat("KEYWORD_END")
        return ("if_chain", branches, else_body)

    def loop_stmt(self):
        """untuk <var> = <start> sampai <end> (langkah <step>)? lakukan: <body> selesai"""
        self.eat("KEYWORD_FOR")
        var = self.eat("VARIABLE")[1]
        self.eat("OPERATOR")
        start = self.expression()
        self.eat("KEYWORD_TO")
        end = self.expression()
        step = None
        if self.current_token() and self.current_token()[0] == "KEYWORD_STEP":
            self.eat("KEYWORD_STEP")
            step = self.expression()
        if self.current_token() and self.current_token()[0] == "KEYWORD_DO":
            self.eat("KEYWORD_DO")
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.block()
        return ("loop", var, start, end, step, body)

    def while_stmt(self):
        """selagi <cond> lakukan: <body> selesai"""
        self.eat("KEYWORD_WHILE")
        cond = self.expression()
        if self.current_token() and self.current_token()[0] == "KEYWORD_DO":
            self.eat("KEYWORD_DO")
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.block()
        return ("while", cond, body)

    def func_stmt(self):
        """puisi <name>(<params>): <body> selesai"""
        self.eat("KEYWORD_FUNC")
        name = self.eat("VARIABLE")[1]
        self.eat("LPAREN")
        params = []
        if self.current_token() and self.current_token()[0] != "RPAREN":
            params.append(self.eat("VARIABLE")[1])
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.eat("COMMA")
                params.append(self.eat("VARIABLE")[1])
        self.eat("RPAREN")
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.block()
        return ("function", name, params, body)

    def return_stmt(self):
        """kembalikan <expr>;"""
        self.eat("KEYWORD_RETURN")
        expr = self.expression()
        self.eat("SEMICOLON")
        return ("return", expr)

    def class_stmt(self):
        """wajah <name> (warisi <parent>)?: <body> selesai"""
        self.eat("KEYWORD_CLASS")
        name = self.eat("VARIABLE")[1]
        parent = None
        if self.current_token() and self.current_token()[0] == "KEYWORD_EXTENDS":
            self.eat("KEYWORD_EXTENDS")
            parent = self.eat("VARIABLE")[1]
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.class_body()
        return ("class", name, parent, body)

    def try_stmt(self):
        """coba: <body> (raih <var>: <body>)? (akhirnya: <body>)? selesai"""
        self.eat("KEYWORD_TRY")
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        try_body = self.block(stop_kinds={"KEYWORD_END", "KEYWORD_CATCH", "KEYWORD_FINALLY"})
        catch_var = None
        catch_body = None
        if self.current_token() and self.current_token()[0] == "KEYWORD_CATCH":
            self.eat("KEYWORD_CATCH")
            if self.current_token() and self.current_token()[0] == "VARIABLE":
                catch_var = self.eat("VARIABLE")[1]
            if self.current_token() and self.current_token()[0] == "COLON":
                self.eat("COLON")
            catch_body = self.block(stop_kinds={"KEYWORD_END", "KEYWORD_FINALLY"})
        finally_body = None
        if self.current_token() and self.current_token()[0] == "KEYWORD_FINALLY":
            self.eat("KEYWORD_FINALLY")
            if self.current_token() and self.current_token()[0] == "COLON":
                self.eat("COLON")
            finally_body = self.block(stop_kinds={"KEYWORD_END"})
        if self.current_token() and self.current_token()[0] == "KEYWORD_END":
            self.eat("KEYWORD_END")
        return ("try", try_body, catch_var, catch_body, finally_body)

    def parse_assign_target(self):
        """Parse a variable or member access as assignment target."""
        tok = self.current_token()
        if not tok:
            raise ParseError("Tak terduga: akhir input saat parsing target")
        if tok[0] == "KEYWORD_THIS":
            self.eat("KEYWORD_THIS")
            obj = ("this",)
        elif tok[0] == "VARIABLE":
            name = self.eat("VARIABLE")[1]
            obj = ("variable", name)
        else:
            raise ParseError(f"Target tak dikenal: {tok[1]}")
        while self.current_token() and self.current_token()[0] == "DOT":
            self.eat("DOT")
            member = self.eat("VARIABLE")[1]
            obj = ("member_get", obj, member)
        return obj

    def block(self, stop_kinds=None):
        if stop_kinds is None:
            stop_kinds = {"KEYWORD_END"}
        stmts = []
        while self.current_token():
            tok = self.current_token()
            if tok[0] in stop_kinds:
                break
            s = self.statement()
            if s is not None and s[0] != "end_block":
                stmts.append(s)
        return stmts

    def class_body(self):
        items = []
        while self.current_token():
            tok = self.current_token()
            if tok[0] == "KEYWORD_END":
                self.eat("KEYWORD_END")
                break
            if tok[0] == "KEYWORD_DECLARE":
                self.eat("KEYWORD_DECLARE")
                expr = self.expression()
                self.eat("KEYWORD_IN")
                target = self.parse_assign_target()
                self.eat("SEMICOLON")
                if isinstance(target, tuple) and target[0] == "variable":
                    items.append(("property", target[1], expr))
                elif isinstance(target, tuple) and target[0] == "member_get":
                    items.append(("expr", ("member_assign", target, expr)))
                else:
                    raise ParseError("Target properti tidak valid")
            elif tok[0] == "KEYWORD_FUNC":
                self.eat("KEYWORD_FUNC")
                name = self.eat("VARIABLE")[1]
                self.eat("LPAREN")
                params = []
                if self.current_token() and self.current_token()[0] != "RPAREN":
                    params.append(self.eat("VARIABLE")[1])
                    while self.current_token() and self.current_token()[0] == "COMMA":
                        self.eat("COMMA")
                        params.append(self.eat("VARIABLE")[1])
                self.eat("RPAREN")
                if self.current_token() and self.current_token()[0] == "COLON":
                    self.eat("COLON")
                body = self.block(stop_kinds={"KEYWORD_END"})
                items.append(("function", name, params, body))
                if self.current_token() and self.current_token()[0] == "KEYWORD_END":
                    self.eat("KEYWORD_END")
            else:
                break
        return items

    def expr_stmt(self):
        expr = self.expression()
        if self.current_token() and self.current_token()[0] == "SEMICOLON":
            self.eat("SEMICOLON")
        return ("expr", expr)

    def expression(self):
        return self.concat()

    def concat(self):
        node = self.logical_or()
        while self.current_token() and self.current_token()[0] == "KEYWORD_CONCAT":
            self.eat("KEYWORD_CONCAT")
            node = ("binop", node, "concat", self.logical_or())
        return node

    def logical_or(self):
        node = self.logical_and()
        while self.current_token() and self.current_token()[0] == "KEYWORD_OR":
            self.eat("KEYWORD_OR")
            node = ("binop", node, "or", self.logical_and())
        return node

    def logical_and(self):
        node = self.not_operator()
        while self.current_token() and self.current_token()[0] == "KEYWORD_AND":
            self.eat("KEYWORD_AND")
            node = ("binop", node, "and", self.not_operator())
        return node

    def not_operator(self):
        if self.current_token() and self.current_token()[0] == "KEYWORD_NOT":
            self.eat("KEYWORD_NOT")
            return ("unop", "not", self.not_operator())
        return self.comparison()

    def comparison(self):
        node = self.arithmetic()
        ops = {"==", "!=", "<", ">", "<=", ">="}
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ops:
            op = self.eat("OPERATOR")[1]
            node = ("binop", node, op, self.arithmetic())
        return node

    def arithmetic(self):
        node = self.term()
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ("+", "-"):
            op = self.eat("OPERATOR")[1]
            node = ("binop", node, op, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ("*", "/", "%"):
            op = self.eat("OPERATOR")[1]
            node = ("binop", node, op, self.factor())
        return node

    def factor(self):
        tok = self.current_token()
        if not tok:
            raise ParseError("Tak terduga: akhir dari puisi")
        k = tok[0]
        if k == "LBRACKET":
            return self.array_literal()
        elif k == "NUMBER":
            self.eat("NUMBER")
            return ("number", float(tok[1]) if "." in tok[1] else int(tok[1]))
        elif k == "STRING":
            self.eat("STRING")
            return ("string", tok[1][1:-1])
        elif k == "KEYWORD_TRUE":
            self.eat("KEYWORD_TRUE")
            return ("boolean", True)
        elif k == "KEYWORD_FALSE":
            self.eat("KEYWORD_FALSE")
            return ("boolean", False)
        elif k == "KEYWORD_NULL":
            self.eat("KEYWORD_NULL")
            return ("null", None)
        elif k == "KEYWORD_NEW":
            self.eat("KEYWORD_NEW")
            cls = self.eat("VARIABLE")[1]
            self.eat("LPAREN")
            args = self.parse_args_rparen()
            self.eat("RPAREN")
            return ("new", cls, args)
        elif k == "LPAREN":
            self.eat("LPAREN")
            node = self.expression()
            self.eat("RPAREN")
            return node
        elif k == "OPERATOR" and tok[1] == "-":
            self.eat("OPERATOR")
            return ("unop", "-", self.factor())
        elif k == "OPERATOR" and tok[1] == "+":
            self.eat("OPERATOR")
            return self.factor()
        elif k == "KEYWORD_THIS":
            self.eat("KEYWORD_THIS")
            obj = ("this",)
            return self.handle_postfix(obj)
        elif k == "VARIABLE":
            name = self.eat("VARIABLE")[1]
            obj = ("variable", name)
            return self.handle_postfix(obj)
        else:
            raise ParseError(f"Tak terduga: {k} '{tok[1]}'")

    def array_literal(self):
        """Parse [item, item, ...] — trailing comma allowed."""
        self.eat("LBRACKET")
        items = []
        if self.current_token() and self.current_token()[0] != "RBRACKET":
            items.append(self.expression())
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.eat("COMMA")
                if self.current_token() and self.current_token()[0] == "RBRACKET":
                    break
                items.append(self.expression())
        self.eat("RBRACKET")
        return ("array", items)

    def handle_postfix(self, obj):
        while self.current_token():
            if self.current_token()[0] == "DOT":
                self.eat("DOT")
                member = self.eat("VARIABLE")[1]
                if self.current_token() and self.current_token()[0] == "LPAREN":
                    self.eat("LPAREN")
                    args = self.parse_args_rparen()
                    self.eat("RPAREN")
                    obj = ("member_call", obj, member, args)
                else:
                    obj = ("member_get", obj, member)
            elif self.current_token()[0] == "LPAREN":
                self.eat("LPAREN")
                args = self.parse_args_rparen()
                self.eat("RPAREN")
                obj = ("call", obj if isinstance(obj, str) else obj[1] if obj[0] == "variable" else None, args)
            elif self.current_token()[0] == "LBRACKET":
                self.eat("LBRACKET")
                index = self.expression()
                self.eat("RBRACKET")
                obj = ("index_get", obj, index)
            else:
                break
        return obj

    def parse_args_rparen(self):
        args = []
        if self.current_token() and self.current_token()[0] != "RPAREN":
            args.append(self.expression())
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.eat("COMMA")
                args.append(self.expression())
        return args

    def member_access(self):
        if self.current_token()[0] == "KEYWORD_THIS":
            self.eat("KEYWORD_THIS")
            obj = ("this",)
        else:
            name = self.eat("VARIABLE")[1]
            obj = ("variable", name)
        while self.current_token():
            if self.current_token()[0] == "DOT":
                self.eat("DOT")
                member = self.eat("VARIABLE")[1]
                if self.current_token() and self.current_token()[0] == "LPAREN":
                    self.eat("LPAREN")
                    args = self.parse_args_rparen()
                    self.eat("RPAREN")
                    obj = ("member_call", obj, member, args)
                else:
                    obj = ("member_get", obj, member)
            elif self.current_token()[0] == "LBRACKET":
                self.eat("LBRACKET")
                index = self.expression()
                self.eat("RBRACKET")
                obj = ("index_get", obj, index)
            else:
                break
        return obj
