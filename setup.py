import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fasm",
    version="0.0.1",
    author="SymbiFlow Authors",
    author_email="symbiflow@lists.librecores.org",
    description="FPGA Assembly (FASM) Parser and Generation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SymbiFlow/fasm",
    packages=setuptools.find_packages(),
    package_data={
        'fasm': ['*.tx'],
    },
    install_requires=['textx'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['fasm=fasm:main'],
    },
)
