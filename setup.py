from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="network-discovery",
    version="0.1.0",
    author="HTB Network Discovery Team",
    description="Cisco network discovery and visualization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "netmiko>=4.3.0",
        "textfsm>=1.1.3",
        "networkx>=3.1",
        "sqlalchemy>=2.0.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "network-discovery=cli.main:app",
        ],
    },
)
