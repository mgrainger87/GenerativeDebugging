# Variables
CC = clang
CFLAGS = -g
SOURCES = std_thread.c io.c func_bad.cpp main.cpp
TARGET = main

# Targets and Rules
all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

clean:
	rm -f $(TARGET)
