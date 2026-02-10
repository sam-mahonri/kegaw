from setuptools import setup, find_packages
setup(
    name="kegaw",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'kegaw=kegaw.cli:main',
        ],
    },
    author="Sam Mahonri (aka Zhyrel)",
    description="Py-to-C-based compiler for Kegaw Language",
    python_requires='>=3.8',
)