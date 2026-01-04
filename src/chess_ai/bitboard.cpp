//
//  bitboard.cpp
//  chess_ai
//
//  Created by Illya Starikov on 03/01/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "bitboard.h"

namespace ChessEngine {

Bitboard::Bitboard() : board_(0) {}

Bitboard::Bitboard(uint64_t board) : board_(board) {}

Bitboard& Bitboard::operator=(const Bitboard& right) {
  if (this != &right) {
    board_ = right.board_;
  }
  return *this;
}

Bitboard& Bitboard::operator=(Bitboard&& right) {
  if (this != &right) {
    board_ = right.board_;
  }
  return *this;
}

Bitboard Bitboard::operator~() const noexcept { return Bitboard(~board_); }

bool Bitboard::operator==(const Bitboard& right) const noexcept {
  return board_ == right.board_;
}

bool Bitboard::operator!=(const Bitboard& right) const noexcept {
  return !(*this == right);
}

Bitboard Bitboard::operator>>(int shift) const noexcept {
  return Bitboard(board_ >> shift);
}

Bitboard Bitboard::operator<<(int shift) const noexcept {
  return Bitboard(board_ << shift);
}

Bitboard Bitboard::operator|(const Bitboard& right) const noexcept {
  return Bitboard(board_ | right.board_);
}

Bitboard Bitboard::operator&(const Bitboard& right) const noexcept {
  return Bitboard(board_ & right.board_);
}

Bitboard Bitboard::operator^(const Bitboard& right) const noexcept {
  return Bitboard(board_ ^ right.board_);
}

Bitboard& Bitboard::operator|=(const Bitboard& right) noexcept {
  board_ |= right.board_;
  return *this;
}

Bitboard& Bitboard::operator&=(const Bitboard& right) noexcept {
  board_ &= right.board_;
  return *this;
}

Bitboard& Bitboard::operator^=(const Bitboard& right) noexcept {
  board_ ^= right.board_;
  return *this;
}

std::vector<int> Bitboard::ToIndices() const {
  std::vector<int> solution;
  int index = 0;
  uint64_t temp_board = board_;

  while (temp_board) {
    if ((temp_board & 1) == 1) {
      solution.push_back(index);
    }
    index += 1;
    temp_board = temp_board >> 1;
  }

  return solution;
}

std::vector<Bitboard> Bitboard::Separated() const {
  // If it is a power of two, it means it's a single index.
  // If so, we can do a single lookup.
  if ((board_ & (board_ - 1)) == 0) {
    return {Bitboard(board_)};
  }

  std::vector<Bitboard> solution;
  uint64_t board = 1;
  uint64_t temp_board = board_;

  while (temp_board) {
    if ((temp_board & 1) == 1) {
      solution.push_back(Bitboard(board));
    }
    temp_board = temp_board >> 1;
    board = board << 1;
  }

  return solution;
}

int Bitboard::NumberOfBits() const noexcept {
  uint64_t temp_board = board_;
  int count = 0;

  for (; temp_board; count++) {
    temp_board &= temp_board - 1;  // Clear the least significant bit set.
  }

  return count;
}

Bitboard& Bitboard::FromIndex(int index) {
  static constexpr uint64_t kIndexes[] = {
      0x1,
      0x2,
      0x4,
      0x8,
      0x10,
      0x20,
      0x40,
      0x80,
      0x100,
      0x200,
      0x400,
      0x800,
      0x1000,
      0x2000,
      0x4000,
      0x8000,
      0x10000,
      0x20000,
      0x40000,
      0x80000,
      0x100000,
      0x200000,
      0x400000,
      0x800000,
      0x1000000,
      0x2000000,
      0x4000000,
      0x8000000,
      0x10000000,
      0x20000000,
      0x40000000,
      0x80000000,
      0x100000000,
      0x200000000,
      0x400000000,
      0x800000000,
      0x1000000000,
      0x2000000000,
      0x4000000000,
      0x8000000000,
      0x10000000000,
      0x20000000000,
      0x40000000000,
      0x80000000000,
      0x100000000000,
      0x200000000000,
      0x400000000000,
      0x800000000000,
      0x1000000000000,
      0x2000000000000,
      0x4000000000000,
      0x8000000000000,
      0x10000000000000,
      0x20000000000000,
      0x40000000000000,
      0x80000000000000,
      0x100000000000000,
      0x200000000000000,
      0x400000000000000,
      0x800000000000000,
      0x1000000000000000,
      0x2000000000000000,
      0x4000000000000000,
      0x8000000000000000};

  board_ = kIndexes[index];
  return *this;
}

}  // namespace ChessEngine

std::ostream& operator<<(std::ostream& os, const ChessEngine::Bitboard& object) {
  os << object.GetRawBinary().to_string();
  return os;
}
