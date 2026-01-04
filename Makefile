CC = gcc
CFLAGS = -O2 -std=c11 -Wall -fPIC
TARGET_SO = libstudentdsa.so
TARGET_DLL = studentdsa.dll
SRC = student_dsa_shared.c

all: $(TARGET_SO)

$(TARGET_SO): $(SRC) student_dsa_shared.h
	$(CC) $(CFLAGS) -shared -o $(TARGET_SO) $(SRC)

# Windows (MinGW) target (optional)
$(TARGET_DLL): $(SRC) student_dsa_shared.h
	$(CC) -O2 -shared -o $(TARGET_DLL) $(SRC)

clean:
	rm -f $(TARGET_SO) $(TARGET_DLL) *.o
