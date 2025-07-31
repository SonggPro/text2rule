#!/usr/bin/env python3
"""
Text2Rule: 医疗文本到规则转换框架
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="text2rule",
    version="1.0.0",
    author="Text2Rule Contributors",
    author_email="your-email@example.com",
    description="基于大语言模型的医疗文本到规则转换框架",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/text2rule",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/text2rule/issues",
        "Documentation": "https://github.com/your-username/text2rule#readme",
        "Source Code": "https://github.com/your-username/text2rule",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "text2rule-generate=framework.function_generator:main",
            "text2rule-execute=framework.function_executor:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.jsonl", "*.csv"],
    },
    keywords=[
        "medical",
        "quality-control",
        "nlp",
        "llm",
        "rule-generation",
        "healthcare",
        "artificial-intelligence",
        "machine-learning",
    ],
    platforms=["any"],
    license="MIT",
    zip_safe=False,
) 