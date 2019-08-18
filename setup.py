import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lambdabuild",
    version="0.2.0",
    author="Shlomi Matichin",
    author_email="shlomomatichin@gmail.com",
    description="Easily build AWS lambda artifacts and layers, correctly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shlomimatichin/lambdabuild",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Environment :: Console',
        'Intended Audience :: Developers',
    ],
    keywords='AWS, lambda, build, docker',
    py_modules=['lambdabuild'],
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'lambdabuild = lambdabuild.cli:_main',
        ],
    },
)
