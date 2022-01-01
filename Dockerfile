FROM ubuntu:latest

RUN ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo Europe/Moscow > /etc/timezone

RUN apt update && \
    apt install -y ca-certificates

COPY sources.list /etc/apt/

RUN apt update && \
    apt install -y --no-install-recommends git cmake clang ninja-build libssl-dev libboost-system-dev binutils zlib1g-dev libcurl4-openssl-dev libspdlog-dev && \
    apt clean

ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++

COPY . /opt/

WORKDIR /opt/

RUN git clone --depth 1  --jobs $(nproc) https://github.com/reo7sp/tgbot-cpp && \
    cd tgbot-cpp && \
    cmake . -G Ninja && \
    ninja && \
    ninja install && \
    rm -rf /opt/tgbot-cpp/*

WORKDIR /opt/build

RUN cmake .. -G Ninja && \
    cmake --build . && \
    CTEST_OUTPUT_ON_FAILURE=TRUE cmake --build . --target dorabot

CMD ["./dorabot"]