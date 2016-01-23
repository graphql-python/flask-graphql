from setuptools import setup, find_packages

required_packages = ['graphql-core>=0.4.9', 'flask>=0.7.0']

setup(
    name='graphql-flask',
    version='0.0.1',
    description='Adds GraphQL support to your Flask application',
    long_description=open('README.rst').read(),
    url='https://github.com/graphql-python/graphql-flask',
    download_url='https://github.com/graphql-python/graphql-flask/releases',
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
)
