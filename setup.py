from pathlib import Path

from setuptools import find_packages, setup

# Read the contents of README file
source_root = Path(".")
with (source_root / "README.md").open(encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
with (source_root / "requirements.txt").open(encoding="utf8") as f:
    requirements = f.readlines()

with (source_root / "requirements_dev.txt").open(encoding="utf8") as f:
    dev_requirements = f.readlines()

with (source_root / "requirements_test.txt").open(encoding="utf8") as f:
    test_requirements = f.readlines()

extras_requires = {"all": requirements + test_requirements + dev_requirements}

setup(
    name="reverie",
    version="0.0.1",
    url="https://github.com/ieaves/reverie",
    description="Fantasy football draft utilities ",
    author="Ian Eaves",
    author_email="ian.k.eaves@gmail.com",
    package_data={"reverie": ["py.typed"]},
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
    include_package_data=True,
    extras_require=extras_requires,
    tests_require=test_requirements,
    python_requires=">=3.8",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    zip_safe=False,
)
