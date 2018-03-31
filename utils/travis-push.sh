#!/bin/bash

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
  git checkout $TRAVIS_BRANCH
  git pull
}

setup_git

bumpversion --no-tag --message '[ci skip] Travis bump version: {current_version} → {new_version}' patch

git push --tags "https://${GH_TOKEN}@github.com/buluba89/Yatcobot.git" $TRAVIS_BRANCH

if [ "$TRAVIS_BRANCH" == "dev" ]; then
    curl -H "Content-Type: application/json" --data '{ "docker_tag" : "dev"}' -X POST https://registry.hub.docker.com/u/buluba89/yatcobot/trigger/$DH_TOKEN/
elif [ "$TRAVIS_BRANCH" == "master" ]; then
    curl -H "Content-Type: application/json" --data '{ "docker_tag" : "latest"}' -X POST https://registry.hub.docker.com/u/buluba89/yatcobot/trigger/$DH_TOKEN/
    # Wait so docker hub not ratelimit the request
    sleep 60
    curl -H "Content-Type: application/json" --data '{ "docker_tag" : "alpine"}' -X POST https://registry.hub.docker.com/u/buluba89/yatcobot/trigger/$DH_TOKEN/
fi