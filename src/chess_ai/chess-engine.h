//
//  chess-engine.h
//  chess_ai
//
//  Created by Illya Starikov on 02/26/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_CHESS_ENGINE_H_
#define CHESS_AI_CHESS_ENGINE_H_

#include <cstdint>
#include <map>
#include <utility>
#include <vector>

#include "action.h"
#include "bitboard.h"
#include "chess-pieces.h"
#include "color.h"
#include "direction.h"

namespace ChessEngine {

class MoveEngine {
 public:
  static int PieceToInt(Piece piece);
  static Piece IntToPiece(int integer);
  static std::vector<std::pair<char, int>> BitStringToDescription(
      Bitboard board);

  static void GenerateInitialState(std::vector<Bitboard>& white,
                                   std::vector<Bitboard>& black);
  static Bitboard AllBitboardsInOneBoard(std::vector<Bitboard> boards);

  static Bitboard AllStandardMovesInOneBitboard(
      const std::vector<Bitboard>& self_pieces, const Bitboard& self,
      const Bitboard& enemy, Color self_color) {
    return KingMoves(self_pieces[static_cast<int>(kKing)], self) |
           QueenMoves(self_pieces[static_cast<int>(kQueen)], self, enemy) |
           RookMoves(self_pieces[static_cast<int>(kRook)], self, enemy) |
           BishopMoves(self_pieces[static_cast<int>(kBishop)], self, enemy) |
           KnightMoves(self_pieces[static_cast<int>(kKnight)], self) |
           PawnMoves(self_pieces[static_cast<int>(kPawn)], self, enemy,
                     self_color);
  }

  static Bitboard Moving(const Bitboard& board, Direction direction);

  // Non-sliding pieces
  static Bitboard KingMoves(const Bitboard& king, const Bitboard& self);
  static Bitboard KnightMoves(const Bitboard& knight, const Bitboard& self);

  // Sliding pieces
  static Bitboard RookMoves(const Bitboard& rook, Bitboard self,
                            Bitboard enemy);
  static Bitboard BishopMoves(const Bitboard& bishop, Bitboard self,
                              Bitboard enemy);
  static Bitboard QueenMoves(const Bitboard& queen, Bitboard self,
                             Bitboard enemy);

  // Pawn moves
  static Bitboard PawnMoves(const Bitboard& pawn, Bitboard self, Bitboard enemy,
                            Color self_color);
  static Bitboard EnpassantMoves(const Bitboard& enemy_enpassant_squares,
                                 const Bitboard& self_pawns);

  // Castling
  static Bitboard CastlingMoves(const Bitboard& castling_squares,
                                const Bitboard& all_white,
                                const Bitboard& all_blacks);

 private:
  static Bitboard NorthMovesWithBlockers(Bitboard board,
                                         const Bitboard& blocker_inverse);
  static Bitboard SouthMovesWithBlockers(Bitboard board,
                                         const Bitboard& blocker_inverse);
  static Bitboard EastMovesWithBlockers(Bitboard board,
                                        const Bitboard& blocker_inverse);
  static Bitboard WestMovesWithBlockers(Bitboard board,
                                        const Bitboard& blocker_inverse);
  static Bitboard NortheastMovesWithBlockers(Bitboard board,
                                             const Bitboard& blocker_inverse);
  static Bitboard NorthwestMovesWithBlockers(Bitboard board,
                                             const Bitboard& blocker_inverse);
  static Bitboard SoutheastMovesWithBlockers(Bitboard board,
                                             const Bitboard& blocker_inverse);
  static Bitboard SouthwestMovesWithBlockers(Bitboard board,
                                             const Bitboard& blocker_inverse);

  static Bitboard PawnNorthMovesWithBlockers(Bitboard board,
                                             const Bitboard& blocker_inverse);
  static Bitboard PawnNorthNorthMovesWithBlockers(
      Bitboard board, const Bitboard& blocker_inverse);
  static Bitboard PawnSouthMovesWithBlockers(Bitboard board,
                                             const Bitboard& blocker_inverse);
  static Bitboard PawnSouthSouthMovesWithBlockers(
      Bitboard board, const Bitboard& blocker_inverse);
};

}  // namespace ChessEngine

#endif  // CHESS_AI_CHESS_ENGINE_H_
