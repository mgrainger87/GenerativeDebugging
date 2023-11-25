# Variables
CC = clang
CFLAGS = -g
SOURCES = func.cpp std_thread.c io.c main.cpp
TARGET = main

# Targets and Rules
all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

clean:
	rm -f $(TARGET)
