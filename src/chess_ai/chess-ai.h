//
//  chess-ai.h
//  chess_ai
//
//  Created by Illya Starikov on 03/06/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_CHESS_AI_H_
#define CHESS_AI_CHESS_AI_H_

#include <algorithm>
#include <functional>
#include <limits>
#include <map>
#include <memory>
#include <numeric>
#include <random>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include "action.h"
#include "bitboard.h"
#include "chess-engine.h"
#include "chess-heuristic.h"
#include "chess-history.h"
#include "chess-outcome.h"
#include "color.h"
#include "fen-parser.h"
#include "move-time-calculator.h"
#include "state.h"
#include "timer.h"

namespace ChessEngine {

class ChessAI {
 public:
  // Static flag for "worst moves" mode - inverts the evaluation function
  // to make the AI pick the worst possible moves.
  static bool worst_mode_;
  static void SetWorstMode(bool enabled) { worst_mode_ = enabled; }

  // Public members are initialized first to avoid warnings about
  // initialization order. Parser must come before current_state_ since
  // current_state_ uses parser_ during initialization.
  FenParser parser_;
  State current_state_;
  Color self_color_;

  explicit ChessAI(const std::string& fen_string);

  ChessAI() = delete;
  ChessAI(const ChessAI& other) = delete;
  ChessAI(ChessAI&& other) = delete;
  ChessAI& operator=(const ChessAI& other) = delete;
  ChessAI& operator=(ChessAI&& other) = delete;

  // AI operations
  static State InitialState();
  static std::vector<Action> Actions(const State& state);
  static State Result(const State& state, const Action& action);

  static ChessOutcome TerminalTest(const State& state,
                                   const PerceptSequence& history);
  static float UtilityFunction(const State& state, Color friendly_color,
                               const PerceptSequence& history);
  static float UtilityHeuristic(const State& state, Color friendly_color);

  void UpdateTimer(double time_remaining_seconds);
  void UpdateMove(const Action& action);

  Action Minimax(double time_limit, const State& state,
                 const PerceptSequence& history);
  Action Move();

 private:
  MoveTimeCalculator time_calculator_;

  PerceptSequence history_;
  Timer move_timer_;

  double time_remaining_;  // in seconds
  int half_move_number_;

  static bool WasCapture(const Bitboard& enemy_bitboard, const Bitboard& move);
  static Piece FindCapturePiece(const std::vector<Bitboard>& enemy_bitboards,
                                const Bitboard& enemy_bitboard,
                                const Bitboard& move);

  static Bitboard EnpassantMoveGenerator(const Bitboard& en_passant_squares,
                                         const Bitboard& pawn,
                                         Color friendly_color);
  static Bitboard CastlingMoveGenerator(const Bitboard& all_whites,
                                        const Bitboard& all_blacks,
                                        const Bitboard& castling_squares,
                                        const Bitboard& rook);
  static Bitboard KingLocationAfterCastling(const Bitboard& rook_after);

  static bool IsEightfoldRepetitionRule(const PerceptSequence& from_history);
  static bool InsufficientMaterial(const State& current_state);
  static bool FiftyMoveRule(const PerceptSequence& history);

  std::shared_ptr<Action> DepthLimitedMinimax(
      int depth_limit, int quiescence_limit, double time_limit,
      const State& state, std::map<Action, int>& history_table,
      const PerceptSequence& history);
  std::shared_ptr<float> MaxValue(int depth_limit, int quiescence_limit,
                                  double time_limit, const State& state,
                                  const Action& action, float alpha, float beta,
                                  Color color,
                                  std::map<Action, int>& history_table,
                                  const PerceptSequence& history);
  std::shared_ptr<float> MinValue(int depth_limit, int quiescence_limit,
                                  double time_limit, const State& state,
                                  const Action& action, float alpha, float beta,
                                  Color color,
                                  std::map<Action, int>& history_table,
                                  const PerceptSequence& history);

  void AddToHistoryTable(std::map<Action, int>& history_table,
                         const Action& action);

  static State FlipColorAtPlay(State state) {
    state.color_at_play_ = static_cast<Color>((state.color_at_play_ + 1) % 2);
    return state;
  }

  static bool IsNonQuiescenceState(const Action& action) {
    return action.WasCapture() || action.WasPromotion() || action.EnemyInCheck();
  }
};

}  // namespace ChessEngine

#endif  // CHESS_AI_CHESS_AI_H_
