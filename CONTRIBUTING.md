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

### Understanding the code

I'll soon write a very brief explanatory documentation on the project's architecture, so you can understand how the project works without having to look every file up first. For now, you'll have to look at the code and try to understand how it works, sorry.

### Fork and Pull

We work with a [Fork & Pull](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#fork--pull) method. Fork this repo, write your code in a feature branch (make sure it is up to date with the project's `develop` branch) and open a **Pull Request** to the `develop` repository, describing your changes or even referencing the **Issue** that inspired your code.

If you're working on a new feature that has no prior **Issue** related to it, please open an **Issue** describing the feature and then reference it in your new **Pull Request**.

### Code conventions

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). It's a must.
- I'm still studying a way to make the entire code uniform, and I'm inclined to only accepting [Black](https://github.com/psf/black) formatted code.
- Make descriptive variable names, as best as you can.

### Python versions

Python is rapidly changing, and I plan to adjust to Python's changes as we go. Currently supported Python version is 3.10.

I'll soon implement [tox](https://github.com/tox-dev/tox) to test all features.

### Tests

If you're writing new features, it is always a good idea to include tests with your code. I know the current code is not filled with tests (it soon will be), but make sure to add tests with your PR, and if you're changing some feature, make sure to pass all tests before submitting code.

We'll also soon be using CI/CD to make development go faster, and tests are an essential part of that.


