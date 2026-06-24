import re
from bisect import bisect_right


class Lexer:
    def __init__(self, code: str):
        self.code = code.strip()

    def tokenize(self):
        code = self.code
        # Preserve strings before multi-word keyword replacement
        strings = []
        def _save_str(m):
            strings.append(m.group(0))
            return f"\0STR{len(strings)-1}\0"
        code = re.sub(r'"[^"]*"', _save_str, code)
        # Handle multi-word keywords first
        code = code.replace("atau jika", "ATAUJIKA")
        code = code.replace("jika tidak", "JIKATIDAK")
        # Restore strings
        for i, s in enumerate(strings):
            code = code.replace(f"\0STR{i}\0", s)

        token_specs = [
            ("COMMENT",      r"//.*"),
            ("KEYWORD_DECLARE", r"\bsimpan\b"),
            ("KEYWORD_IN",    r"\bdalam\b"),
            ("KEYWORD_PRINT", r"\blukiskan\b"),
            ("KEYWORD_CONCAT", r"\blalu\b"),
            ("KEYWORD_IF",    r"\bseandainya\b"),
            ("KEYWORD_ELIF",  r"\bATAUJIKA\b"),
            ("KEYWORD_ELSE",  r"\bJIKATIDAK\b"),
            ("KEYWORD_FOR",   r"\buntuk\b"),
            ("KEYWORD_TO",    r"\bsampai\b"),
            ("KEYWORD_STEP",  r"\blangkah\b"),
            ("KEYWORD_DO",    r"\blakukan\b"),
            ("KEYWORD_WHILE", r"\bselagi\b"),
            ("KEYWORD_FUNC",  r"\bpuisi\b"),
            ("KEYWORD_RETURN", r"\bkembalikan\b"),
            ("KEYWORD_INPUT", r"\bdengarkan\b"),
            ("KEYWORD_TRUE",  r"\bbenar\b"),
            ("KEYWORD_FALSE", r"\bpalsu\b"),
            ("KEYWORD_NULL",  r"\bhampa\b"),
            ("KEYWORD_AND",   r"\bdan\b"),
            ("KEYWORD_OR",    r"\batau\b"),
            ("KEYWORD_NOT",   r"\bbukan\b"),
            ("KEYWORD_TRY",   r"\bcoba\b"),
            ("KEYWORD_CATCH", r"\braih\b"),
            ("KEYWORD_FINALLY", r"\bakhirnya\b"),
            ("KEYWORD_THROW", r"\blemparkan\b"),
            ("KEYWORD_CLASS", r"\bwajah\b"),
            ("KEYWORD_THIS",  r"\bdiri\b"),
            ("KEYWORD_NEW",   r"\bciptakan\b"),
            ("KEYWORD_EXTENDS", r"\bwarisi\b"),
            ("KEYWORD_END",   r"\bselesai\b"),
            ("KEYWORD_BREAK", r"\bhening\b"),
            ("KEYWORD_CONTINUE", r"\bsambung\b"),
            ("NUMBER",       r"\b\d+(\.\d+)?\b"),
            ("STRING",       r'\"[^\"]*\"'),
            ("VARIABLE",     r"[a-zA-Z_][a-zA-Z_0-9]*"),
            ("OPERATOR",     r"==|!=|<=|>=|[+\-*/%=<>]"),
            ("DOT",          r"\."),
            ("COLON",        r":"),
            ("LPAREN",       r"\("),
            ("RPAREN",       r"\)"),
            ("LBRACKET",     r"\["),
            ("RBRACKET",     r"\]"),
            ("COMMA",        r","),
            ("SEMICOLON",    r";"),
            ("SKIP",         r"[ \t\r\n]+"),
            ("MISMATCH",     r"."),
        ]

        regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specs)
        pattern = re.compile(regex)

        # Substitutions above (multi-word keywords, string placeholders) must
        # not add or remove newlines, or line/col tracking breaks.
        line_starts = [0]
        for i, ch in enumerate(code):
            if ch == '\n':
                line_starts.append(i + 1)

        def _line_col(offset):
            line_idx = bisect_right(line_starts, offset) - 1
            return line_idx + 1, offset - line_starts[line_idx] + 1

        for match in pattern.finditer(code):
            kind = match.lastgroup
            value = match.group()
            if kind == "SKIP" or kind == "COMMENT":
                continue
            elif kind == "MISMATCH":
                line, col = _line_col(match.start())
                raise SyntaxError(
                    f"Karakter tak dikenal: '{value}' di baris {line}, kolom {col}"
                )
            line, col = _line_col(match.start())
            yield (kind, value, line, col)
