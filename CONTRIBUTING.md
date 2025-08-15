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

### Code of Conduct

We are committed to fostering an open and welcoming environment for all contributors. We expect everyone participating in the eSports Manager project to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md), which promotes respect, inclusivity, and positive interactions within our community.

**Core Principles:**
- Be respectful and inclusive of differing viewpoints and experiences
- Use welcoming and inclusive language
- Focus on constructive criticism and feedback
- Show empathy towards other community members

Inappropriate behavior will not be tolerated. If you witness or experience unacceptable behavior, please report it to the project maintainers at admin@esportsmanager.net.

### Fork and Pull Process

We work with a [Fork & Pull](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#fork--pull) method. Here's the detailed process:

1. **Fork the repository** to your own GitHub account
2. **Clone your fork** locally on your machine
3. **Create a feature branch** from the `develop` branch (not from `main`)
4. **Make your changes** and commit them to your feature branch
5. **Keep your branch updated** with the project's `develop` branch by regularly pulling and rebasing
6. **Push your changes** to your fork on GitHub
7. **Submit a Pull Request** to the original repository's `develop` branch

Once submitted, your PR will be reviewed by the maintainers. You may be asked to make changes before your contribution is accepted. All PRs require at least one approval from a maintainer before being merged.

If you're working on a new feature that has no prior **Issue** related to it, please open an **Issue** describing the feature and then reference it in your new **Pull Request**.

### Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for our commit messages. This helps us automatically generate changelogs and makes the commit history more readable.

Format: `type(scope): subject`

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without feature changes
- `test`: Adding or updating tests
- `chore`: Changes to build process or auxiliary tools

**Examples:**
```
feat(player): add nationality to player profile
fix(matches): resolve issue with match scheduling
docs(README): update installation instructions
refactor(database): optimize team queries
test(models): add unit tests for Staff model
```

### Code conventions

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). I use **flake8** to check for PEP 8 compliance.
- Use the **pre-commit** package to auto format your code with **ruff**. I don't like to spend time talking about formatting, and styling issues, so using autoformatters to take care of these issues is a way to settle the styling debate.
- Make descriptive variable names, as best as you can.
- Whenever you can, use typehints. Typehints help me and other devs to understand how a function or class should be used. I learned to love typehints, you should embrace them as your friend as well.
- I usually separate my work in classes rather than just using functions. I don't enforce the use of OOP in code, but I use it very often to encapsulate behavior.
- Unit testing is what kept my sanity while writing this project. I like simple tests, and you should write them when adding functionality to the project. I prefer using **pytest** because it's way simpler to write than **unittest**.

### Python versions

I'm currently using Python 3.11, but it should be compatible with Python 3.10+.

### Branching Strategy

We use a modified version of the GitFlow workflow with the following branches:

- `main`: Production-ready code, always stable and deployable
- `develop`: Main development branch where features are integrated
- `feature/*`: Feature branches (e.g., `feature/player-stats-page`)
- `bugfix/*`: Bug fix branches (e.g., `bugfix/match-scheduling-error`)
- `hotfix/*`: Urgent fixes for production (e.g., `hotfix/critical-crash-fix`)

When creating a new branch, follow these naming conventions:
- Use lowercase and hyphens for words
- Include a descriptive but concise name
- Prefix with the appropriate category (feature, bugfix, hotfix)

### Project Structure Overview

To help you get started quickly, here's a brief overview of the project structure:

```
esports-manager/
├── esm/                # Main application code
│   ├── models/         # SQLModel data models
│   ├── routes/         # API route handlers
│   ├── utils/          # Utility functions and helpers
│   └── config.py       # Application configuration
├── frontend/          # Frontend code
│   ├── static/         # Static assets (CSS, JS, images)
│   └── templates/      # HTML templates
├── scripts/           # Utility scripts
├── tests/             # Test suite
└── esm.py            # Main application entry point
```

### Development Environment Setup

Below is an expanded guide to setting up your development environment:

#### Prerequisites

- Python 3.10+ installed
- Git installed
- A GitHub account

#### Setup Steps

