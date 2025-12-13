//
//  chess-heuristic.h
//  chess_ai
//
//  Created by Illya Starikov on 03/18/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_CHESS_HEURISTIC_H_
#define CHESS_AI_CHESS_HEURISTIC_H_

#include <map>

#include "chess-engine.h"
#include "chess-pieces.h"
#include "color.h"
#include "state.h"

namespace ChessEngine {

template <class T>
class ChessAIHeuristic {
 public:
  static T MaterialAdvantage(const State& state, Color player_color);
};

template <class T>
T ChessAIHeuristic<T>::MaterialAdvantage(const State& state,
                                         Color player_color) {
  static std::map<Piece, int> piece_weights = {
      {kPawn, 1}, {kKnight, 3}, {kBishop, 3}, {kRook, 5}, {kQueen, 9}};

  T value = 0;

  for (const auto& element : piece_weights) {
    Piece piece = element.first;
    int piece_weight = element.second;

    int num_friendly = player_color == kWhite
                           ? state.whites_[MoveEngine::PieceToInt(piece)]
                                 .NumberOfBits()
                           : state.blacks_[MoveEngine::PieceToInt(piece)]
                                 .NumberOfBits();
    int num_enemy = player_color == kWhite
                        ? state.blacks_[MoveEngine::PieceToInt(piece)]
                              .NumberOfBits()
                        : state.whites_[MoveEngine::PieceToInt(piece)]
                              .NumberOfBits();

    T difference =
        static_cast<T>(piece_weight) * (num_friendly - num_enemy);
    value += difference;
  }

  return value;
}

}  // namespace ChessEngine

#endif  // CHESS_AI_CHESS_HEURISTIC_H_
