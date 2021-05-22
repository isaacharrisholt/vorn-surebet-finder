apt-get install python3-pip || sudo apt-get install python3-pip || brew install python3-pip
apt-get install chromium-chromedriver || sudo apt-get chromium-chromedriver || brew cask install chromium-chromedriver
xattr -d com.apple.quarantine files/chromedriver_mac || echo
python3 -m pip install -r requirements.txt || sudo python3 -m pip install -r requirements.txt || python -m pip install -r requirements.txt || sudo python -m pip install -r requirements.txt