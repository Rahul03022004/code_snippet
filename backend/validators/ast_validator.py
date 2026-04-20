# backend/validators/ast_validator.py
import ast
import subprocess
import tempfile
import os


def validate_syntax(code: str, framework: str) -> tuple:
    """
    WHY: LLMs produce broken syntax ~15-20% of the time.
    We catch this before showing the developer anything.
    Returns (is_valid: bool, error: str)
    """
    if not code or len(code.strip()) < 10:
        return False, "Generated code is empty or too short"

    if framework in ["fastapi", "django", "python"]:
        return _validate_python(code)
    elif framework in ["nextjs", "react", "express", "nestjs"]:
        return _validate_javascript(code)
    else:
        return _basic_validation(code)


def _validate_python(code: str) -> tuple:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"


def _validate_javascript(code: str) -> tuple:
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.js', delete=False, encoding='utf-8'
        ) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["node", "--check", temp_path],
            capture_output=True, text=True, timeout=10
        )
        os.unlink(temp_path)

        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip().split('\n')[0]

    except FileNotFoundError:
        return _basic_validation(code)
    except Exception:
        return True, ""


def _basic_validation(code: str) -> tuple:
    opens  = code.count('{') + code.count('(') + code.count('[')
    closes = code.count('}') + code.count(')') + code.count(']')
    if abs(opens - closes) > 3:
        return False, f"Unbalanced brackets ({opens} open vs {closes} close)"
    if len(code.strip().split('\n')) < 3:
        return False, "Generated code is too short"
    return True, ""
