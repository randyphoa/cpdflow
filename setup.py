from setuptools import setup, find_packages

exec(open("cpdflow/version.py").read())

# with open("README.rst") as f:
#     readme = f.read()

with open("README.md") as f:
    readme = f.read()

with open("requirements/requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="cpdflow",
    version=__version__,  # type: ignore # noqa F821
    description="A declarative approach to model lifecycle management on Cloud Pak for Data",
    long_description=readme,
    long_description_content_type="text/markdown",  # "text/x-rst"
    author="Randy Phoa",
    url="https://github.com/randyphoa/cpdflow",
    license="GPLv3",
    packages=find_packages(exclude=("tests", "docs")),
    entry_points={"console_scripts": ["cpdflow=cpdflow.cli:cli"]},
    install_requires=install_requires,
    classifiers=["Development Status :: 3 - Alpha", "Intended Audience :: Developers", "Programming Language :: Python :: 3.7"],
    include_package_data=True,
)
