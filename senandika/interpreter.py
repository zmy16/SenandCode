import operator


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class SenandikaClass:
    def __init__(self, name, parent, body):
        self.name = name
        self.parent = parent
        self.properties = {}
        self.methods = {}
        for item in body:
            if item[0] == "property":
                self.properties[item[1]] = item[2]
            elif item[0] == "function":
                self.methods[item[1]] = (item[2], item[3])


class SenandikaInstance:
    def __init__(self, cls, interpreter):
        self.cls = cls
        self.fields = {}
        chain = []
        curr = cls
        visited = set()
        while curr and curr.name not in visited:
            chain.insert(0, curr)
            visited.add(curr.name)
            curr = interpreter.classes.get(curr.parent) if curr.parent else None
        for c in chain:
            for name, expr in c.properties.items():
                self.fields[name] = interpreter.evaluate(expr)

    def get_method(self, name, interpreter):
        curr = self.cls
        visited = set()
        while curr and curr.name not in visited:
            visited.add(curr.name)
            if name in curr.methods:
                return curr.methods[name]
            curr = interpreter.classes.get(curr.parent) if curr.parent else None
        return None

    def __repr__(self):
        return f"<Objek {self.cls.name}>"


class Interpreter:
    def __init__(self, ast, variables=None, functions=None, classes=None):
        self.ast = ast
        self.variables = variables if variables is not None else {}
        self.functions = functions if functions is not None else {}
        self.classes = classes if classes is not None else {}
        self.this_context = None
        self.return_flag = False
        self.return_value = None
        self.break_flag = False
        self.continue_flag = False

    def interpret(self):
        self.execute(self.ast)

    def evaluate(self, node):
        if node is None:
            return None
        if not isinstance(node, (tuple, list)):
            return node
        kind = node[0]

        if kind == "number":
            return node[1]
        elif kind == "string":
            return node[1]
        elif kind == "boolean":
            return node[1]
        elif kind == "null":
            return None
        elif kind == "variable":
            name = node[1]
            if name in self.variables:
                return self.variables[name]
            raise RuntimeError(f"Variabel '{name}' tak kutemukan.")
        elif kind == "this":
            if self.this_context is None:
                raise RuntimeError("'diri' hanya bisa dipakai di dalam kelas.")
            return self.this_context
        elif kind == "member_get":
            obj = self.evaluate(node[1])
            if not isinstance(obj, SenandikaInstance):
                raise RuntimeError("Akses anggota hanya bisa pada objek.")
            member = node[2]
            if member in obj.fields:
                return obj.fields[member]
            raise RuntimeError(f"Anggota '{member}' tak ditemukan pada {obj.cls.name}.")
        elif kind == "member_call":
            obj = self.evaluate(node[1])
            method_name = node[2]
            args = [self.evaluate(a) for a in node[3]]
            if not isinstance(obj, SenandikaInstance):
                raise RuntimeError("Panggil metode hanya bisa pada objek.")
            method = obj.get_method(method_name, self)
            if not method:
                raise RuntimeError(f"Metode '{method_name}' tak ditemukan pada {obj.cls.name}.")
            params, body = method
            if len(args) != len(params):
                raise RuntimeError(f"Metode '{method_name}' butuh {len(params)} argumen, diberi {len(args)}.")
            local_vars = dict(zip(params, args))
            mi = Interpreter(body, local_vars, self.functions, self.classes)
            mi.this_context = obj
            mi.interpret()
            return mi.return_value
        elif kind == "new":
            cls_name = node[1]
            if cls_name not in self.classes:
                raise RuntimeError(f"Kelas '{cls_name}' tak ditemukan.")
            cls = self.classes[cls_name]
            instance = SenandikaInstance(cls, self)
            init = instance.get_method("lahir", self)
            if init:
                params, body = init
                args = [self.evaluate(a) for a in node[2]]
                if len(args) != len(params):
                    raise RuntimeError(f"Konstruktor '{cls_name}.lahir' butuh {len(params)} argumen, diberi {len(args)}.")
                local_vars = dict(zip(params, args))
                ci = Interpreter(body, local_vars, self.functions, self.classes)
                ci.this_context = instance
                ci.interpret()
            return instance
        elif kind == "array":
            return [self.evaluate(item) for item in node[1]]
        elif kind == "index_get":
            obj = self.evaluate(node[1])
            index = self.evaluate(node[2])
            if isinstance(obj, list):
                try:
                    return obj[int(index)]
                except IndexError:
                    raise RuntimeError(f"Index {index} di luar batas array (panjang: {len(obj)})")
            elif isinstance(obj, str):
                try:
                    return obj[int(index)]
                except IndexError:
                    raise RuntimeError(f"Index {index} di luar batas string (panjang: {len(obj)})")
            raise RuntimeError("Pengindeksan hanya bisa pada array atau string")
        elif kind == "binop":
            left_node = node[1]
            op = node[2]
            right_node = node[3]
            if op == "and":
                return self.evaluate(left_node) and self.evaluate(right_node)
            if op == "or":
                return self.evaluate(left_node) or self.evaluate(right_node)
            if op == "concat":
                return str(self.evaluate(left_node)) + str(self.evaluate(right_node))
            left = self.evaluate(left_node)
            right = self.evaluate(right_node)
            return self.apply_op(left, op, right)
        elif kind == "unop":
            op = node[1]
            val = self.evaluate(node[2])
            if op == "-":
                return -val
            if op == "not":
                return not val
            return val
        elif kind == "call":
            name = node[1]
            args = [self.evaluate(a) for a in node[2]]
            if name == "panjang":
                if len(args) != 1:
                    raise RuntimeError(f"panjang() butuh 1 argumen, diberi {len(args)}")
                val = args[0]
                if isinstance(val, (list, str)):
                    return len(val)
                raise RuntimeError(f"panjang() hanya bisa untuk array atau string, bukan {type(val).__name__}")
            if name not in self.functions:
                raise RuntimeError(f"Puisi '{name}' tak kutemukan.")
            params, body = self.functions[name]
            if len(args) != len(params):
                raise RuntimeError(f"Puisi '{name}' butuh {len(params)} argumen, diberi {len(args)}.")
            local_vars = dict(zip(params, args))
            fi = Interpreter(body, local_vars, self.functions, self.classes)
            fi.interpret()
            return fi.return_value
        return node

    def apply_op(self, left, op, right):
        ops = {
            "+": operator.add, "-": operator.sub, "*": operator.mul,
            "/": operator.truediv, "%": operator.mod,
            "//": lambda a, b: int(a) // int(b),
            "==": operator.eq, "!=": operator.ne,
            "<": operator.lt, ">": operator.gt,
            "<=": operator.le, ">=": operator.ge,
        }
        if op in ops:
            try:
                return ops[op](left, right)
            except Exception as e:
                raise RuntimeError(f"Operasi '{op}' gagal: {e}")
        raise RuntimeError(f"Operator '{op}' tak dikenal.")

    def execute(self, ast):
        if not ast:
            return
        for stmt in ast:
            if self.return_flag or self.break_flag or self.continue_flag:
                break
            kind = stmt[0]
            if kind in ("declare", "assign"):
                self.variables[stmt[1]] = self.evaluate(stmt[2])
            elif kind == "member_assign":
                target, expr = stmt[1], stmt[2]
                val = self.evaluate(expr)
                if target[0] == "member_get":
                    obj = self.evaluate(target[1])
                    if isinstance(obj, SenandikaInstance):
                        obj.fields[target[2]] = val
                    else:
                        raise RuntimeError("Pemberian anggota hanya pada objek.")
            elif kind == "index_assign":
                obj = self.evaluate(stmt[1])
                index = self.evaluate(stmt[2])
                val = self.evaluate(stmt[3])
                if isinstance(obj, list):
                    try:
                        obj[int(index)] = val
                    except IndexError:
                        raise RuntimeError(f"Index {index} di luar batas array (panjang: {len(obj)})")
                else:
                    raise RuntimeError("Pemberian index hanya bisa pada array")
            elif kind == "print":
                results = [self.evaluate(e) for e in stmt[1]]
                parts = []
                for v in results:
                    if isinstance(v, SenandikaInstance):
                        parts.append(f"<Objek {v.cls.name}>")
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
            elif kind == "input":
                var_name = stmt[1]
                prompt = stmt[2] if stmt[2] else f"Tulislah {var_name}: "
                val = input(prompt)
                if val and val.replace(".", "", 1).replace("-", "", 1).isdigit():
                    val = float(val) if "." in val else int(val)
                self.variables[var_name] = val
            elif kind == "if_chain":
                branches, else_body = stmt[1], stmt[2]
                handled = False
                for _, cond, body in branches:
                    if self.evaluate(cond):
                        self.execute(body)
                        handled = True
                        break
                if not handled and else_body:
                    self.execute(else_body)
            elif kind == "loop":
                var, start, end = stmt[1], stmt[2], stmt[3]
                step = self.evaluate(stmt[4]) if stmt[4] is not None else 1
                body = stmt[5]
                start_v = int(self.evaluate(start))
                end_v = int(self.evaluate(end))
                step_v = int(step)
                if step_v == 0:
                    raise RuntimeError("Langkah perulangan tidak boleh nol.")
                r = range(start_v, end_v + 1, step_v) if step_v > 0 else range(start_v, end_v - 1, step_v)
                for i in r:
                    self.variables[var] = i
                    self.execute(body)
                    if self.return_flag:
                        break
                    if self.break_flag:
                        self.break_flag = False
                        break
                    if self.continue_flag:
                        self.continue_flag = False
            elif kind == "while":
                cond, body = stmt[1], stmt[2]
                while self.evaluate(cond):
                    self.execute(body)
                    if self.return_flag:
                        break
                    if self.break_flag:
                        self.break_flag = False
                        break
                    if self.continue_flag:
                        self.continue_flag = False
            elif kind == "break":
                self.break_flag = True
            elif kind == "continue":
                self.continue_flag = True
            elif kind == "function":
                self.functions[stmt[1]] = (stmt[2], stmt[3])
            elif kind == "class":
                self.classes[stmt[1]] = SenandikaClass(stmt[1], stmt[2], stmt[3])
            elif kind == "try":
                try_body, cv, catch_body, fin_body = stmt[1], stmt[2], stmt[3], stmt[4]
                try:
                    self.execute(try_body)
                except (BreakException, ContinueException):
                    raise
                except Exception as e:
                    if catch_body:
                        old_vars = dict(self.variables)
                        self.variables[cv if cv else "kesalahan"] = str(e)
                        self.execute(catch_body)
                        self.variables = old_vars
                    else:
                        raise
                finally:
                    if fin_body:
                        self.execute(fin_body)
            elif kind == "throw":
                raise RuntimeError(str(self.evaluate(stmt[1])))
            elif kind == "return":
                self.return_value = self.evaluate(stmt[1])
                self.return_flag = True
            elif kind == "expr":
                self.evaluate(stmt[1])
