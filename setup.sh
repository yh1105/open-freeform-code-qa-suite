# setting up javascript and typescript env
apt-get install -y nodejs
mkdir ~/.npm-global
npm config set prefix `~/.npm-global`
source ~/.profile
export PATH=~/.npm-global/bin:$PATH
npm install -g jsdom
npm install -g typescript
export NODE_PATH=$(npm root --quiet -g)