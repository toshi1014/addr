all:
	@echo all

init_db:
	@python3 init_db.py

run:
	@python3 bruteforce.py

clean:
	@echo clean

.PHONY:
	all init_db clean
