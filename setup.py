from setuptools import setup, find_packages
from butch import get_version

NAME = "butch"
KWARGS = dict(
    name=NAME,
    version=get_version(),
    description="The free Batch interpreter",
    author="Peter Badida",
    author_email="keyweeusr@gmail.com",
    url="https://github.com/KeyWeeUsr/Butch",
    download="https://github.com/KeyWeeUsr/Butch/releases",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        # "Development Status :: 6 - Mature",

        "Environment :: Console",

        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",

        "Natural Language :: English",
        "Natural Language :: Slovak",

        "Operating System :: OS Independent",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",

        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Interpreters",

        "Topic :: System",
        "Topic :: System :: Emulators",
        "Topic :: System :: Shells",
        "Topic :: System :: System Shells",
        "Topic :: Terminals",
        "Topic :: Terminals :: Terminal Emulators/X Terminals",
        "Topic :: Utilities",
        "Typing :: Typed"
    ],
    keywords=[
        "batch", "butch", "cmd", "shell", "interpreter", "console", "bat",
        "windows", "batchscript", "batch-script", "batchfile", "batch-file",
        "free", "foss"
    ],
    python_requires='>=3.6',
    packages=find_packages(),
    package_data={
        "": ["*.txt", "*.bat", "*.out"]
    },
    include_package_data=True,
    exclude_package_data={
        "": ["*.pyc"]
    },
    setup_requires=[
        "wheel"
    ],
    extras_require={
        "dev": [
            "pycodestyle>=2.7.0",
            "pylint>=2.9.3",
            "wemake-python-styleguide>=0.15.3"
        ],
        "release": [
            "setuptools", "wheel", "twine"
        ]
    },
    entry_points={
        "console_scripts": [
            f"{NAME} = {NAME}.__main__:main"
        ]
    }
)


if __name__ == "__main__":
    with open("README.rst") as file:
        KWARGS["long_description"] = file.read()
    setup(**KWARGS)
