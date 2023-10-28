__version__ = "0.0.1"
from setuptools import setup

setup(
    name="pygmc",
    version=__version__,
    url="https://github.com/Wikilicious/pygmc",
    author="Thomaz",
    license="MIT",
    python_requires=">=3.6",
    install_requires=["pyserial>=3.4"],
)
