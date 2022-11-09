import glob
from pathlib import Path
from typing import Any, Dict

import cachesim.backend
from pybind11.setup_helpers import Pybind11Extension, build_ext


def build(setup_kwargs: Dict[str, Any]) -> None:
    cachesim_backend_file = Path(cachesim.backend.__file__)

    ext_modules = [
        Pybind11Extension(
            "__alex_core",
            ["core/main.cpp"],
            include_dirs=[str(cachesim_backend_file.parent), "core/"],
            library_dirs=[str(cachesim_backend_file.parent)],
            runtime_library_dirs=[str(cachesim_backend_file.parent)],
            libraries=[f":{cachesim_backend_file.name}"],
            cxx_std=20,
            extra_compile_args=["-Wall", "-Wextra", "-Werror", "-mbmi2"],
            depends=glob.glob("core/**/*.hpp", recursive=True),
        ),
    ]

    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "cmdclass": {"build_ext": build_ext},
            "zip_safe": False,
        }
    )
