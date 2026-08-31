.PHONY: all server client-c test run preview clean

CC = gcc
CFLAGS = -Wall -Wextra -O2

all: server client-c

server: Servidor_Cliente/servidorTicTacToe.c Servidor_Cliente/sha256.h
	$(CC) $(CFLAGS) -o Servidor_Cliente/servidor Servidor_Cliente/servidorTicTacToe.c

client-c: Servidor_Cliente/clienteTicTacToe.c
	$(CC) $(CFLAGS) -o Servidor_Cliente/cliente Servidor_Cliente/clienteTicTacToe.c

test:
	python3 -m unittest discover -s tests -v

run:
	python3 client/ticTacToe.py

preview:
	SDL_VIDEODRIVER=dummy python3 client/ticTacToe.py --preview docs

clean:
	rm -f Servidor_Cliente/servidor Servidor_Cliente/cliente tests/hash_check
