all:
	@echo all

init_db:
	@python3 src/init_db.py

run:
	@python3 src/bruteforce.py

clean:
	@echo clean

.PHONY:
	all init_db clean
