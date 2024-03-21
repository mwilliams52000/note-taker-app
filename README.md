# note-taker-app

A note-taking app made for academic purposes as part of the Python class at PennWest California.

## Table of Contents
1. [Downloading Python](#downloading-python)
1. [Downloading Git](#downloading-git)
2. [Downloading VS Code](#downloading-vs-code)
3. [Downloading Libraries](#downloading-libraries)

## Downloading Python

If you need Python installed on your device, go to [this](https://www.python.org/downloads/) page and install the latest version of Python 3.

## Downloading Git

Go to [this](https://git-scm.com/download/win) page. Click on the "64-bit Git for Windows Setup" option, which should download an exe file. Install it, the default options should be fine.

Once Git is installed, you will need to configure your username and email. These are the same as your GitHub username and GitHub email, respectively. Run these commands, replacing the parts in quotes with your information:

    git config --global user.name "Your Name"
    git config --global user.email "youremail@yourdomain.com"

## Downloading VS Code

Download VS Code from [here](https://code.visualstudio.com/). Once it's opened, install the Python extension [here](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and Live Share extension [here](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare). These will be useful for this project.

Clone this repo by clicking on the Source Control button on the left toolbar, then click "Clone Repository". You will have to log into GitHub. Make sure to choose **YOUR** fork, not someone else's!

## Downloading Libraries

Before you go any further, make sure you have Python and that the expected version is available from your command line. You can check this by clicking the Windows key + R and typing 'cmd'. Click 'Ok' and launch the command line. Type 'py --version' within the command line. You should see something like this if Python is properly installed: 'Python 3.11.4'. If you do, then type in 'py -m pip --version' to ensure that you have pip available. As long as pip is available, you can proceed to installing the libraries.

To install pyaudio, type this into the command line:

    py -m pip install pyaudio

To install pyspellchecker, type this into the command line:

    py -m pip install pyspellchecker
