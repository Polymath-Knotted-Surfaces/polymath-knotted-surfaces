# polymath-knotted-surfaces
## Getting Started with Python, GitHub, and all that
This document will get you to install Git and Python for working with SnapPy.

### Tools Needed:
Macs:
* [Homebrew](https://docs.brew.sh/Installation)
* [MiniForge3](https://github.com/conda-forge/miniforge) (Make sure to grab the ***Mambaforge*** version for your system!)

Windows:
* [GitForWindows](https://gitforwindows.org/)
* [MiniForge3](https://github.com/conda-forge/miniforge) (Make sure to grab the ***Mambaforge*** version for your system! Mamba is a better version of Conda.)

---

On either system, once all software is installed, open up a command prompt. (On Macs, this is the terminal app. On windows, look for "Git Bash")

First, we need to make sure git is properly setup.
1. If you're on a Mac, you first need to run `brew install git`. (On a Windows machine, you can ignore this step.)
2. We'll now setup git for use with GitHub.
	1. Set your name in git `git config --global user.name "John Doe"`
	2. Set your email in git `git config --global user.email johndoe@example.com`
	3. Set the default branch to "master" `git config --global init.defaultBranch master`
	4. Set colorful mode true `git config --global color.ui true`
	5. Use [this link](https://docs.github.com/en/get-started/getting-started-with-git/caching-your-github-credentials-in-git) to setup the credential manager for your machine. Make sure to follow the instructions for your operating system. You may be prompted for your GitHub username and password. Enter them. They are now saved to your machine's keychain/credentials store.
	6. We'll use GitHub at a later date for sharing code. For now, we just need it to be installed and setup.
	
Now, we're going to get Python setup.
1. Test that Python and Miniforge3 was installed nicely by executing the command `mamba --version`. The result should be something like `mamba 0.14.1` or a (higher) version.
2. Run `mamba upgrade --all -y` to update your packages.
3. Run `mamba install -y numpy pandas scipy plotnine jupyterlab jupyter cffi docutils  ipykernel ipython networkx matplotlib sympy click requests arrow toolz cython cytoolz path path.py pyrsistent qt qtawesome qtpy regex seaborn setuptools pip statsmodels spyder spyder-kernels tk toml pyyaml tqdm pillow` to add some default packages. (This will probably take some time, be patient!)
4. Next, run `pip install -U snappy snappy-15-knots` to install snappy.
5. We now test that the SnapPy installation was successful. Try running `python -m snappy.app`. If a window launches, you're good to go!