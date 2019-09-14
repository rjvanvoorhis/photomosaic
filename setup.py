from setuptools import find_packages
from distutils.core import setup
from distutils.extension import Extension
from version_info import __author__, __version__


USE_CYTHON=True
if USE_CYTHON:
    try:
        from Cython.Distutils import build_ext
    except (ImportError, ModuleNotFoundError):
        if USE_CYTHON == 'auto':
            USE_CYTHON = False
        else:
            raise

cmdclass = {}
ext_modules = []

if USE_CYTHON:
    ext_modules.extend([
        Extension('photomosaic.matrix_math', ['src/matrix_math.pyx']),
    ])
    cmdclass.update({'build_ext': build_ext})
else:
    ext_modules.extend([
        Extension('photomosaic.matrix_math', ['src/matrix_math.c'])
    ])

setup(
    name='photomosaic',
    version=__version__,
    author=__author__,
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    packages=['photomosaic', 'photomosaic.version_info'],
    package_dir={'photomosaic': 'photomosaic', 'photomosaic.version_info': 'version_info'},
    # package_dir={'photomosaic': 'photomosaic', 'photomosaic.dist_info': 'dist_info'},
    entry_points={
        'console_scripts': [
            'mosaicfy = scripts.cli:cli'
        ]
    },
    include_package_data=True,
    install_requires=[
        'cython',
        'numpy',
        'click',
        'Pillow'
    ]
)
