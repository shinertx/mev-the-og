import ast, os

ALPHA_DIR = os.path.join('src', 'alpha')

REQUIRED_CALLS = ['update_pnl', 'update_drawdown']


def test_trading_functions_call_updates():
    for fn in os.listdir(ALPHA_DIR):
        if not fn.endswith('.py'):
            continue
        path = os.path.join(ALPHA_DIR, fn)
        tree = ast.parse(open(path).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('execute_'):
                body = ast.get_source_segment(open(path).read(), node)
                for call in REQUIRED_CALLS:
                    assert call in body, f"{fn}:{node.name} missing {call}"
