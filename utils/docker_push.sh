#!/bin/bash

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin


if [ "$TRAVIS_BRANCH" == "dev" ]; then
    docker build -t buluba89/yatcobot:dev .

    docker push buluba89/yatcobot:dev

elif [ "$TRAVIS_BRANCH" == "master" ]; then
    docker build -t buluba89/yatcobot:latest .
    docker build -f Dockerfile.alpine -t buluba89/yatcobot:alpine .

    docker push buluba89/yatcobot:latest
    docker push buluba89/yatcobot:alpine
fi