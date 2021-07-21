from setuptools import setup
from butch import get_version

KWARGS = dict(
    name="butch",
    version=get_version()
)


if __name__ == "__main__":
    setup(**KWARGS)
