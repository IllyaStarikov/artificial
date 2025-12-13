//
//  bitboard.h
//  chess_ai
//
//  Created by Illya Starikov on 03/01/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_BITBOARD_H_
#define CHESS_AI_BITBOARD_H_

#include <bitset>
#include <cstdint>
#include <ostream>
#include <vector>

namespace ChessEngine {

class Bitboard;

}  // namespace ChessEngine

std::ostream& operator<<(std::ostream& os, const ChessEngine::Bitboard& object);

namespace ChessEngine {

class Bitboard {
 public:
  uint64_t board_;

  Bitboard();
  explicit Bitboard(uint64_t board);
  Bitboard(const Bitboard& board) = default;
  Bitboard(Bitboard&& board) = default;

  Bitboard& operator=(const Bitboard& right);
  Bitboard& operator=(Bitboard&& right);

  bool operator==(const Bitboard& right) const noexcept;
  bool operator!=(const Bitboard& right) const noexcept;
  Bitboard operator>>(int shift) const noexcept;
  Bitboard operator<<(int shift) const noexcept;

  Bitboard operator~() const noexcept;
  Bitboard operator|(const Bitboard& right) const noexcept;
  Bitboard operator&(const Bitboard& right) const noexcept;
  Bitboard operator^(const Bitboard& right) const noexcept;

  Bitboard& operator|=(const Bitboard& right) noexcept;
  Bitboard& operator&=(const Bitboard& right) noexcept;
  Bitboard& operator^=(const Bitboard& right) noexcept;

  std::vector<int> ToIndices() const;
  Bitboard& FromIndex(int index);

  std::vector<Bitboard> Separated() const;
  int NumberOfBits() const noexcept;

  std::bitset<64> GetRawBinary() const noexcept {
    return std::bitset<64>(board_);
  }

  friend std::ostream& ::operator<<(std::ostream& os, const Bitboard& object);
};

}  // namespace ChessEngine

#endif  // CHESS_AI_BITBOARD_H_
