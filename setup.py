import version_info
from distutils.core import setup
from distutils.extension import Extension


USE_CYTHON=True


if USE_CYTHON:
    try:
        from Cython.Distutils import build_ext
    except ImportError:
        if USE_CYTHON == 'auto':
            USE_CYTHON = False
        else:
            raise

cmdclass = {}
ext_modules = []

if USE_CYTHON:
    ext_modules.extend([
        Extension('photomosaic.matrix_math', ['cython_utils/matrix_math.pyx']),
    ])
    cmdclass.update({'build_ext': build_ext})
else:
    ext_modules.extend([
        Extension('photomosaic.matrix_math', ['cython_utils/matrix_math.c'])
    ])

setup(
    name='photomosaic',
    version=version_info.__version__,
    description='Convert an image into a mosaic of images',
    author='Ryan Van Voorhis',
    author_email='rjvanvoorhis@crimson.ua.edu',
    packages=['photomosaic', 'version_info'],
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    long_description=open('README.md').read(),
    license="MIT",
    classifiers=[
        'Development Status :: Beta',
        'Programming Language :: Python',
        'Programming Language :: Cython',
    ],
    keywords='image processing linear algebra'
)