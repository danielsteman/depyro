import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = ["python-dotenv==0.19.2", "requests==2.26.0"]

setuptools.setup(
    name="depyro",
    version="1.0.0",
    author="Daniel Steman",
    author_email="daniel-steman@live.nl",
    description="A wrapper for the De Giro API to fetch portfolio data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    url="https://github.com/danielsteman/depyro",
    project_urls={"Bug Tracker": "https://github.com/danielsteman/depyro/issues"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
