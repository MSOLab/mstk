import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mstk",
    version="0.0.1",
    author="MSO Lab",
    author_email="mso.postech@gmail.com",
    description="Machine Scheduling ToolKit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL 3.0",
        "Operating System :: Windows (x64)",
    ],
    zip_safe=False,
    python_requires=">=3.7",
)

# TODO: add depedency for PyQt5
