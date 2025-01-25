setup(
    name="easyaiapi",  # Your library name
    version="0.1.0",
    author="Martin Yanev",
    author_email="your_email@example.com",
    description="A Python library for dynamic ChatGPT interactions made easy.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/easyaiapi",  # Replace with your GitHub repo URL
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
