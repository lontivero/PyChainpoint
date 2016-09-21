import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
install_requires = [
    "merkletools==1.0.0"
]

setup(
    name='chainpoint',
    version='1.0.0',
    description='Chainpoint proof of existance library',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    url='https://github.com/lontivero/pychainpoint',
    author='Lucas Ontivero',
    keywords='proof of existance, blockchain, merkle tree',
    license="MIT",
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    install_requires=install_requires
)
