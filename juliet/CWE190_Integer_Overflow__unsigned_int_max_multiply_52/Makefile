# Variables
CC = clang
CFLAGS = -g
SOURCES = funca.c std_thread.c io.c main.c
TARGET = main

# Targets and Rules
all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

clean:
	rm -f $(TARGET)
