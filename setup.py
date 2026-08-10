from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="RAG Learning",
    version="0.1",
    author="prateek sharma",
    packages=find_packages(),
    install_requires = requirements,
)