from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cinefolders",
    version="0.1.0",
    author="Holland Gibson",
    author_email="cinefiles-hgibs@googlegroups.com",
    description="A utility for organizing a media folder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/hgibs/cinefolders',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires='>=3.6',
    install_requires=[
        'guessit>=3.1',
        'requests>=2.22',
        'pycountry>=19.8.18',
        'argparse>=1.4',
    ],
    entry_points = {
        'console_scripts': [
            'cinefolders = cinefolders.__main__:main'
        ],
    },
    extras_require = {
        'dev': ['twine','wheel','bump2version'],
        'test': ['codecov','pytest','pytest-pep8','pytest-cov',
                'pytest-console-scripts'],
    }
)