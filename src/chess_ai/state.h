//
//  state.h
//  chess_ai
//
//  Created by Illya Starikov on 03/06/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_STATE_H_
#define CHESS_AI_STATE_H_

#include <algorithm>
#include <iostream>
#include <map>
#include <ostream>
#include <sstream>
#include <vector>

#include "bitboard.h"
#include "chess-engine.h"
#include "chess-pieces.h"
#include "color.h"

namespace ChessEngine {

class State;

}  // namespace ChessEngine

std::ostream& operator<<(std::ostream& os, const ChessEngine::State& object);

namespace ChessEngine {

class State {
 public:
  Color color_at_play_;

  Bitboard all_whites_;
  Bitboard all_blacks_;

  std::vector<Bitboard> whites_;
  std::vector<Bitboard> blacks_;

  Bitboard en_passant_squares_;
  Bitboard castling_squares_;

  State(Color color_at_play, const Bitboard& all_whites,
        const Bitboard& all_blacks, const std::vector<Bitboard>& whites,
        const std::vector<Bitboard>& blacks, const Bitboard& en_passant_squares,
        const Bitboard& castling_squares)
      : color_at_play_(color_at_play),
        all_whites_(all_whites),
        all_blacks_(all_blacks),
        whites_(whites),
        blacks_(blacks),
        en_passant_squares_(en_passant_squares),
        castling_squares_(castling_squares) {}

  bool operator==(const State& other) const noexcept;
  bool operator!=(const State& other) const noexcept;

  void Print() { std::cout << *this; }
  friend std::ostream& ::operator<<(std::ostream& os, const State& object);
};

}  // namespace ChessEngine

#endif  // CHESS_AI_STATE_H_
