"""Dependency resolver"""
import os
import tokenize
from tokenize import NAME, NEWLINE
from typing import List, Set

# NOTE: direct imports have been turned off due to duplicate file names
# this prevents us from precisely knowing which file to include
ENABLE_DIRECT_IMPORTS = False


def _detect_dependencies(file_name: str) -> List[List[str]]:
    """Detect import statements in source files"""
    dependencies: List[List[str]] = []
    with tokenize.open(file_name) as f:
        tokens = tokenize.generate_tokens(f.readline)
        while True:
            try:
                token = next(tokens)
            except StopIteration:
                break
            if token.type == NAME and "from" == token.string:
                package_path = ""
                module_name: str
                while True:
                    token = next(tokens)
                    if "import" == token.string:
                        break
                    package_path += token.string
                module_count = len(token.line.split(","))
                package_path = package_path.split(".")
                for _ in range(module_count):
                    token = next(tokens)
                    if token.string == ",":
                        token = next(tokens)
                    module_name = token.string
                    dependencies.append(package_path + [module_name])
            if (
                ENABLE_DIRECT_IMPORTS
                and token.type == NAME
                and "import" in token.string
            ):
                module_name: str = ""
                while True:
                    token = next(tokens)
                    if token.type == NEWLINE or "as" in token.string:
                        break
                    module_name += token.string
                dependencies.append(module_name.split("."))
    print('Detected dependencies in file:', file_name, dependencies)
    return dependencies


def _resolve_paths(dependencies: List[List[str]]) -> Set[str]:
    """Check if the file is found in the local folder"""
    resolved_paths: Set[str] = set()
    for dependency in dependencies:
        if len(dependency) == 1:
            dir_contents = os.listdir(".")
            for content in dir_contents:
                if not os.path.isfile(content):
                    sub_dir_content = os.listdir(content)
                    line = "".join(dependency) + ".py"
                    if line in sub_dir_content:
                        resolved_paths.add(f"{content}/{line}")
        else:
            # TODO: add support for relative imports
            # and directly imported objects
            module_path = "/".join(dependency) + ".py"
            result = os.path.exists(module_path)
            if result:
                resolved_paths.add(module_path)

    return resolved_paths


def _resolve(file_name: str) -> Set[str]:
    dependencies = _detect_dependencies(file_name)
    return _resolve_paths(dependencies)


def resolve_dependencies(file_name: str) -> Set[str]:
    """Resolve dependencies of the main file recursively"""
    detected_files: Set[str] = set()
    traversed: Set[str] = set()
    remaining: Set[str] = set()

    def _run_resolver(file_location: str) -> None:
        deps = _resolve(file_location)
        traversed.add(file_location)
        detected_files.update(deps)
        remaining.update(deps - traversed)

    remaining.add(file_name)

    while len(remaining) > 0:
        path = remaining.pop()
        _run_resolver(path)

    return detected_files
