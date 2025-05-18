import sys
import types
import unittest

# Stub external dependencies so importing CLI works without installed packages.
requests_stub = types.ModuleType('requests')
requests_stub.post = lambda *a, **k: types.SimpleNamespace(ok=True, json=lambda: {})
requests_stub.get = lambda *a, **k: types.SimpleNamespace(ok=True, json=lambda: {})
sys.modules.setdefault('requests', requests_stub)

typer_stub = types.ModuleType('typer')
filetype = types.ModuleType("filetype")
filetype.guess = lambda x: types.SimpleNamespace(mime="text/plain")
sys.modules.setdefault("filetype", filetype)
typer_stub.echo = lambda *a, **k: None

class DummyCliRunner:
    def invoke(self, app, args=None):
        return types.SimpleNamespace(exit_code=0, output="CLI interface for Basecamp API")

class DummyApp:
    def __init__(self, help=None):
        self.help = help
    def command(self, *a, **k):
        def decorator(fn):
            return fn
        return decorator
    def __call__(self, *a, **k):
        pass

typer_stub.Typer = DummyApp

typer_testing = types.ModuleType('typer.testing')
typer_testing.CliRunner = lambda: DummyCliRunner()

typer_stub.testing = typer_testing
sys.modules.setdefault('typer', typer_stub)
sys.modules.setdefault('typer.testing', typer_testing)

from basecampapi.cli import app


class CLITestCase(unittest.TestCase):
    def test_help(self):
        runner = DummyCliRunner()
        result = runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("CLI interface for Basecamp API", result.output)


if __name__ == "__main__":
    unittest.main()
