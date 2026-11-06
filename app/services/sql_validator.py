import re

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE"
}


def validate_sql(sql: str) -> bool:
    """Allow one read-only SELECT statement.

    This is a conservative lexical guard. The executor also uses a read-only
    database transaction because SQL text checks cannot prove a query safe.
    """
    if not isinstance(sql, str) or not sql.strip():
        return False

    # Remove comments and quoted strings/identifiers before checking tokens so
    # harmless text such as 'updated' does not trigger a false positive.
    cleaned = []
    i = 0
    quote = None
    while i < len(sql):
        char = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""
        if quote:
            if char == quote:
                if nxt == quote:
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if char in ("'", '"', '`'):
            quote = char
            cleaned.append(" ")
            i += 1
            continue
        if char == "-" and nxt == "-":
            end = sql.find("\n", i + 2)
            i = len(sql) if end < 0 else end + 1
            cleaned.append(" ")
            continue
        if char == "/" and nxt == "*":
            end = sql.find("*/", i + 2)
            if end < 0:
                return False
            cleaned.append(" ")
            i = end + 2
            continue
        cleaned.append(char)
        i += 1

    normalized = "".join(cleaned).strip().upper()
    if quote:
        return False
    # Permit at most one trailing terminator; reject statement chaining.
    if normalized.endswith(";"):
        normalized = normalized[:-1].rstrip()
    if ";" in normalized or not re.match(r"^SELECT\b", normalized):
        return False

    tokens = set(re.findall(r"[A-Z_][A-Z0-9_]*", normalized))
    if tokens & FORBIDDEN_KEYWORDS or "INTO" in tokens:
        return False

    return True
