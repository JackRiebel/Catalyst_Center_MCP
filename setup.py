from setuptools import setup, find_packages

setup(
    name="catalyst-center-mcp",
    version="0.1.0",
    description="Model Context Protocol server for Cisco Catalyst Center",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-username/catalyst-center-mcp",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.103.2",
        "uvicorn==0.23.2",
        "requests==2.31.0",
        "pydantic==2.4.2",
        "python-dotenv==1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)