BUILD_DIR=build

all:
	@echo all

init_db:
	@python3 pyattacker/init_db.py

run_cpp:
	@cargo build --release --manifest-path rusthash/Cargo.toml
	@cmake attacker -B ${BUILD_DIR}
	@cmake --build ${BUILD_DIR}
	@echo "\n\n=== out =========\n"
	@${BUILD_DIR}/a.out
	@echo

clean:
	@echo clean

.PHONY:
	all init_db clean
