FROM ubuntu:24.04

ENV WORK_DIR=/addr

RUN apt update
RUN apt install -y \
    autoconf \
    automake \
    build-essential \
    cmake \
    curl \
    libtool \
    libgmp-dev \
    libssl-dev \
    sqlite3 \
    libsqlite3-dev \
    git vim

# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH=/root/.cargo/bin:$PATH

# copy
COPY "attacker" "$WORK_DIR/attacker"
COPY "pyattacker" "$WORK_DIR/pyattacker"
COPY "rusthash" "$WORK_DIR/rusthash"
COPY "db" "$WORK_DIR/db"
COPY [ \
    "setup.sh", \
    "Makefile", \
    "config.json", \
    "$WORK_DIR" \
    ]

# setup
RUN bash "$WORK_DIR/setup.sh"

WORKDIR $WORK_DIR
CMD ["make release"]
