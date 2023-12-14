all:
	@echo all

init_db:
	@python3 src/pyattacker/init_db.py

run:
	@python3 src/pyattacker/bruteforce.py

clean:
	@echo clean

.PHONY:
	all init_db clean
