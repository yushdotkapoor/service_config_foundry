from setuptools import setup, find_packages

# Load the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="service_config_foundry",
    version="0.5.2",
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
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),  # Automatically finds packages in the project
    python_requires=">=3.8",
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0", 
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "pytest-cov>=4.0.0", 
            "flake8>=6.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "pre-commit>=3.0.0",
            "tox>=4.0.0",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
    },
)
