"""Architecture rules of the bounded-context design (strategic DDD).

Each context lives in its own package with domain/application/infrastructure/controllers
layers. The test parses every module (including imports inside functions) and fails if a
dependency rule is broken, so the module boundaries stay real and not just folders.
"""

import ast
from pathlib import Path

import pytest

MAIN = Path(__file__).resolve().parents[2] / "main"
CONTEXTS = ("identity", "profiles", "recruitment", "matching", "internships", "certification", "notifications")
FRAMEWORKS = ("flask", "flask_wtf", "flask_sqlalchemy", "flask_migrate", "sqlalchemy", "werkzeug")


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module


def modules_of(package):
    return sorted((MAIN / package).rglob("*.py"))


def rel(path):
    return path.relative_to(MAIN).as_posix()


@pytest.mark.parametrize("context", CONTEXTS)
def test_context_only_uses_other_contexts_through_their_api(context):
    violations = []
    for path in modules_of(context):
        for module in imported_modules(path):
            top = module.split(".")[0]
            if top in CONTEXTS and top != context and module != f"{top}.api":
                violations.append(f"{rel(path)} -> {module}")
            if top == "bootstrap" and not (
                module == "bootstrap.dependencies" and "/controllers/" in f"/{rel(path)}"
            ):
                violations.append(f"{rel(path)} -> {module}")
    assert violations == [], "imports that cross a context boundary:\n" + "\n".join(violations)


@pytest.mark.parametrize("context", CONTEXTS)
def test_domain_layer_is_independent_of_outer_layers_and_frameworks(context):
    violations = []
    for path in modules_of(f"{context}/domain"):
        for module in imported_modules(path):
            parts = module.split(".")
            if parts[0] in FRAMEWORKS or (
                parts[0] == context and len(parts) > 1 and parts[1] in ("application", "infrastructure", "controllers")
            ):
                violations.append(f"{rel(path)} -> {module}")
    assert violations == [], "the domain must not depend on outer layers:\n" + "\n".join(violations)


def test_shared_kernel_does_not_depend_on_contexts_or_bootstrap():
    violations = [
        f"{rel(path)} -> {module}"
        for path in modules_of("shared")
        for module in imported_modules(path)
        if module.split(".")[0] in CONTEXTS + ("bootstrap",)
    ]
    assert violations == [], "\n".join(violations)


def test_every_context_has_the_same_layered_layout():
    for context in CONTEXTS:
        layers = {p.name for p in (MAIN / context).iterdir() if p.is_dir() and p.name != "__pycache__"}
        assert {"domain", "application", "infrastructure", "controllers"} <= layers, context


def test_no_technical_layer_packages_remain_at_the_top_level():
    for legacy in ("application", "domain", "infrastructure", "frameworks"):
        assert not (MAIN / legacy).exists(), f"src/main/{legacy}/ should not exist"
