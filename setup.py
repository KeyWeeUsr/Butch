from setuptools import setup, find_packages
from butch import get_version

KWARGS = dict(
    name="butch",
    version=get_version(),
    packages=find_packages(),
    package_data={
        "": ["*.txt", "*.bat", "*.out"]
    },
    include_package_data=True,
    exclude_package_data={
        "": ["*.pyc"]
    },
    entry_points={
        "console_scripts": [
            "butch = butch.__main__:main"
        ]
    }
)


if __name__ == "__main__":
    setup(**KWARGS)
