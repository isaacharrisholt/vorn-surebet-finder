apt-get install python3-pip || sudo apt-get install python3-pip || brew install python3-pip
python3 -m pip install -r requirements.txt || sudo python3 -m pip install -r requirements.txt || python -m pip install -r requirements.txt || sudo python -m pip install -r requirements.txt
apt-get install chromium-chromedriver || sudo apt-get chromium-chromedriver || brew cask install chromium-chromedriver
cd files || exit
xattr -d com.apple.quarantine chromedriver_mac || echo
spctl --add --label 'Approved' chromedriver_mac || echo
