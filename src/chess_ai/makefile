# Chess AI Makefile
# Standalone chess engine with minimax + alpha-beta pruning

CXX = g++
CXXFLAGS = -std=c++17 -O3 -Wall -Wextra

# Source files
SRCS = main.cpp \
       chess-ai.cpp \
       chess-engine.cpp \
       action.cpp \
       bitboard.cpp \
       fen-parser.cpp \
       state.cpp \
       timer.cpp \
       move-time-calculator.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Target executable
TARGET = chess_ai

# Default target
all: $(TARGET)

# Link object files to create executable
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Compile source files to object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Clean build artifacts
clean:
	rm -f $(OBJS) $(TARGET)

# Run the program
run: $(TARGET)
	./$(TARGET)

# Build with debug symbols
debug: CXXFLAGS = -std=c++17 -g -Wall -Wextra -DDEBUG
debug: clean all

.PHONY: all clean run debug
