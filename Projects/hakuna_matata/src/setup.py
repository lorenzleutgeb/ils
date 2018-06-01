import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hakuna_matata",
    version="0.0.3",
    author="Lorenz Leutgeb",
    author_email="lorenz@leutgeb.xyz",
    description="A logic-based agent that plays Hunt the Wumpus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lorenzleutgeb/ils",
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': [
        'hakuna_matata = hakuna_matata.cli.__main__',
    ]},
    license='MIT',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
    ),
)
