"""API documentation generator."""

import itertools
import shutil
import textwrap
from importlib import import_module
from inspect import getmembers, isclass, isfunction
from pathlib import Path
from pkgutil import walk_packages
from types import FunctionType, ModuleType
from typing import Any, Optional, Union

API_META = (
    "# 0.5 - API\n"
    "# 2 - Release\n"
    "# 3 - Contributing\n"
    "# 5 - Template Page\n"
    "# 10 - Default\n"
    "search:\n"
    "  boost: 0.5"
)

MD_API_META = "---\n" + API_META + "\n---\n\n"


def _get_submodules(package_name: str) -> list[str]:
    """Get all submodules of a package.

    Args:
        package_name: The name of the package.

    Returns:
        A list of submodules.
    """
    try:
        # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
        m = import_module(package_name)
    except ModuleNotFoundError as e:
        raise e
    submodules = [
        info.name for info in walk_packages(m.__path__, prefix=f"{package_name}.")
    ]
    submodules = [
        x for x in submodules if not any(name.startswith("_") for name in x.split("."))
    ]
    return [package_name, *submodules]


def _import_submodules(module_name: str) -> Optional[list[ModuleType]]:
    def _import_module(name: str) -> Optional[ModuleType]:
        try:
            # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            return import_module(name)
        except Exception as e:
            print(f"Failed to import {name} with error: {e}")  # noqa: T201
            return None

    package_names = _get_submodules(module_name)
    modules = [_import_module(n) for n in package_names]
    return [m for m in modules if m is not None]


def _import_functions_and_classes(
    m: ModuleType,
) -> list[tuple[str, Union[FunctionType, type[Any]]]]:
    funcs_and_classes = [
        (x, y) for x, y in getmembers(m) if isfunction(y) or isclass(y)
    ]
    if hasattr(m, "__all__"):
        for t in m.__all__:
            obj = getattr(m, t)
            if isfunction(obj) or isclass(obj):
                funcs_and_classes.append((t, m.__name__ + "." + t))
    return funcs_and_classes


def _is_private(name: str) -> bool:
    parts = name.split(".")
    return any(part.startswith("_") for part in parts)


def _import_all_members(module_name: str) -> list[str]:
    submodules = _import_submodules(module_name)
    members: list[tuple[str, Union[FunctionType, type[Any]]]] = list(
        itertools.chain(*[_import_functions_and_classes(m) for m in submodules])
    )

    names = [
        y if isinstance(y, str) else f"{y.__module__}.{y.__name__}" for x, y in members
    ]
    names = [
        name for name in names if not _is_private(name) and name.startswith(module_name)
    ]
    return names


def _merge_lists(members: list[str], submodules: list[str]) -> list[str]:
    members_copy = members[:]
    for sm in submodules:
        for i, el in enumerate(members_copy):
            if el.startswith(sm):
                members_copy.insert(i, sm)
                break
    return members_copy


def _add_all_submodules(members: list[str]) -> list[str]:
    def _f(x: str) -> list[str]:
        xs = x.split(".")
        return [".".join(xs[:i]) + "." for i in range(1, len(xs))]

    def _get_sorting_key(item):
        y = item.split(".")
        z = [f"~{a}" for a in y[:-1]] + [y[-1]]
        return ".".join(z)

    submodules = list(set(itertools.chain(*[_f(x) for x in members])))
    members = _merge_lists(members, submodules)
    members = list(dict.fromkeys(members))
    return sorted(members, key=_get_sorting_key)


def _get_api_summary_item(x: str) -> str:
    xs = x.split(".")
    if x.endswith("."):
        indent = " " * (4 * (len(xs) - 1))
        return f"{indent}- {xs[-2]}"
    else:
        indent = " " * (4 * (len(xs)))
        return f"{indent}- [{xs[-1]}](api/{'/'.join(xs)}.md)"


def _get_api_summary(members: list[str]) -> str:
    return "\n".join([_get_api_summary_item(x) for x in members])


def _generate_api_doc(name: str, docs_path: Path) -> Path:
    xs = name.split(".")
    module_name = ".".join(xs[:-1])
    member_name = xs[-1]
    path = docs_path / f"{('/').join(xs)}.md"
    content = f"::: {module_name}.{member_name}\n"

    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(MD_API_META + content)

    return path


