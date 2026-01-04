//
//  state.cpp
//  chess_ai
//
//  Created by Illya Starikov on 03/07/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "state.h"

namespace ChessEngine {

bool State::operator==(const State& other) const noexcept {
  return color_at_play_ == other.color_at_play_ &&
         all_whites_ == other.all_whites_ &&
         all_blacks_ == other.all_blacks_ && whites_ == other.whites_ &&
         blacks_ == other.blacks_ &&
         en_passant_squares_ == other.en_passant_squares_ &&
         castling_squares_ == other.castling_squares_;
}

bool State::operator!=(const State& other) const noexcept {
  return !(*this == other);
}

}  // namespace ChessEngine

std::ostream& operator<<(std::ostream& os, const ChessEngine::State& object) {
  static std::map<ChessEngine::Piece, char> piece_to_char{
      {ChessEngine::kKing, 'K'},   {ChessEngine::kQueen, 'Q'},
      {ChessEngine::kKnight, 'N'}, {ChessEngine::kRook, 'R'},
      {ChessEngine::kBishop, 'B'}, {ChessEngine::kPawn, 'P'}};

  std::map<int, char> mappings;

  for (int i = 0; i < 6; i++) {
    for (int index : object.whites_[i].ToIndices()) {
      mappings[index] =
          toupper(piece_to_char[ChessEngine::MoveEngine::IntToPiece(i)]);
    }

    for (int index : object.blacks_[i].ToIndices()) {
      mappings[index] =
          tolower(piece_to_char[ChessEngine::MoveEngine::IntToPiece(i)]);
    }
  }

  std::stringstream ss;

  for (int i = 63; i >= 0; i--) {
    if (i == 63) {
      os << "    +------------------------+";
    }

    if ((i + 1) % 8 == 0) {
      std::string str = ss.str();
      std::reverse(str.begin(), str.end());

      os << str;
      os << "\n " << static_cast<int>(i / 8 + 1) << " | ";

      ss.str("");
      ss.clear();
    }

    if (mappings.find(i) == mappings.end()) {
      ss << " . ";
    } else {
      ss << " " << mappings[i] << " ";
    }

    if (i == 0) {
      std::string str = ss.str();
      std::reverse(str.begin(), str.end());

      os << str;
      os << "\n    +------------------------+";
      os << "\n      a  b  c  d  e  f  g  h\n";
    }
  }

  return os;
}
