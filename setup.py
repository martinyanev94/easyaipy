from setuptools import setup, find_packages


setup(
    name="easyaipy",
    version="0.1.0",
    author="Martin Yanev",
    author_email="mpyanev@gmail.com",
    description="A Python library for dynamic ChatGPT interactions made easy.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/martinyanev94/easyaiapi",
    packages=find_packages(),
    install_requires=[
        "openai",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