1. [Fork the repository](https://github.com/esports-manager/esports-manager/fork)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/esports-manager.git
   cd esports-manager
   ```

1. **Set up the virtual environment and dependencies:**
   ```bash
   uv venv .venv
   uv sync
   ```

1. **Activate the virtual environment:**
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

1. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

1. **Populate the database:**
  ```bash
  uv run python scripts/init_db.py
  ```

#### Running the Application

To run the main application:
```bash
uv run python esm.py
```

To run the development server with auto-reload:
```bash
uv run uvicorn dev:app --reload
```

Alternatively, you can use the shell scripts:


To run the main application with pywebview:
```bash
./scripts/run.sh
```

To run the development server with tailwindcss updates (if you are changing the frontend):
```bash
./scripts/run_dev.sh
```

#### Working on the frontend

To stylize the frontend, you need to run tailwindcss:

```bash
uv run tailwindcss -i frontend/static/css/input.css -o frontend/static/css/tailwind.css --watch
```

Alternatively, you can use the shell script to both run the server and update the CSS:

```bash
./scripts/run_dev.sh
```

If you wish to minify the CSS, you can run:

```bash
uv run tailwindcss -i frontend/static/css/input.css -o frontend/static/css/tailwind.css --minify
```

#### Troubleshooting Common Issues

- **Missing dependencies error**: Try running `uv sync --upgrade` to ensure all dependencies are up to date.
- **Database connection error**: Check that your database file is created correctly. Start the development server, it should create the database file if it doesn't exist.
- **Import errors**: Ensure you're running commands from the project root directory with the virtual environment activated.
- **Pre-commit hooks failing**: Run `uv run pre-commit run --all-files` to identify and fix formatting issues.
- **Windows-specific issues**: If you encounter path-related issues on Windows, try using forward slashes in configuration files.
- **Error while committing**: This might be because the pre-commit has identified a few problems with your code. To check them individually, use `uv run ruff check` and `uv run ruff format` to see the messages that are returned by both services. Then you have to stage your changes properly and try to commit them again.

### Testing

Testing is crucial for maintaining code quality and preventing regressions. We use pytest for all tests.

#### Running Tests

To run all tests:
```bash
uv run pytest
```

To run specific tests:
```bash
uv run pytest tests/
uv run pytest tests/test_player_model.py
uv run pytest tests/test_player_model.py::test_create_moba_player
```

With coverage report:
```bash
uv run pytest --cov=esm tests/
```

#### Test Guidelines

- All new features should include tests
- Aim for at least 80% test coverage for new code
- Focus on testing behavior rather than implementation details
- Use fixtures for common test setups
- Keep tests fast and isolated from each other

### Issue Templates

When creating an issue, please use the appropriate template:

#### Bug Reports

A good bug report should include:

- Clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Screenshots or code examples if applicable
- Game version and environment details
- Any error messages or logs

Example:
```
**Bug**: Match scores not updating after simulation

**Steps to Reproduce**:
1. Start a new match simulation
2. Complete the simulation
3. View the team standings page

**Expected**: Updated scores in team standings
**Actual**: Old scores still displayed

**Environment**: eSports Manager v0.1.0, Windows 11
```

#### Feature Requests

Feature requests should include:

- Clear description of the proposed feature
- Justification for why it's valuable
- Any design ideas or implementation suggestions
- Examples of similar features in other applications (if applicable)

### Translation Guide

The internationalization system is currently being developed. When complete, the translation workflow will be:

1. Extraction of translatable strings from the codebase
2. Translation files organized by language code in the `locales/` directory
3. Web interface for translating strings (coming soon)

If you're interested in helping with translations, please watch for updates on this feature.

### Contact and Communication

Have questions or need help? Reach out through one of these channels:

- **Issue Tracker**: Best for bug reports and feature requests
- **Discussions**: For general questions and ideas
- **Email**: admin@esportsmanager.net for private inquiries

For security issues, please contact admin@esportsmanager.net directly instead of posting publicly.

## Thank You!

Thank you for contributing to eSports Manager. Your support helps make this project better for everyone in the community!
