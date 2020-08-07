from setuptools import setup, find_packages

install_requires = [
    "graphql-server[flask]>=3.0.0b1",
]

tests_requires = [
    "pytest>=5.4,<5.5",
    "pytest-cov>=2.8,<3",
]

dev_requires = [
    "flake8>=3.7,<4",
    "isort>=4,<5",
    "check-manifest>=0.40,<1",
] + tests_requires

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name="Flask-GraphQL",
    version="2.0.1",
    description="Adds GraphQL support to your Flask application",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/graphql-python/flask-graphql",
    download_url="https://github.com/graphql-python/flask-graphql/releases",
    author="Syrus Akbary",
    author_email="me@syrusakbary.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="api graphql protocol rest flask",
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
    tests_require=tests_requires,
    extras_require={
        'test': tests_requires,
        'dev': dev_requires,
    },
    include_package_data=True,
    zip_safe=False,
    platforms="any",
)
