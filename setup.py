import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cinefolders",
    version="0.0.9",
    author="Holland Gibson",
    author_email="cinefiles-hgibs@googlegroups.com",
    description="A utility for organizing a media folder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/hgibs/cinefolders',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
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
}
)