def _generate_api_docs(members: list[str], docs_path: Path) -> list[Path]:
    return [_generate_api_doc(x, docs_path) for x in members if not x.endswith(".")]


def _get_submodule_members(module_name: str) -> list[str]:
    """Get a list of all submodules contained within the module.

    Args:
        module_name: The name of the module to retrieve submodules from

    Returns:
        A list of submodule names within the module
    """
    members = _import_all_members(module_name)
    members_with_submodules = _add_all_submodules(members)
    members_with_submodules_str: list[str] = [
        x[:-1] if x.endswith(".") else x for x in members_with_submodules
    ]
    return members_with_submodules_str


def _load_submodules(
    module_name: str,
    members_with_submodules: list[str],
) -> list[Union[FunctionType, type[Any]]]:
    """Load the given submodules from the module.

    Args:
        module_name: The name of the module whose submodules to load
        members_with_submodules: A list of submodule names to load

    Returns:
        A list of imported submodule objects.
    """
    submodules = _import_submodules(module_name)
    members = itertools.chain(*map(_import_functions_and_classes, submodules))
    names = [
        y
        for _, y in members
        if (isinstance(y, str) and y in members_with_submodules)
        or (f"{y.__module__}.{y.__name__}" in members_with_submodules)
    ]
    return names


def _update_single_api_doc(
    symbol: Union[FunctionType, type[Any]], docs_path: Path, module_name: str
) -> None:
    en_docs_path = docs_path / "docs" / "en"

    if isinstance(symbol, str):
        class_name = symbol.split(".")[-1]
        module_name = ".".join(symbol.split(".")[:-1])
        # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
        obj = getattr(import_module(module_name), class_name)
        if obj.__module__.startswith(module_name):
            obj = symbol
        filename = symbol

    else:
        obj = symbol
        filename = f"{symbol.__module__}.{symbol.__name__}"

    content = "::: %s\n" % (
        obj if isinstance(obj, str) else f"{obj.__module__}.{obj.__qualname__}"
    )

    target_file_path = "/".join(filename.split(".")) + ".md"

    (en_docs_path / "api" / target_file_path).write_text(MD_API_META + content)


def _update_api_docs(
    symbols: list[Union[FunctionType, type[Any]]], docs_path: Path, module_name: str
) -> None:
    for symbol in symbols:
        _update_single_api_doc(
            symbol=symbol, docs_path=docs_path, module_name=module_name
        )


def _generate_api_docs_for_module(root_path: Path, module_name: str) -> str:
    """Generate API documentation for a module.

    Args:
        root_path: The root path of the project.
        module_name: The name of the module.

    Returns:
        A string containing the API documentation for the module.

    """
    members = _import_all_members(module_name)
    members_with_submodules = _add_all_submodules(members)
    api_summary = _get_api_summary(members_with_submodules)

    api_root = root_path / "docs" / "en" / "api"
    shutil.rmtree(api_root / module_name, ignore_errors=True)
    api_root.mkdir(parents=True, exist_ok=True)

    (api_root / ".meta.yml").write_text(API_META)

    _generate_api_docs(members_with_submodules, api_root)

    members_with_submodules = _get_submodule_members(module_name)
    symbols = _load_submodules(module_name, members_with_submodules)

    _update_api_docs(symbols, root_path, module_name)

    return api_summary


def get_navigation_template(docs_dir: Path) -> str:
    # read summary template from file
    navigation_template = (docs_dir / "navigation_template.txt").read_text()
    return navigation_template


def create_api_docs(
    root_path: Path,
    module: str,
    navigation_template: str,
) -> str:
    """Create API documentation for a module.

    Args:
        root_path: The root path of the project.
        module: The name of the module.
        navigation_template: The navigation template for the documentation.
    """
    docs_dir = root_path / "docs"

    api = _generate_api_docs_for_module(root_path, module)

    # add [API] to navigation template
    api = textwrap.indent(api, " " * 4)
    api = "    - API\n" + api

    summary = navigation_template.format(api=api, cli="{cli}")

    summary = "\n".join(filter(bool, (x.rstrip() for x in summary.split("\n"))))

    (docs_dir / "SUMMARY.md").write_text(summary)

    return summary


if __name__ == "__main__":
    root_path = Path(__file__).resolve().parent
    docs_dir = root_path / "docs"

    navigation_template = get_navigation_template(docs_dir)
    create_api_docs(root_path, "mcp_servers", navigation_template)
