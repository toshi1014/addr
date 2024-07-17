BUILD_DIR=build
ENTROPY_TYPE=random

define prepare
	@cargo build --release --manifest-path rusthash/Cargo.toml
	@cmake attacker -B ${BUILD_DIR}
	@cmake -DCMAKE_BUILD_TYPE=$1 ${BUILD_DIR} -DENTROPY_TYPE=${ENTROPY_TYPE}
	@cmake --build ${BUILD_DIR}
	@echo "\n\n=== out =========\n"
endef


all: attacker/CMakeLists.txt
	@$(call prepare,)
	@${BUILD_DIR}/a.out

debug: attacker/CMakeLists.txt
	@$(call prepare,Debug)
	@${BUILD_DIR}/a.out

release: attacker/CMakeLists.txt
	@$(call prepare,Release)
	@if [ "$(ENTROPY_TYPE)" = "random" ]; then \
		while true; do sudo ${BUILD_DIR}/a.out; done; \
	else \
		sudo ${BUILD_DIR}/a.out; \
	fi

init_db:
	@python3 pyattacker/init_db.py

clean:
	@echo clean

.PHONY:
	all debug release init_db clean
