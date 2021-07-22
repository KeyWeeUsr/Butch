from setuptools import setup, find_packages
from butch import get_version

NAME = "butch"
KWARGS = dict(
    name=NAME,
    version=get_version(),
    description="The free Batch interpreter",
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
