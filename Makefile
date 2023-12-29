BUILD_DIR=build

all:
	@echo all

init_db:
	@python3 src/pyattacker/init_db.py

run_py:
	@python3 src/pyattacker/bruteforce.py

run_cpp:
	@cmake src/attacker -B ${BUILD_DIR}
	@cmake --build ${BUILD_DIR}
	@echo "\n\n=== out =========\n"
	@${BUILD_DIR}/a.out
	@echo

clean:
	@echo clean

.PHONY:
	all init_db clean
