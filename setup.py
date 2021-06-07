from setuptools import setup

setup(
    name="cfn_lint_ax",
    version="0.0.1",
    url="https://github.com/aexeagmbh/cfn-lint-rules",
    description="Rules for cfn lint.",
    packages=[
        "cfn_lint_ax",
        "cfn_lint_ax.rules",
    ],
    install_requires=["cfn-lint"],
)
