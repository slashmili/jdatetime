from setuptools import setup


setup(
    name="jdatetime",
    version="5.2.0",
    packages=[
        "jdatetime",
    ],
    license="Python Software Foundation License",
    keywords="Jalali implementation of Python datetime",
    platforms="any",
    author="Milad Rastian",
    author_email="eslashmili@gmail.com",
    description=("Jalali datetime binding for python"),
    url="https://github.com/slashmili/python-jalali",
    long_description=open("README").read(),
    python_requires=">=3.9",
    install_requires=["jalali-core>=1.0"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development",
    ],
)
