# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

required_packages = ['graphql-core>=1.0', 'flask>=0.7.0']

setup(
    name='Flask-GraphQL',
    version='1.4.1',
    description='Adds GraphQL support to your Flask application',
    long_description=open('README.rst').read(),
    url='https://github.com/graphql-python/flask-graphql',
    download_url='https://github.com/graphql-python/flask-graphql/releases',
    author='Syrus Akbary',
    author_email='me@syrusakbary.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='api graphql protocol rest flask',
    packages=find_packages(exclude=['tests']),
    install_requires=required_packages,
    tests_require=['pytest>=2.7.3'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
)
