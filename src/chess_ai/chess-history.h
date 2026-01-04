//
//  chess-history.h
//  chess_ai
//
//  Created by Illya Starikov on 03/20/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_CHESS_HISTORY_H_
#define CHESS_AI_CHESS_HISTORY_H_

#include <deque>

#include "constants.h"
#include "state.h"

namespace ChessEngine {

class PerceptSequence {
 public:
  void Add(const State& state) {
    if (state_history_.size() > kMaxHistory) {
      state_history_.pop_front();
    }
    state_history_.push_back(state);
  }

  void Add(const Action& action) {
    moves_since_capture_ = action.WasCapture() ? moves_since_capture_ + 1 : 0;
    moves_since_pawn_movement_ =
        action.GetPiece() == kPawn ? moves_since_pawn_movement_ + 1 : 0;
  }

  const State operator[](int index) const { return state_history_[index]; }

  int MovesSincePawnMovement() const noexcept {
    return moves_since_pawn_movement_;
  }

  int MovesSinceCapture() const noexcept { return moves_since_capture_; }

  size_t Size() const noexcept { return state_history_.size(); }

 private:
  std::deque<State> state_history_;
  int moves_since_capture_ = 0;
  int moves_since_pawn_movement_ = 0;
};

}  // namespace ChessEngine

#endif  // CHESS_AI_CHESS_HISTORY_H_
