"""Architecture rules: Client (views) -> REST API -> modular monolith (strategic DDD).

Each context lives in its own package with controllers/application/domain/infrastructure
layers and publishes an ``api.py`` facade, the only way other contexts reach it. The client
is a separate app that talks to the API over HTTP. The test parses every module (including
imports inside functions) and fails if a dependency rule is broken, so the module boundaries
stay real and not just folders.
"""

import ast
from pathlib import Path

import pytest

MAIN = Path(__file__).resolve().parents[2] / "main"
CONTEXTS = ("identity", "profiles", "recruitment", "matching", "internships", "certification", "notifications")
FRAMEWORKS = ("flask", "flask_wtf", "flask_sqlalchemy", "flask_migrate", "sqlalchemy", "werkzeug")
BACKEND = CONTEXTS + ("bootstrap", "shared", "config", "run")


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
        assert "presentation" not in layers, f"{context}/presentation/ was renamed to controllers/"


def test_no_technical_layer_packages_remain_at_the_top_level():
    for legacy in ("application", "domain", "infrastructure", "frameworks"):
        assert not (MAIN / legacy).exists(), f"src/main/{legacy}/ should not exist"


def container_getter_owners():
    """Maps each DependencyContainer.get_* to the context of the classes it builds."""
    tree = ast.parse((MAIN / "bootstrap" / "dependencies.py").read_text(encoding="utf-8"))
    name_context = {
        alias.asname or alias.name: node.module.split(".")[0]
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in CONTEXTS
        for alias in node.names
    }
    container = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "DependencyContainer")
    owners = {}
    for method in container.body:
        if isinstance(method, ast.FunctionDef) and method.name.startswith("get_"):
            used = {name_context[n.id] for n in ast.walk(method) if isinstance(n, ast.Name) and n.id in name_context}
            assert len(used) == 1, f"{method.name} builds classes of {used or 'no context'}"
            owners[method.name] = used.pop()
    return owners


@pytest.mark.parametrize("context", CONTEXTS)
def test_controllers_only_use_their_own_getters_or_public_apis(context):
    owners = container_getter_owners()
    violations = []
    for path in modules_of(f"{context}/controllers"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "container"
                and node.attr.startswith("get_")
                and not node.attr.endswith("_api")
                and owners.get(node.attr) != context
            ):
                violations.append(f"{rel(path)}:{node.lineno} -> container.{node.attr}() of {owners.get(node.attr)}")
    assert violations == [], "use the other context's get_*_api() facade:\n" + "\n".join(violations)


def test_container_wires_services_with_facades_of_other_contexts():
    from bootstrap.app import create_app
    from bootstrap.dependencies import DependencyContainer

    container = DependencyContainer()
    violations = []
    with create_app("testing").app_context():
        for getter in sorted(n for n in dir(container) if n.startswith("get_") and n.endswith("_service")):
            service = getattr(container, getter)()
            own = type(service).__module__.split(".")[0]
            for attribute, value in vars(service).items():
                dependency_context = type(value).__module__.split(".")[0]
                if dependency_context in CONTEXTS and dependency_context != own and not type(value).__name__.endswith("Api"):
                    violations.append(f"{getter}: {attribute} is {type(value).__name__} from {dependency_context}")
    assert violations == [], "cross-context dependencies must be *Api facades:\n" + "\n".join(violations)


def test_client_and_backend_do_not_import_each_other():
    violations = [
        f"{rel(path)} -> {module}"
        for path in modules_of("client")
        for module in imported_modules(path)
        if module.split(".")[0] in BACKEND
    ]
    violations += [
        f"{rel(path)} -> {module}"
        for package in CONTEXTS + ("bootstrap", "shared")
        for path in modules_of(package)
        for module in imported_modules(path)
        if module.split(".")[0] == "client"
    ]
    violations += [f"{rel(p)} -> {m}" for p in (MAIN / "config.py", MAIN / "run.py") for m in imported_modules(p) if m.split(".")[0] == "client"]
    assert violations == [], "client and API only talk over HTTP:\n" + "\n".join(violations)


def test_views_and_assets_live_only_in_the_client():
    for folder in ("templates", "static"):
        assert not (MAIN / "bootstrap" / folder).exists(), f"bootstrap/{folder}/ belongs to the client"
        assert (MAIN / "client" / folder).is_dir(), f"client/{folder}/ is missing"
