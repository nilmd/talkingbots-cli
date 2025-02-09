from setuptools import setup, find_packages

setup(
    name="talkingbots-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ollama",
        "typer[all]",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "talkingbots-cli=src.main:app",
        ],
    },
    author="NilMD",
    description="A CLI tool that enables users to create conversations between multiple large language models",
    url="https://github.com/nilmd/talkingbots-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)