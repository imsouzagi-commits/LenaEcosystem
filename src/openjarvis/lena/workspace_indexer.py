from __future__ import annotations

import os
from pathlib import Path

from openjarvis.lena.workspace_center import LenaWorkspaceCenter


class LenaWorkspaceIndexer:
    MAX_DEPTH = 4
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

    IGNORED_DIRS = {
        ".git",
        ".venv",
        "__pycache__",
        "pycache",
        "node_modules",
        "logs",
        "memory",
        "cache",
        "delivery",
        "snapshots",
        "exports",
        "reports",
        "temp",
        ".pytest_cache",
    }

    @classmethod
    def _root(cls) -> Path:
        return LenaWorkspaceCenter.ROOT.resolve()

    @classmethod
    def _depth(cls, path: Path, root: Path) -> int:
        try:
            return len(path.relative_to(root).parts)
        except ValueError:
            return cls.MAX_DEPTH + 1

    @classmethod
    def _ignore_dir(cls, name: str) -> bool:
        return name.startswith(".") or name in cls.IGNORED_DIRS

    @classmethod
    def _ignore_file(cls, file_name: str, full_path: Path) -> bool:
        if file_name.startswith("."):
            return True

        try:
            return full_path.stat().st_size > cls.MAX_FILE_SIZE_BYTES
        except OSError:
            return True

    @staticmethod
    def build_index() -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        root_path = LenaWorkspaceIndexer._root()

        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)
            current_depth = LenaWorkspaceIndexer._depth(current_path, root_path)

            dirs[:] = [
                directory
                for directory in dirs
                if current_depth < LenaWorkspaceIndexer.MAX_DEPTH
                and not LenaWorkspaceIndexer._ignore_dir(directory)
            ]

            relevant_files = []
            for file_name in files:
                full_path = current_path / file_name
                if LenaWorkspaceIndexer._ignore_file(file_name, full_path):
                    continue
                relevant_files.append(str(full_path))

            if relevant_files:
                index[str(current_path)] = relevant_files

        return index

    @staticmethod
    def build_index_light() -> dict[str, int]:
        total_dirs = 0
        total_files = 0
        root_path = LenaWorkspaceIndexer._root()

        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)
            current_depth = LenaWorkspaceIndexer._depth(current_path, root_path)

            dirs[:] = [
                directory
                for directory in dirs
                if current_depth < LenaWorkspaceIndexer.MAX_DEPTH
                and not LenaWorkspaceIndexer._ignore_dir(directory)
            ]

            total_dirs += len(dirs)

            for file_name in files:
                full_path = current_path / file_name
                if LenaWorkspaceIndexer._ignore_file(file_name, full_path):
                    continue
                total_files += 1

        return {
            "directories": total_dirs,
            "files": total_files,
        }
