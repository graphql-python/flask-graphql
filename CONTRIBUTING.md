# Contributing

Thanks for helping to make flask-graphql awesome!

We welcome all kinds of contributions:

- Bug fixes
- Documentation improvements
- New features
- Refactoring & tidying


## Getting started

If you have a specific contribution in mind, be sure to check the [issues](https://github.com/graphql-python/flask-graphql/issues) and [projects](https://github.com/graphql-python/flask-graphql/projects) in progress - someone could already be working on something similar and you can help out.


## Project setup

After cloning this repo, ensure dependencies are installed by running:

```sh
make dev-setup
```

## Running tests

After developing, the full test suite can be evaluated by running:

```sh
make tests
```

## Development on Conda

In order to run `tox` command on conda, you must create a new env (e.g. `flask-grapqhl-dev`) with the following command:

```sh
conda create -n flask-grapqhl-dev python=3.8
```

Then activate the environment with `conda activate flask-grapqhl-dev` and install [tox-conda](https://github.com/tox-dev/tox-conda):

```sh
conda install -c conda-forge tox-conda
```

Uncomment the `requires = tox-conda` line on `tox.ini` file and that's it! Run `tox` and you will see all the environments being created and all passing tests. :rocket:

