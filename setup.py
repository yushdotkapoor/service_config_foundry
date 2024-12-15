from setuptools import setup

# Load the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="service-config-foundry",
    version="0.1",
    author="Yush Kapoor",
    author_email="yushdotkapoor@gmail.com",
    description="Helps create non-templated systemd services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yushdotkapoor/service-config-foundry",
    project_urls={
        "Bug Tracker": "https://github.com/yushdotkapoor/service-config-foundry/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Linux & Python users",
    ],
    packages=["find:"],  # Automatically finds packages in the project
    python_requires=">=3.0",
)
