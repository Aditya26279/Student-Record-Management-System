# ============================================================
# Makefile — Student Record Management System (C modules)
# ============================================================

CC      = gcc
CFLAGS  = -Wall -Wextra -O2 -std=c11
TARGET  = srms_test
SRCS    = main.c linked_list.c bst.c hash_table.c sorting.c searching.c file_ops.c
OBJS    = $(SRCS:.c=.o)

# ── Default target ───────────────────────────────────────────────────────────
.PHONY: all
all: $(TARGET)
	@echo "Build successful → ./$(TARGET)"

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ -lm

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

# ── Run tests ────────────────────────────────────────────────────────────────
.PHONY: run
run: all
	./$(TARGET)

# ── Clean ────────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	del /Q *.o $(TARGET).exe 2>nul || rm -f *.o $(TARGET)

# ── Dependencies ─────────────────────────────────────────────────────────────
main.o:        main.c student.h linked_list.h bst.h hash_table.h sorting.h searching.h file_ops.h
linked_list.o: linked_list.c linked_list.h student.h
bst.o:         bst.c bst.h student.h
hash_table.o:  hash_table.c hash_table.h student.h
sorting.o:     sorting.c sorting.h student.h
searching.o:   searching.c searching.h student.h sorting.h
file_ops.o:    file_ops.c file_ops.h student.h
