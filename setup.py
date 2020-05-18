from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

version = '0.0.1'

setup(
    name='secura-archiver',
    version=version,
    packages=find_packages(exclude=('tests',)),
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Isaac Williams',
    author_email='isaac.williams@secura.com',
    description='A 7zip archiver',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
)
