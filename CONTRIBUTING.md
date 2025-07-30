<!--
SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
SPDX-License-Identifier: GPL-3.0-or-later
License-Filename: LICENSES/GPL-3.0-or-later
-->

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

Like I said, I like to use virtualenv and dependency managers to develop my projects. This project uses [`uv`](https://docs.astral.sh/uv/) as a dependency and virtualenv manager.

To start the virtualenv and install the dependencies, run:

```bash
uv venv
uv sync
```

To activate the virtualenv, run:

```bash
source .venv/bin/activate
```

To run the project, run:

```bash
uv run python esm
```

To run the development server, run:

```bash
uv run uvicorn dev:app --reload
```

To run the tests, run:

```bash
uv run pytest
```

Just to make sure you didn't break anything. Once you submit a PR, GitHub Actions will run these automated tests too, just in case you forgot to run the tests.

### Code conventions

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). I use **flake8** to check for PEP 8 compliance.
- Use the **pre-commit** package to auto format your code with **Black** and **isort**. I don't like to spend time talking about formatting, and styling issues, so using autoformatters to take care of these issues is a way to settle the styling debate.
- Make descriptive variable names, as best as you can.
- Whenever you can, use typehints. Typehints help me and other devs to understand how a function or class should be used. I learned to love typehints, you should embrace them as your friend as well.
- I usually separate my work in classes rather than just using functions. I don't enforce the use of OOP in code, but I use it very often to encapsulate behavior.
- Unit testing is what kept my sanity while writing this project. I like simple tests, and you should write them when adding functionality to the project. I prefer using **pytest** because it's way simpler to write than **unittest**.

### Python versions

I'm currently using Python 3.11, but it should be compatible with Python 3.10+.

