# Variables
CC = clang
CFLAGS = -g
SOURCES = funca.c funce.c std_thread.c io.c funcb.c funcc.c main.c funcd.c
TARGET = main

# Targets and Rules
all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

clean:
	rm -f $(TARGET)
