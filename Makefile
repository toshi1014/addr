BUILD_DIR=build

all: attacker/CMakeLists.txt
	@cargo build --release --manifest-path rusthash/Cargo.toml
	@cmake attacker -B ${BUILD_DIR}
	@cmake --build ${BUILD_DIR}
	@echo "\n\n=== out =========\n"
	@${BUILD_DIR}/a.out
	@echo


init_db:
	@python3 pyattacker/init_db.py

clean:
	@echo clean

.PHONY:
	all init_db clean
