import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BoSS-pkg-Tomev",
    version="0.0.1",
    author="Tomasz Rybotycki",
    author_email="rybotycki.tomasz+boss@gmail.com",
    description="A utility package for boson sampling experiments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tomev-CTP/BoSS",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
