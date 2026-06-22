FROM timescale/timescaledb:latest-pg15

RUN apk add build-base make clang19 llvm19 git || apk add build-base make clang llvm git; \
    [ -x /usr/bin/clang-19 ] || ln -sf "$(command -v clang)" /usr/bin/clang-19
COPY tulip /tulip
RUN cd /tulip && make USE_PGXS=1 install && cd / && \
	git clone https://github.com/ossc-db/pg_hint_plan --branch PG15 && \
	cd pg_hint_plan && make USE_PGXS=1 install
