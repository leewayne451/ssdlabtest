FROM alpine:3.20

RUN apk add --no-cache git openssh-client

RUN git config --global user.name "WAYNE LEE" \
    && git config --global user.email "2400968@sit.singaporetech.edu.sg" \
    && git config --global init.defaultBranch main

WORKDIR /repo

ENTRYPOINT ["git"]
