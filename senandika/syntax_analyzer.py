
from dataclasses import dataclass, field
from typing import Any, Optional


class GayaError(SyntaxError):

    def __init__(self, message: str, line: int = 0, col: int = 0):
        self.line = line
        self.col = col
        super().__init__(f"[{line}:{col}] {message}" if line else message)


class Expression:
    pass


@dataclass
class NumberLiteral(Expression):
    value: Any


@dataclass
class StringLiteral(Expression):
    value: str


@dataclass
class BooleanLiteral(Expression):
    value: bool


@dataclass
class NullLiteral(Expression):
    pass


@dataclass
class VariableRef(Expression):
    name: str


@dataclass
class ArrayLiteral(Expression):
    items: list


@dataclass
class IndexAccess(Expression):
    target: Expression
    index: Expression


@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression


@dataclass
class ThisRef(Expression):
    pass


@dataclass
class MemberAccess(Expression):
    obj: Expression
    member: str


@dataclass
class MethodCall(Expression):
    obj: Expression
    method: str
    args: list


@dataclass
class FuncCall(Expression):
    name: str
    args: list


@dataclass
class NewExpr(Expression):
    class_name: str
    args: list


class Statement:
    pass


@dataclass
class DeclareStmt(Statement):
    name: str
    value: Expression


@dataclass
class AssignStmt(Statement):
    name: str
    value: Expression


@dataclass
class IndexAssignStmt(Statement):
    target: Expression
    index: Expression
    value: Expression


@dataclass
class MemberAssignStmt(Statement):
    target_name: str
    member: str
    value: Expression


@dataclass
class PrintStmt(Statement):
    expressions: list


@dataclass
class InputStmt(Statement):
    variable: str
    prompt: Optional[str]


@dataclass
class IfStmt(Statement):
    branches: list  # [(condition: Expression, body: list[Statement])]
    else_body: Optional[list[Statement]]


@dataclass
class ForStmt(Statement):
    variable: str
    start: Expression
    end: Expression
    body: list[Statement]


@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: list[Statement]


@dataclass
class BreakStmt(Statement):
    pass


@dataclass
class ContinueStmt(Statement):
    pass


@dataclass
class FuncDef(Statement):
    name: str
    params: list
    body: list[Statement]


@dataclass
class ReturnStmt(Statement):
    value: Expression


@dataclass
class ClassDef(Statement):
    name: str
    parent: Optional[str]
    body: list  # list of FuncDef + property tuples (for now)


@dataclass
class TryStmt(Statement):
    try_body: list[Statement]
    catch_var: Optional[str]
    catch_body: Optional[list[Statement]]
    finally_body: Optional[list[Statement]]


@dataclass
class ThrowStmt(Statement):
    value: Expression


@dataclass
class ExprStmt(Statement):
    expr: Expression


