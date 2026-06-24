import operator

from senandika.syntax_analyzer import (
    Expression, Statement,
    NumberLiteral, StringLiteral, BooleanLiteral, NullLiteral,
    VariableRef, ArrayLiteral, IndexAccess,
    BinaryOp, UnaryOp, ThisRef,
    MemberAccess, MethodCall, FuncCall, NewExpr,
    DeclareStmt, AssignStmt, IndexAssignStmt, MemberAssignStmt,
    PrintStmt, InputStmt, IfStmt, ForStmt, WhileStmt,
    BreakStmt, ContinueStmt, FuncDef, ReturnStmt,
    ClassDef, TryStmt, ThrowStmt, ExprStmt,
)


class AlirHenti(Exception):
    pass


class AlirLangkau(Exception):
    pass


class WajahBlueprint:
    def __init__(self, name, parent, body):
        self.name = name
        self.parent = parent
        self.ciri = {}
        self.gerak = {}
        for item in body:
            if isinstance(item, tuple) and item[0] == "property":
                self.ciri[item[1]] = item[2]
            elif isinstance(item, FuncDef):
                self.gerak[item.name] = (item.params, item.body)


class WujudNyata:
    def __init__(self, blueprint, penghayal):
        self.biru = blueprint
        self.ladang = {}
        chain = []
        kini = blueprint
        pernah = set()
        while kini and kini.name not in pernah:
            chain.insert(0, kini)
            pernah.add(kini.name)
            kini = penghayal.klas.get(kini.parent) if kini.parent else None
        for c in chain:
            for name, expr in c.ciri.items():
                self.ladang[name] = penghayal.nilai(expr)

    def cari_gerak(self, name, penghayal):
        kini = self.biru
        pernah = set()
        while kini and kini.name not in pernah:
            pernah.add(kini.name)
            if name in kini.gerak:
                return kini.gerak[name]
            kini = penghayal.klas.get(kini.parent) if kini.parent else None
        return None

    def __repr__(self):
        return f"<{self.biru.name}>"


