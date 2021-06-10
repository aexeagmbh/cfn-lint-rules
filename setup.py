from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="cfn_lint_ax",
    version="0.0.5",
    author="AX Semantics",
    author_email="infrastructure@ax-semantics.com",
    description="Rules for cfn lint.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aexeagmbh/cfn-lint-rules",
    project_urls={
        "Bug Tracker": "https://github.com/aexeagmbh/cfn-lint-rules/issues",
        "Source": "https://github.com/aexeagmbh/cfn-lint-rules",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=[
        "cfn_lint_ax",
        "cfn_lint_ax.rules",
    ],
    python_requires=">=3.8",
    install_requires=["cfn-lint >= 0.49"],
)
