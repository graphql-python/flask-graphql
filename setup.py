from setuptools import setup, find_packages

install_requires = [
    "graphql-core>=2.3,<3",
    "flask>=0.7.0",
    "graphql-server-core>=1.1,<2",
]

tests_requires = [
    'pytest>=2.7.2',
    'pytest-cov==2.8.1',
    'pytest-flask>=0.10.0',
    'graphql-core>=2.1,<3',
    'graphql-server-core>=1.1,<2',
    'Flask>=0.10.0',
]

dev_requires = [
    'flake8==3.7.9',
    'isort<4.0.0'
] + tests_requires

setup(
    name="Flask-GraphQL",
    version="2.0.1",
    description="Adds GraphQL support to your Flask application",
    long_description=open("README.md").read(),
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
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
