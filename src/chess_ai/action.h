//
//  action.h
//  chess_ai
//
//  Created by Illya Starikov on 03/02/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_ACTION_H_
#define CHESS_AI_ACTION_H_

#include <cstdint>
#include <unordered_map>

#include "bitboard.h"
#include "chess-pieces.h"
#include "color.h"

// Action bit layout:
// 0      : Color (0 = white, 1 = black)
// 1-6    : From Index
// 7-12   : To Index
// 13-15  : Unused
// 16-18  : Piece type moved (001=king, 010=pawn, 011=bishop, 100=knight,
//          101=rook, 110=queen)
// 19     : Double pawn forward flag
// 20     : Queen side castle flag
// 21     : King side castle flag
// 22     : Checking flag (will put opponent in check)
// 23-25  : Capture type (000=none, 010=pawn, 011=bishop, 100=knight,
//          101=rook, 110=queen)
// 26     : En passant flag
// 27     : Equal capture flag (capturing same piece type)
// 28-30  : Promotion type (001=none, 011=bishop, 100=knight, 101=rook,
//          110=queen)
// 31     : Winning capture flag (capture is of higher value piece)

namespace ChessEngine {

class Action {
 public:
  uint32_t Key() const { return action_; }

  Piece GetPiece() const { return ActionToPieceMoved(action_); }
  Color GetColor() const { return ActionToColor(action_); }

  Bitboard PieceBefore() const { return ActionToPieceBefore(action_); }
  Bitboard PieceAfter() const { return ActionToPieceAfter(action_); }

  bool DoublePawnForward() const { return ActionToDoublePawnForward(action_); }

  bool QueenSideCastling() const { return ActionToQueenSideCastle(action_); }
  bool KingSideCastling() const { return ActionToKingSideCastle(action_); }

  bool EnemyInCheck() const { return ActionToEnemyInCheck(action_); }

  bool WasCapture() const { return ActionToWasCapture(action_); }
  Piece PieceCaptured() const { return ActionToPieceCaptured(action_); }
  bool WasEnPassantCapture() const {
    return ActionToWasEnpassantCapture(action_);
  }

  bool WasEqualCapture() const { return ActionToWasEqualPieceCapture(action_); }

  bool WasPromotion() const { return ActionToWasPromotion(action_); }
  Piece PromotedTo() const { return ActionToPromotedTo(action_); }

  bool operator<(const Action& other) const {
    return action_ < other.action_;
  }
  bool operator>(const Action& other) const {
    return action_ > other.action_;
  }
  bool operator==(const Action& other) const {
    return action_ == other.action_;
  }

  Action(Piece piece, Color color, const Bitboard& piece_before,
         const Bitboard& piece_after, bool double_pawn_forward,
         bool queen_side_castling, bool king_side_castling, bool enemy_in_check,
         bool was_capture, bool was_en_passant_capture, Piece piece_captured,
         bool was_promotion, Piece promoted_to) {
    action_ = 0 | ColorToBitboard(color) |
              PieceBeforeToBitboard(piece_before) |
              PieceAfterToBitboard(piece_after) |
              PieceMovedToBitboard(piece) |
              DoublePawnForwardToBitboard(double_pawn_forward) |
              QueenSideCastleToBitboard(queen_side_castling) |
              KingSideCastleToBitboard(king_side_castling) |
              EnemyInCheckToBitboard(enemy_in_check) |
              PieceCapturedToBitboard(was_capture, piece_captured) |
              WasEnPassantCaptureToBitboard(was_en_passant_capture) |
              WasEqualPieceCaptureToBitboard(was_capture, piece,
                                             piece_captured) |
              PromotionToBitboard(was_promotion, promoted_to);
  }

  Action() = default;
  Action(const Action& other) = default;
  Action& operator=(const Action& other) = default;

 private:
  uint32_t action_;

  static uint32_t ColorToBitboard(Color color);
  static Color ActionToColor(uint32_t board);

  static uint32_t PieceBeforeToBitboard(const Bitboard& before);
  static Bitboard ActionToPieceBefore(uint32_t board);

  static uint32_t PieceAfterToBitboard(const Bitboard& after);
  static Bitboard ActionToPieceAfter(uint32_t board);

  static uint32_t PieceMovedToBitboard(Piece piece);
  static Piece ActionToPieceMoved(uint32_t board);

  static uint32_t DoublePawnForwardToBitboard(bool double_pawn_forward);
  static bool ActionToDoublePawnForward(uint32_t board);

  static uint32_t QueenSideCastleToBitboard(bool queen_side_castling);
  static bool ActionToQueenSideCastle(uint32_t board);

  static uint32_t KingSideCastleToBitboard(bool king_side_castling);
  static bool ActionToKingSideCastle(uint32_t board);

  static uint32_t EnemyInCheckToBitboard(bool enemy_in_check);
  static bool ActionToEnemyInCheck(uint32_t board);

  static uint32_t PieceCapturedToBitboard(bool was_capture, Piece piece);
  static Piece ActionToPieceCaptured(uint32_t board);
  static bool ActionToWasCapture(uint32_t board);

  static uint32_t WasEnPassantCaptureToBitboard(bool was_en_passant_capture);
  static bool ActionToWasEnpassantCapture(uint32_t board);

  static uint32_t WasEqualPieceCaptureToBitboard(bool was_capture, Piece piece,
                                                 Piece capture_piece);
  static bool ActionToWasEqualPieceCapture(uint32_t board);

  static uint32_t PromotionToBitboard(bool was_promotion, Piece promoted_to);
  static bool ActionToWasPromotion(uint32_t board);
  static Piece ActionToPromotedTo(uint32_t board);
};

}  // namespace ChessEngine

namespace std {

template <>
struct hash<ChessEngine::Action> {
  size_t operator()(const ChessEngine::Action& action) const {
    return static_cast<size_t>(action.Key());
  }
};

}  // namespace std

#endif  // CHESS_AI_ACTION_H_
