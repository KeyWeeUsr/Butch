from setuptools import setup, find_packages
from butch import get_version

KWARGS = dict(
    name="butch",
    version=get_version(),
    packages=find_packages()
)


if __name__ == "__main__":
    setup(**KWARGS)
