from __future__ import annotations


def optional_import(path: str, symbol: str):
    try:
        module = __import__(path, fromlist=[symbol])
        return getattr(module, symbol)
    except Exception:
        return None


class LenaDependencies:

    LenaKernel = optional_import(
        "openjarvis.lena.kernel",
        "LenaKernel",
    )

    LenaSearchOrchestrator = optional_import(
        "openjarvis.lena.search_orchestrator",
        "LenaSearchOrchestrator",
    )

    LenaDesktopController = optional_import(
        "openjarvis.lena.desktop_controller",
        "LenaDesktopController",
    )

    LenaFileController = optional_import(
        "openjarvis.lena.file_controller",
        "LenaFileController",
    )