class Penghayal:
    def __init__(self, ast, variables=None, functions=None, classes=None):
        self.ast = ast
        self.lingkungan = variables if variables is not None else {}
        self.puisi = functions if functions is not None else {}
        self.klas = classes if classes is not None else {}
        self.si_ini = None
        bool_map = {True: "benar", False: "palsu", None: "hampa"}
        self.tanda_balik = False
        self.hasil_balik = None
        self.tanda_henti = False
        self.tanda_langkau = False

    def hayal(self):
        self.jalankan(self.ast)

    def nilai(self, node):
        if node is None:
            return None
        if not isinstance(node, Expression):
            return node

        if isinstance(node, NumberLiteral):
            return node.value
        elif isinstance(node, StringLiteral):
            return node.value
        elif isinstance(node, BooleanLiteral):
            return node.value
        elif isinstance(node, NullLiteral):
            return None
        elif isinstance(node, VariableRef):
            if node.name in self.lingkungan:
                return self.lingkungan[node.name]
            raise RuntimeError(f"'{node.name}' tak dikenal di sini.")
        elif isinstance(node, ThisRef):
            if self.si_ini is None:
                raise RuntimeError("'diri' hanya hadir di dalam kelas.")
            return self.si_ini
        elif isinstance(node, MemberAccess):
            obj = self.nilai(node.obj)
            if not isinstance(obj, WujudNyata):
                raise RuntimeError("Hanya objek yang punya anggota.")
            if node.member in obj.ladang:
                return obj.ladang[node.member]
            raise RuntimeError(f"'{node.member}' bukan milik {obj.biru.name}.")
        elif isinstance(node, MethodCall):
            obj = self.nilai(node.obj)
            if not isinstance(obj, WujudNyata):
                raise RuntimeError("Hanya objek yang punya metode.")
            method = obj.cari_gerak(node.method, self)
            if not method:
                raise RuntimeError(f"'{node.method}' bukan metode {obj.biru.name}.")
            params, body = method
            args = [self.nilai(a) for a in node.args]
            if len(args) != len(params):
                raise RuntimeError(f"'{node.method}' butuh {len(params)} argumen, diberi {len(args)}.")
            lokal = dict(zip(params, args))
            wi = Penghayal(body, lokal, self.puisi, self.klas)
            wi.si_ini = obj
            wi.hayal()
            return wi.hasil_balik
        elif isinstance(node, FuncCall):
            args = [self.nilai(a) for a in node.args]
            if node.name == "panjang":
                if len(args) != 1:
                    raise RuntimeError(f"panjang() perlu 1 argumen, diberi {len(args)}.")
                if isinstance(args[0], (list, str)):
                    return len(args[0])
                raise RuntimeError(f"panjang() hanya untuk larik atau aksara.")
            if node.name not in self.puisi:
                raise RuntimeError(f"Puisi '{node.name}' tak tergubah.")
            params, body = self.puisi[node.name]
            if len(args) != len(params):
                raise RuntimeError(f"'{node.name}' butuh {len(params)} argumen, diberi {len(args)}.")
            lokal = dict(zip(params, args))
            wi = Penghayal(body, lokal, self.puisi, self.klas)
            wi.hayal()
            return wi.hasil_balik
        elif isinstance(node, NewExpr):
            if node.class_name not in self.klas:
                raise RuntimeError(f"Wajah '{node.class_name}' tak terlukis.")
            wujud = self.klas[node.class_name]
            instance = WujudNyata(wujud, self)
            init = instance.cari_gerak("lahir", self)
            if init:
                params, body = init
                args = [self.nilai(a) for a in node.args]
                if len(args) != len(params):
                    raise RuntimeError(f"Lahir {node.class_name} butuh {len(params)} argumen, diberi {len(args)}.")
                lokal = dict(zip(params, args))
                wi = Penghayal(body, lokal, self.puisi, self.klas)
                wi.si_ini = instance
                wi.hayal()
            return instance
        elif isinstance(node, ArrayLiteral):
            return [self.nilai(item) for item in node.items]
        elif isinstance(node, IndexAccess):
            obj = self.nilai(node.target)
            index = self.nilai(node.index)
            if isinstance(obj, list):
                try:
                    return obj[int(index)]
                except IndexError:
                    raise RuntimeError(f"Index {index} melebihi panjang larik ({len(obj)}).")
            elif isinstance(obj, str):
                try:
                    return obj[int(index)]
                except IndexError:
                    raise RuntimeError(f"Index {index} melebihi panjang aksara ({len(obj)}).")
            raise RuntimeError("Hanya larik atau aksara bisa diindeks.")
        elif isinstance(node, BinaryOp):
            if node.operator == "and":
                return self.nilai(node.left) and self.nilai(node.right)
            elif node.operator == "or":
                return self.nilai(node.left) or self.nilai(node.right)
            elif node.operator == "concat":
                return str(self.nilai(node.left)) + str(self.nilai(node.right))
            kiri = self.nilai(node.left)
            kanan = self.nilai(node.right)
            return self.gabung(kiri, node.operator, kanan)
        elif isinstance(node, UnaryOp):
            val = self.nilai(node.operand)
            if node.operator == "-":
                return -val
            elif node.operator == "not":
                return not val
            return val
        return node

    def gabung(self, left, op, right):
        daptar = {
            "+": operator.add, "-": operator.sub, "*": operator.mul,
            "/": operator.truediv, "%": operator.mod,
            "//": lambda a, b: int(a) // int(b),
            "==": operator.eq, "!=": operator.ne,
            "<": operator.lt, ">": operator.gt,
            "<=": operator.le, ">=": operator.ge,
        }
        if op in daptar:
            try:
                return daptar[op](left, right)
            except Exception as e:
                raise RuntimeError(f"'{op}' gagal: {e}")
        raise RuntimeError(f"'{op}' bukan operator.")

    def jalankan(self, tree):
        if not tree:
            return
        for stmt in tree:
            if self.tanda_balik or self.tanda_henti or self.tanda_langkau:
                break

            if isinstance(stmt, DeclareStmt):
                self.lingkungan[stmt.name] = self.nilai(stmt.value)
            elif isinstance(stmt, AssignStmt):
                self.lingkungan[stmt.name] = self.nilai(stmt.value)
            elif isinstance(stmt, MemberAssignStmt):
                val = self.nilai(stmt.value)
                if stmt.target_name == "this" and self.si_ini is not None:
                    self.si_ini.ladang[stmt.member] = val
                else:
                    obj = self.lingkungan.get(stmt.target_name)
                    if isinstance(obj, WujudNyata):
                        obj.ladang[stmt.member] = val
                    else:
                        raise RuntimeError(f"'{stmt.target_name}' bukan objek.")
            elif isinstance(stmt, IndexAssignStmt):
                obj = self.nilai(stmt.target)
                index = self.nilai(stmt.index)
                val = self.nilai(stmt.value)
                if isinstance(obj, list):
                    try:
                        obj[int(index)] = val
                    except IndexError:
                        raise RuntimeError(f"Index {index} melewati batas (panjang: {len(obj)}).")
                else:
                    raise RuntimeError("Hanya larik yang bisa diindeks-assign.")
            elif isinstance(stmt, PrintStmt):
                results = [self.nilai(e) for e in stmt.expressions]
                parts = []
                for v in results:
                    if isinstance(v, WujudNyata):
                        parts.append(repr(v))
                    elif v is True:
                        parts.append("benar")
                    elif v is False:
                        parts.append("palsu")
                    elif v is None:
                        parts.append("hampa")
                    elif isinstance(v, list):
                        parts.append("[" + ", ".join(str(item) for item in v) + "]")
                    else:
                        parts.append(str(v))
                print(" ".join(parts))
            elif isinstance(stmt, InputStmt):
                prompt = stmt.prompt if stmt.prompt else f"{stmt.variable}: "
                val = input(prompt)
                if val and val.replace(".", "", 1).replace("-", "", 1).isdigit():
                    val = float(val) if "." in val else int(val)
                self.lingkungan[stmt.variable] = val
            elif isinstance(stmt, IfStmt):
                done = False
                for cond, body in stmt.branches:
                    if self.nilai(cond):
                        self.jalankan(body)
                        done = True
                        break
                if not done and stmt.else_body:
                    self.jalankan(stmt.else_body)
            elif isinstance(stmt, ForStmt):
                start = int(self.nilai(stmt.start))
                end = int(self.nilai(stmt.end))
                for i in range(start, end + 1):
                    self.lingkungan[stmt.variable] = i
                    self.jalankan(stmt.body)
                    if self.tanda_balik:
                        break
                    if self.tanda_henti:
                        self.tanda_henti = False
                        break
                    if self.tanda_langkau:
                        self.tanda_langkau = False
            elif isinstance(stmt, WhileStmt):
                while self.nilai(stmt.condition):
                    self.jalankan(stmt.body)
                    if self.tanda_balik:
                        break
                    if self.tanda_henti:
                        self.tanda_henti = False
                        break
                    if self.tanda_langkau:
                        self.tanda_langkau = False
            elif isinstance(stmt, BreakStmt):
                self.tanda_henti = True
            elif isinstance(stmt, ContinueStmt):
                self.tanda_langkau = True
            elif isinstance(stmt, FuncDef):
                self.puisi[stmt.name] = (stmt.params, stmt.body)
            elif isinstance(stmt, ClassDef):
                self.klas[stmt.name] = WajahBlueprint(stmt.name, stmt.parent, stmt.body)
            elif isinstance(stmt, ReturnStmt):
                self.hasil_balik = self.nilai(stmt.value)
                self.tanda_balik = True
            elif isinstance(stmt, TryStmt):
                try:
                    self.jalankan(stmt.try_body)
                except (AlirHenti, AlirLangkau):
                    raise
                except Exception as e:
                    if stmt.catch_body:
                        lama = dict(self.lingkungan)
                        self.lingkungan[stmt.catch_var if stmt.catch_var else "kesalahan"] = str(e)
                        self.jalankan(stmt.catch_body)
                        self.lingkungan = lama
                    else:
                        raise
                finally:
                    if stmt.finally_body:
                        self.jalankan(stmt.finally_body)
            elif isinstance(stmt, ThrowStmt):
                raise RuntimeError(str(self.nilai(stmt.value)))
            elif isinstance(stmt, ExprStmt):
                self.nilai(stmt.expr)
