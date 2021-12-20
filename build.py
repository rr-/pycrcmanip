import multiprocessing
import sys
from pathlib import Path

from Cython.Build import cythonize
from Cython.Distutils.build_ext import new_build_ext as cython_build_ext
from setuptools import Distribution, Extension

SOURCE_DIR = Path("crcmanip")
BUILD_DIR = Path("cython_build")


def get_extension_modules() -> list[Extension]:
    """Collect all .py files and construct Setuptools Extensions"""
    extension_modules: list[Extension] = []
    for c_file in SOURCE_DIR.rglob("*.c"):
        module_path = c_file.with_suffix("")
        module_path = str(module_path).replace("/", ".")
        extension_module = Extension(name=module_path, sources=[str(c_file)])
        extension_module._needs_stub = False
        extension_modules.append(extension_module)
    return extension_modules


def cythonize_helper(extension_modules: list[Extension]) -> list[Extension]:
    """Cythonize all Python extensions"""

    return cythonize(
        module_list=extension_modules,
        build_dir=BUILD_DIR,
        annotate=False,
        nthreads=multiprocessing.cpu_count() * 2,
        compiler_directives={"language_level": "3"},
        force=True,
    )


extension_modules = cythonize_helper(get_extension_modules())

distribution = Distribution(
    {
        "ext_modules": extension_modules,
        "cmdclass": {
            "build_ext": cython_build_ext,
        },
    }
)

# Grab the build_ext command and copy all files back to source dir.
# Done so Poetry grabs the files during the next step in its build.
cmd = distribution.reinitialize_command("build_ext")
cmd.inplace = 1

distribution.run_command("build_ext")
