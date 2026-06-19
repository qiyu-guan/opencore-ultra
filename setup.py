#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="opencore-ultra",
    version="5.0.0",
    author="OpenCore Ultra Team",
    author_email="opencore@example.com",
    description="Professional Android Flashing Tool with 50+ Features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/你的用户名/opencore-ultra",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Embedded Systems",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.28.0",
        "pyinstaller>=5.0",
    ],
    entry_points={
        "console_scripts": [
            "opencore-ultra=opencore_tool:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