class SyntaxAnalyzer:

    def __init__(self, tokens: list):
        self.tokens = list(tokens)
        self.pos = 0


    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected_kind=None):
        token = self.current_token()
        if not token:
            raise GayaError("Tak terduga: akhir dari puisi")
        kind, value, line, col = token[0], token[1], token[2], token[3]
        if expected_kind and kind != expected_kind:
            raise GayaError(
                f"Kuharap {expected_kind}, namun kudapat {kind} '{value}'",
                line=line, col=col,
            )
        self.pos += 1
        return token

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.tokens[idx] if 0 <= idx < len(self.tokens) else None


    def olah(self):
        stmts: list[Statement] = []
        while self.current_token():
            stmt = self.statement()
            if stmt is not None:
                stmts.append(stmt)
        return stmts


    def statement(self) -> Optional[Statement]:
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
            return BreakStmt()
        elif k == "KEYWORD_CONTINUE":
            self.eat("KEYWORD_CONTINUE")
            self.eat("SEMICOLON")
            return ContinueStmt()
        elif k == "KEYWORD_FUNC":
            return self.func_def()
        elif k == "KEYWORD_RETURN":
            return self.return_stmt()
        elif k == "KEYWORD_CLASS":
            return self.class_def()
        elif k == "KEYWORD_TRY":
            return self.try_stmt()
        elif k == "KEYWORD_THROW":
            self.eat("KEYWORD_THROW")
            e = self.expression()
            self.eat("SEMICOLON")
            return ThrowStmt(value=e)
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
            return None  # sentinel, filtered in block()
        else:
            return self.expr_stmt()

    def declare_stmt(self) -> Statement:
        self.eat("KEYWORD_DECLARE")
        expr = self.expression()
        self.eat("KEYWORD_IN")
        target = self.parse_assign_target()
        self.eat("SEMICOLON")
        if isinstance(target, VariableRef):
            return DeclareStmt(name=target.name, value=expr)
        elif isinstance(target, MemberAccess):
            return self._member_assign_from_expr(target, expr)
        raise GayaError("Target harus berupa variabel atau anggota kelas")

    def _member_assign_from_expr(self, target: MemberAccess, value: Expression) -> MemberAssignStmt:
        if isinstance(target.obj, VariableRef):
            return MemberAssignStmt(target_name=target.obj.name, member=target.member, value=value)
        elif isinstance(target.obj, ThisRef):
            return MemberAssignStmt(target_name="this", member=target.member, value=value)
        raise GayaError("Target anggota tidak dikenali")

    def assignment_stmt(self) -> Statement:
        name = self.eat("VARIABLE")[1]
        self.eat("OPERATOR")
        expr = self.expression()
        self.eat("SEMICOLON")
        return AssignStmt(name=name, value=expr)

    def member_assignment_stmt(self) -> Statement:
        target = self.member_access()
        tok = self.current_token()
        if tok and tok[0] == "OPERATOR" and tok[1] == "=":
            self.eat("OPERATOR")
            expr = self.expression()
            self.eat("SEMICOLON")
            if isinstance(target, IndexAccess):
                return IndexAssignStmt(target=target.target, index=target.index, value=expr)
            elif isinstance(target, MemberAccess):
                return self._member_assign_from_expr(target, expr)
            return ExprStmt(expr=target)
        if tok and tok[0] == "SEMICOLON":
            self.eat("SEMICOLON")
        return ExprStmt(expr=target)

    def print_stmt(self) -> Statement:
        self.eat("KEYWORD_PRINT")
        exprs = [self.expression()]
        while self.current_token() and self.current_token()[0] == "KEYWORD_CONCAT":
            self.eat("KEYWORD_CONCAT")
            exprs.append(self.expression())
        self.eat("SEMICOLON")
        return PrintStmt(expressions=exprs)

    def input_stmt(self) -> Statement:
        self.eat("KEYWORD_INPUT")
        name = self.eat("VARIABLE")[1]
        prompt = None
        if self.current_token() and self.current_token()[0] == "STRING":
            prompt = self.eat("STRING")[1][1:-1]
        self.eat("SEMICOLON")
        return InputStmt(variable=name, prompt=prompt)

    def if_stmt(self) -> Statement:
        self.eat("KEYWORD_IF")
        cond = self.expression()
        if self.current_token() and self.current_token()[0] == "KEYWORD_DO":
            self.eat("KEYWORD_DO")
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.block(stop_kinds={"KEYWORD_END", "KEYWORD_ELIF", "KEYWORD_ELSE"})
        branches = [(cond, body)]
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
                branches.append((cond, body))
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
        return IfStmt(branches=branches, else_body=else_body)

    def loop_stmt(self) -> Statement:
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
        return ForStmt(variable=var, start=start, end=end, body=body)

    def while_stmt(self) -> Statement:
        self.eat("KEYWORD_WHILE")
        cond = self.expression()
        if self.current_token() and self.current_token()[0] == "KEYWORD_DO":
            self.eat("KEYWORD_DO")
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.block()
        return WhileStmt(condition=cond, body=body)

    def func_def(self) -> Statement:
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
        return FuncDef(name=name, params=params, body=body)

    def return_stmt(self) -> Statement:
        self.eat("KEYWORD_RETURN")
        expr = self.expression()
        self.eat("SEMICOLON")
        return ReturnStmt(value=expr)

    def class_def(self) -> Statement:
        self.eat("KEYWORD_CLASS")
        name = self.eat("VARIABLE")[1]
        parent = None
        if self.current_token() and self.current_token()[0] == "KEYWORD_EXTENDS":
            self.eat("KEYWORD_EXTENDS")
            parent = self.eat("VARIABLE")[1]
        if self.current_token() and self.current_token()[0] == "COLON":
            self.eat("COLON")
        body = self.class_body()
        return ClassDef(name=name, parent=parent, body=body)

    def try_stmt(self) -> Statement:
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
        return TryStmt(try_body=try_body, catch_var=catch_var, catch_body=catch_body, finally_body=finally_body)

    def expr_stmt(self) -> Statement:
        expr = self.expression()
        if self.current_token() and self.current_token()[0] == "SEMICOLON":
            self.eat("SEMICOLON")
        return ExprStmt(expr=expr)


    def block(self, stop_kinds=None) -> list[Statement]:
        if stop_kinds is None:
            stop_kinds = {"KEYWORD_END"}
        stmts: list[Statement] = []
        while self.current_token():
            tok = self.current_token()
            if tok[0] in stop_kinds:
                break
            s = self.statement()
            if s is not None:
                stmts.append(s)
        return stmts

    def class_body(self) -> list:
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
                if isinstance(target, VariableRef):
                    items.append(("property", target.name, expr))
                elif isinstance(target, MemberAccess):
                    items.append(("expr", self._member_assign_from_expr(target, expr)))
                else:
                    raise GayaError("Target properti tidak valid")
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
                items.append(FuncDef(name=name, params=params, body=body))
                if self.current_token() and self.current_token()[0] == "KEYWORD_END":
                    self.eat("KEYWORD_END")
            else:
                break
        return items


    def parse_assign_target(self) -> Expression:
        tok = self.current_token()
        if not tok:
            raise GayaError("Tak terduga: akhir input saat parsing target")
        if tok[0] == "KEYWORD_THIS":
            self.eat("KEYWORD_THIS")
            obj: Expression = ThisRef()
        elif tok[0] == "VARIABLE":
            name = self.eat("VARIABLE")[1]
            obj: Expression = VariableRef(name=name)
        else:
            raise GayaError(f"Target tak dikenal: {tok[1]}")
        while self.current_token() and self.current_token()[0] == "DOT":
            self.eat("DOT")
            member = self.eat("VARIABLE")[1]
            obj = MemberAccess(obj=obj, member=member)
        return obj


    def expression(self) -> Expression:
        return self.concat()

    def concat(self) -> Expression:
        node = self.logical_or()
        while self.current_token() and self.current_token()[0] == "KEYWORD_CONCAT":
            self.eat("KEYWORD_CONCAT")
            node = BinaryOp(left=node, operator="concat", right=self.logical_or())
        return node

    def logical_or(self) -> Expression:
        node = self.logical_and()
        while self.current_token() and self.current_token()[0] == "KEYWORD_OR":
            self.eat("KEYWORD_OR")
            node = BinaryOp(left=node, operator="or", right=self.logical_and())
        return node

    def logical_and(self) -> Expression:
        node = self.not_operator()
        while self.current_token() and self.current_token()[0] == "KEYWORD_AND":
            self.eat("KEYWORD_AND")
            node = BinaryOp(left=node, operator="and", right=self.not_operator())
        return node

    def not_operator(self) -> Expression:
        if self.current_token() and self.current_token()[0] == "KEYWORD_NOT":
            self.eat("KEYWORD_NOT")
            return UnaryOp(operator="not", operand=self.not_operator())
        return self.comparison()

    def comparison(self) -> Expression:
        node = self.arithmetic()
        ops = {"==", "!=", "<", ">", "<=", ">="}
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ops:
            op = self.eat("OPERATOR")[1]
            node = BinaryOp(left=node, operator=op, right=self.arithmetic())
        return node

    def arithmetic(self) -> Expression:
        node = self.term()
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ("+", "-"):
            op = self.eat("OPERATOR")[1]
            node = BinaryOp(left=node, operator=op, right=self.term())
        return node

    def term(self) -> Expression:
        node = self.factor()
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ("*", "/", "%"):
            op = self.eat("OPERATOR")[1]
            node = BinaryOp(left=node, operator=op, right=self.factor())
        return node

    def factor(self) -> Expression:
        tok = self.current_token()
        if not tok:
            raise GayaError("Tak terduga: akhir dari puisi")
        k = tok[0]
        line, col = tok[2], tok[3]

        if k == "LBRACKET":
            return self.array_literal()
        elif k == "NUMBER":
            self.eat("NUMBER")
            return NumberLiteral(value=float(tok[1]) if "." in tok[1] else int(tok[1]))
        elif k == "STRING":
            self.eat("STRING")
            return StringLiteral(value=tok[1][1:-1])
        elif k == "KEYWORD_TRUE":
            self.eat("KEYWORD_TRUE")
            return BooleanLiteral(value=True)
        elif k == "KEYWORD_FALSE":
            self.eat("KEYWORD_FALSE")
            return BooleanLiteral(value=False)
        elif k == "KEYWORD_NULL":
            self.eat("KEYWORD_NULL")
            return NullLiteral()
        elif k == "KEYWORD_NEW":
            self.eat("KEYWORD_NEW")
            cls = self.eat("VARIABLE")[1]
            self.eat("LPAREN")
            args = self.parse_args_rparen()
            self.eat("RPAREN")
            return NewExpr(class_name=cls, args=args)
        elif k == "LPAREN":
            self.eat("LPAREN")
            node = self.expression()
            self.eat("RPAREN")
            return node
        elif k == "OPERATOR" and tok[1] == "-":
            self.eat("OPERATOR")
            return UnaryOp(operator="-", operand=self.factor())
        elif k == "OPERATOR" and tok[1] == "+":
            self.eat("OPERATOR")
            return self.factor()
        elif k == "KEYWORD_THIS":
            self.eat("KEYWORD_THIS")
            obj: Expression = ThisRef()
            return self.handle_postfix(obj)
        elif k == "VARIABLE":
            name = self.eat("VARIABLE")[1]
            obj: Expression = VariableRef(name=name)
            return self.handle_postfix(obj)
        else:
            raise GayaError(
                f"Tak terduga: {k} '{tok[1]}'",
                line=line, col=col,
            )

    def array_literal(self) -> Expression:
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
        return ArrayLiteral(items=items)

    def handle_postfix(self, obj: Expression) -> Expression:
        while self.current_token():
            if self.current_token()[0] == "DOT":
                self.eat("DOT")
                member = self.eat("VARIABLE")[1]
                if self.current_token() and self.current_token()[0] == "LPAREN":
                    self.eat("LPAREN")
                    args = self.parse_args_rparen()
                    self.eat("RPAREN")
                    obj = MethodCall(obj=obj, method=member, args=args)
                else:
                    obj = MemberAccess(obj=obj, member=member)
            elif self.current_token()[0] == "LPAREN":
                self.eat("LPAREN")
                args = self.parse_args_rparen()
                self.eat("RPAREN")
                if isinstance(obj, VariableRef):
                    obj = FuncCall(name=obj.name, args=args)
                else:
                    obj = FuncCall(name="", args=args)
            elif self.current_token()[0] == "LBRACKET":
                self.eat("LBRACKET")
                index = self.expression()
                self.eat("RBRACKET")
                obj = IndexAccess(target=obj, index=index)
            else:
                break
        return obj


    def parse_args_rparen(self) -> list[Expression]:
        args = []
        if self.current_token() and self.current_token()[0] != "RPAREN":
            args.append(self.expression())
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.eat("COMMA")
                args.append(self.expression())
        return args


    def member_access(self) -> Expression:
        if self.current_token()[0] == "KEYWORD_THIS":
            self.eat("KEYWORD_THIS")
            obj: Expression = ThisRef()
        else:
            name = self.eat("VARIABLE")[1]
            obj: Expression = VariableRef(name=name)
        while self.current_token():
            if self.current_token()[0] == "DOT":
                self.eat("DOT")
                member = self.eat("VARIABLE")[1]
                if self.current_token() and self.current_token()[0] == "LPAREN":
                    self.eat("LPAREN")
                    args = self.parse_args_rparen()
                    self.eat("RPAREN")
                    obj = MethodCall(obj=obj, method=member, args=args)
                else:
                    obj = MemberAccess(obj=obj, member=member)
            elif self.current_token()[0] == "LBRACKET":
                self.eat("LBRACKET")
                index = self.expression()
                self.eat("RBRACKET")
                obj = IndexAccess(target=obj, index=index)
            else:
                break
        return obj
