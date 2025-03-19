# CONTRIBUTING

Thank your for taking the time to read this, and for showing your interest in supporting us!

There are several ways you can contribute with the project, whether you are a programmer or just a fan of this type of project, it means a lot if you can help us in any meaningful way. This game was born out of a dissatisfaction with alternatives in the market, and was built by an eSports fan, so I assume that if you're here, you want to be part of this and you're also an eSports fan.

If you can't code, but you have other skills that you can help us, don't worry, you can still do it. And if you can't do either of the things we proposed, you can still help us:

- Give us a star!
- Tweet about the project!
- Refer this project in your project's readme!
- Tell your friends about us!
- Share us on facebook!
- Donate to the project *(not available yet)*
- Make a video about it!
- Play it!

## How to contribute

If you really want to help us directly, thank you very much! We have a few jobs that you might be interested in:

- **Report a problem**  
  You can report bugs or issues you encounter in the game. Open an Issue and follow the steps to report the problem. Please read carefully the bug reporting issue template before submitting a new bug report. Provide as much information as you can to help us track the bug and solve it as fast as we possibly can.

- **Propose enhancements**  
  You can also propose new enhancements or improvements to the game. We're considering new ideas every day, and you can propose yours by opening an Issue and following the steps to propose enhancements. Just make sure to check the Issues page for similar ideas before opening up a new Issue. We don't want to flood the page with duplicated issues.

- **Documentation**  
  Do you think we can improve our documentation somehow? You can propose changes to the text, or write useful tutorials or examples on how to do certain things in the game.

- **Translation**  
  The game is still not translatable, but it soon will be. If you want to translate the game to your own language, you will be able to do that. We will soon provide a platform to do that. You will also be able to translate the documentation to your language.

- **Create new content**  
  You can create content to the game, like images, logos, database improvements, whatever you'd like. Soon this option will be available, and you will be able to submit your new content proposal easily.

## Submitting code

The most traditional way to contribute is to submit new code. **eSports Manager** is a GPLv3 licensed project, read the [LICENSE.md](LICENSE.md) before submitting your code. Your code must be GPLv3 compliant, which means you understand that any code submitted here is original or also GPL-compliant, and must not depend on patents or copyrighted third-party content. Your code is subject to a free and open source license that will be available to the entire open source community.

Once you understand that concept, you're welcome to submit new code.

### Fork and Pull

We work with a [Fork & Pull](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#fork--pull) method. Fork this repo, write your code in a feature branch (make sure it is up to date with the project's `develop` branch) and open a **Pull Request** to the `develop` repository, describing your changes or even referencing the **Issue** that inspired your code.

If you're working on a new feature that has no prior **Issue** related to it, please open an **Issue** describing the feature and then reference it in your new **Pull Request**.

### How do I install the dependencies and start developing?

This is primarily a Python project. Usually, some developers like to install the dependencies from a `requirements.txt` file. I don't like to maintain a separate `requirements.txt` file for that, and I resort to virtualenv managers to manage my dependencies.

If you're not familiar with the concept of Virtual environments, see [this documentation](https://docs.python.org/3/library/venv.html) from the official Python documentation.

Like I said, I like to use virtualenv and dependency managers to develop my projects. This project supports [Pipenv](https://pipenv.pypa.io/en/latest/) and [Poetry](https://python-poetry.org/). You can pick either one, you don't need both at the same time.

I started this project using **Pipenv** and I'm quite comfortable using it, but **Poetry** is becoming more of a standard for Python projects lately, because it relies on the [**pyproject.toml**](pyproject.toml) file, which is a new standard proposed on [PEP 518](https://peps.python.org/pep-0518/) and [PEP 621](https://peps.python.org/pep-0621/). If you don't know what a PEP is, see [PEP 1 – PEP Purpose and Guidelines](https://peps.python.org/pep-0001/).

So if you use **Pipenv** on a daily basis, you can keep using it. If you use **Poetry**, you can safely use it here.

**How do I set up my environment then?**

It's pretty simple, actually. An important requirement here is that you have the standard Python package manager installed: **pip**. To learn how to install **pip**, see [Installing pip](https://pip.pypa.io/en/stable/installation/).

Then you can install either **Pipenv** or **Poetry**:

**Pipenv:**

```bash
pip install pipenv
```

**Poetry:**

```bash
pip install poetry
```

You can [fork this repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) and clone it:

```bash
git clone https://github.com/<your-user-name>/esports-manager.git
```

And you then enter the repository directory:

```bash
cd esports-manager
```

And you just run the install the project with all the development dependencies:

**Pipenv:**

```bash
pipenv install --dev
```

**Poetry:**

```bash
poetry install
```

This installs all of the game's dependencies, with all that you need to develop the project. This includes the testing framework we use: [**pytest**](https://docs.pytest.org/en/stable/), the tool to run git hooks called [**pre-commit**](https://pre-commit.com/), the [**black**](https://black.readthedocs.io/en/stable/index.html) code formatter, and other tools like [**isort**](https://pypi.org/project/isort/), [**flake8**](https://flake8.pycqa.org/en/latest/), and [**hypothesis**](https://hypothesis.readthedocs.io/en/latest/).

To contribute code, you must install the **pre-commit** package:

**Pipenv:**

```
pipenv run pre-commit install
```

**Poetry:**

```
poetry run pre-commit install
```

This will run the pre-commit hooks before every commit. The hooks will format your code and check for [PEP 8](https://peps.python.org/pep-0008/) compliance. The reason why I use these pre-commit hooks and auto formatters is to avoid discussions regarding formatting or standard programming practices in Python. We can just focus on code that works.

A good practice is to also run tests before submitting code:

**Pipenv:**

```
pipenv run pytest
```

**Poetry:**

```
poetry run pytest
```

Just to make sure you didn't break anything. Once you submit a PR, GitHub Actions will run these automated tests too, just in case you forgot to run the tests.

### Code conventions

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). I use **flake8** to check for PEP 8 compliance.
- Use the **pre-commit** package to auto format your code with **Black** and **isort**.
- Make descriptive variable names, as best as you can.
- I usually separate my work in classes rather than just using functions. I don't enforce the use of OOP in code, but it's a good way to encapsulate behavior.
- Unit tests are great. Use **pytest** to write your tests.

### Python versions

Python is rapidly changing, and I plan to adjust to Python's changes as we go. Currently supported Python version is 3.10.

I'll soon implement [tox](https://github.com/tox-dev/tox) to test all features.

### Tests

If you're writing new features, it is always a good idea to include tests with your code. If you're changing some feature, make sure to pass all tests before submitting code.
