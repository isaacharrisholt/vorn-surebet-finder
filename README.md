# Vorn Surebet Finder

Vorn Surebet Finder is a Python program that scrapes odds data from broker websites for live matches for a given sport.
Within those, it then finds combinations of bets that make up a "surebet". You can learn more about surebets
[here](https://betblazers.com/guide/sure-bets).

The program will then present these surebets to the user along with how much the user should invest on each bet.

Currently supported sites (more to come):
- [Betfair](https://www.betfair.com/sport/)
- [bwin](https://sports.bwin.com/en/sports)
- [Ladbrokes](https://sports.ladbrokes.com/)

The program currently supports the following sports, but more will come as the program gets updated:
- Football
- Tennis

## Prerequisite Software

- [Python 3](https://www.python.org/) (make sure to add Python to PATH/environment variables when installing)
- [pandas 1.2.4 or newer](https://pandas.pydata.org/)
- [Selenium 3.141.0 or newer](https://github.com/SeleniumHQ/selenium/)
- [SymPy 1.8 or newer](https://www.sympy.org/en/index.html)
- [FuzzyWuzzy 0.18.0 or newer](https://github.com/seatgeek/fuzzywuzzy)
- [beepy 1.0.7 or newer](https://pypi.org/project/beepy/) (for alert sounds)
- [colorama 0.4.4 or newer](https://pypi.org/project/colorama/) (optional, enables colours in command line output)

### Windows installation

You can install the prerequisites double-clicking `install_prerequesites.bat` after installing Python 3.

### Mac and Linux installation

First, install Homebrew, which is a very useful package manager for MacOS and Linux. I recommend having this regardless
of whether or not it's to use this program. You can install it with the following command:

```commandline
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Run `install_prerequisites.sh` from the terminal to install the prerequisites. This will also install required libraries
for Chromedriver, so don't skip this step!

### Updating Chromedriver

I will try my best to keep the included Chromedriver up to date with the latest stable version of Chrome, but sometimes 
I may miss an update by a few days. If you wish to update it yourself, please download the relevant version of
Chromedriver from [here](https://chromedriver.chromium.org/downloads) and replace the correct file in the `chromedriver`
directory.

For Windows, this is `chromedriver.exe`, and for MacOS and Linux it's `chromedriver_mac` and `chromedriver_linux`
respectively.

## Program Installation

Vorn Surebet Finder can either be installed by downloading the repository from
[the GitHub page](https://github.com/isaacharrisholt/vorn-surebet-finder) or by running the following command if git
is installed on your machine:
```commandline
git clone https://github.com/isaacharrisholt/vorn-surebet-finder
```

## Usage
     
Follow the instructions for your operating system below.

### Windows

Once you've installed the [prerequisites](#prerequisite-software), double click `start_windows.bat`. That's it. Bish 
bash bosh.

### Mac and Linux

Run the `start_unix.sh` file once you've installed the [prerequisites](#prerequisite-software). You can do this with the
following command:

```commandline
source start_unix.sh
```

### Using the program

The program will ask which sport you'd like to check surebets for. I recommend not choosing the same sport all the time,
as this can start to look suspicious to bookies. Similarly, don't switch sports all over the place.

The program will then guide you through the rest of the process yourself, but should you have any issues, please raise
them with [@isaacharrisholt](https://github.com/isaacharrisholt).

## To-Dos

There are a few more things I want to do with this project. The current to-do list is below, but if you think of
anything you'd like added, please let me know!

- [x] Support for 3 sites
- [ ] Support for 5 sites
- [ ] Support for 10 sites!
- [ ] SUPPORT FOR 15 SITES!!!
- [ ] Support for 5 sports
- [ ] Support for 10 sports
- [ ] Add a GUI

## Contribute

Pull requests welcome, though if you want to make a major change, please open an issue first for discussion.

If you'd like to contribute by providing support for a new site, please create a Python file called `<sitename>.py` then
open an issue or message [@isaacharrisholt](https://github.com/isaacharrisholt). Please also ensure you follow the same
structure as I've done, so if I need to make changes in the future it's easy to find things.

## Credits

**Devs:**
- So far, just me.

**Inspiration:**
- [Frank Andrade on Medium](https://frank-andrade.medium.com/)

## License

Vorn Surebet Finder is licensed under [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).
