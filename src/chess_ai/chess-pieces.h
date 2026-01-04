//
//  chess-pieces.h
//  chess_ai
//
//  Created by Illya Starikov on 02/26/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_CHESS_PIECES_H_
#define CHESS_AI_CHESS_PIECES_H_

#include <cstddef>

namespace ChessEngine {

enum Piece {
  kKing = 0,
  kQueen = 1,
  kRook = 2,
  kBishop = 3,
  kKnight = 4,
  kPawn = 5
};

}  // namespace ChessEngine

namespace std {

template <>
struct hash<ChessEngine::Piece> {
  size_t operator()(const ChessEngine::Piece& piece) const {
    return static_cast<size_t>(piece);
  }
};

}  // namespace std

#endif  // CHESS_AI_CHESS_PIECES_H_
