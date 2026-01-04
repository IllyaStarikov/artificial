//
//  chess-engine.cpp
//  chess_ai
//
//  Created by Illya Starikov on 02/26/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "chess-engine.h"

namespace ChessEngine {

Bitboard MoveEngine::NorthMovesWithBlockers(Bitboard board,
                                            const Bitboard& blocker_inverse) {
  Bitboard result = board;

  // Move the board north until reaching a blocker. The blockers are inverted,
  // so blocking squares will be zero. Using bitwise AND, the movement stops
  // at the blocker. We shift 7 times for the board length minus current piece.
  result |= board = (board << 8) & blocker_inverse;
  result |= board = (board << 8) & blocker_inverse;
  result |= board = (board << 8) & blocker_inverse;
  result |= board = (board << 8) & blocker_inverse;
  result |= board = (board << 8) & blocker_inverse;
  result |= board = (board << 8) & blocker_inverse;
  result |= board = (board << 8) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::SouthMovesWithBlockers(Bitboard board,
                                            const Bitboard& blocker_inverse) {
  Bitboard result = board;

  result |= board = (board >> 8) & blocker_inverse;
  result |= board = (board >> 8) & blocker_inverse;
  result |= board = (board >> 8) & blocker_inverse;
  result |= board = (board >> 8) & blocker_inverse;
  result |= board = (board >> 8) & blocker_inverse;
  result |= board = (board >> 8) & blocker_inverse;
  result |= board = (board >> 8) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::EastMovesWithBlockers(Bitboard board,
                                           const Bitboard& blocker_inverse) {
  const Bitboard kAFileInverse(0xfefefefefefefefe);

  // Consider wraparound for east/west movement.
  Bitboard result = board;
  Bitboard blocker_and_file_inverse = blocker_inverse & kAFileInverse;

  result |= board = (board << 1) & blocker_and_file_inverse;
  result |= board = (board << 1) & blocker_and_file_inverse;
  result |= board = (board << 1) & blocker_and_file_inverse;
  result |= board = (board << 1) & blocker_and_file_inverse;
  result |= board = (board << 1) & blocker_and_file_inverse;
  result |= board = (board << 1) & blocker_and_file_inverse;
  result |= board = (board << 1) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::WestMovesWithBlockers(Bitboard board,
                                           const Bitboard& blocker_inverse) {
  const Bitboard kHFileInverse(0x7f7f7f7f7f7f7f7f);

  Bitboard result = board;
  Bitboard blocker_and_file_inverse = blocker_inverse & kHFileInverse;

  result |= board = (board >> 1) & blocker_and_file_inverse;
  result |= board = (board >> 1) & blocker_and_file_inverse;
  result |= board = (board >> 1) & blocker_and_file_inverse;
  result |= board = (board >> 1) & blocker_and_file_inverse;
  result |= board = (board >> 1) & blocker_and_file_inverse;
  result |= board = (board >> 1) & blocker_and_file_inverse;
  result |= board = (board >> 1) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::NortheastMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  const Bitboard kAFileInverse(0xfefefefefefefefe);

  Bitboard result = board;
  Bitboard blocker_and_file_inverse = blocker_inverse & kAFileInverse;

  result |= board = (board << 9) & blocker_and_file_inverse;
  result |= board = (board << 9) & blocker_and_file_inverse;
  result |= board = (board << 9) & blocker_and_file_inverse;
  result |= board = (board << 9) & blocker_and_file_inverse;
  result |= board = (board << 9) & blocker_and_file_inverse;
  result |= board = (board << 9) & blocker_and_file_inverse;
  result |= board = (board << 9) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::NorthwestMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  const Bitboard kHFileInverse(0x7f7f7f7f7f7f7f7f);

  Bitboard result = board;
  Bitboard blocker_and_file_inverse = blocker_inverse & kHFileInverse;

  result |= board = (board << 7) & blocker_and_file_inverse;
  result |= board = (board << 7) & blocker_and_file_inverse;
  result |= board = (board << 7) & blocker_and_file_inverse;
  result |= board = (board << 7) & blocker_and_file_inverse;
  result |= board = (board << 7) & blocker_and_file_inverse;
  result |= board = (board << 7) & blocker_and_file_inverse;
  result |= board = (board << 7) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::SoutheastMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  const Bitboard kAFileInverse(0xfefefefefefefefe);

  Bitboard result = board;
  Bitboard blocker_and_file_inverse = blocker_inverse & kAFileInverse;

  result |= board = (board >> 7) & blocker_and_file_inverse;
  result |= board = (board >> 7) & blocker_and_file_inverse;
  result |= board = (board >> 7) & blocker_and_file_inverse;
  result |= board = (board >> 7) & blocker_and_file_inverse;
  result |= board = (board >> 7) & blocker_and_file_inverse;
  result |= board = (board >> 7) & blocker_and_file_inverse;
  result |= board = (board >> 7) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::SouthwestMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  const Bitboard kHFileInverse(0x7f7f7f7f7f7f7f7f);

  Bitboard result = board;
  Bitboard blocker_and_file_inverse = blocker_inverse & kHFileInverse;

  result |= board = (board >> 9) & blocker_and_file_inverse;
  result |= board = (board >> 9) & blocker_and_file_inverse;
  result |= board = (board >> 9) & blocker_and_file_inverse;
  result |= board = (board >> 9) & blocker_and_file_inverse;
  result |= board = (board >> 9) & blocker_and_file_inverse;
  result |= board = (board >> 9) & blocker_and_file_inverse;
  result |= board = (board >> 9) & blocker_inverse;

  return result;
}

Bitboard MoveEngine::PawnNorthMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  Bitboard result = board;
  result |= board = (board << 8) & blocker_inverse;
  return result;
}

Bitboard MoveEngine::PawnNorthNorthMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  Bitboard result = board;
  result |= board = (board << 8) & blocker_inverse;
  result |= board = (board << 8) & blocker_inverse;
  return result;
}

Bitboard MoveEngine::PawnSouthMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  Bitboard result = board;
  result |= board = (board >> 8) & blocker_inverse;
  return result;
}

Bitboard MoveEngine::PawnSouthSouthMovesWithBlockers(
    Bitboard board, const Bitboard& blocker_inverse) {
  Bitboard result = board;
  result |= board = (board >> 8) & blocker_inverse;
  result |= board = (board >> 8) & blocker_inverse;
  return result;
}

std::vector<std::pair<char, int>> MoveEngine::BitStringToDescription(
    Bitboard board) {
  std::vector<int> indices = board.ToIndices();
  std::vector<std::pair<char, int>> solution;

  for (int index : indices) {
    // Convert index to file (A-H) and rank (1-8).
    // File is horizontal, rank increases vertically.
    char file = static_cast<char>(static_cast<int>(index % 8) + 65);
    int rank = static_cast<int>(index / 8.0 + 1.0);

    solution.push_back(std::make_pair(file, rank));
  }

  return solution;
}

int MoveEngine::PieceToInt(Piece piece) { return static_cast<int>(piece); }

Piece MoveEngine::IntToPiece(int integer) {
  return static_cast<Piece>(integer);
}

void MoveEngine::GenerateInitialState(std::vector<Bitboard>& white,
                                      std::vector<Bitboard>& black) {
  // Hand-calculated values for the initial chess state.
  white[PieceToInt(kKing)] = Bitboard().FromIndex(4);
  white[PieceToInt(kQueen)] = Bitboard().FromIndex(3);
  white[PieceToInt(kRook)] =
      Bitboard().FromIndex(0) | Bitboard().FromIndex(7);
  white[PieceToInt(kBishop)] =
      Bitboard().FromIndex(2) | Bitboard().FromIndex(5);
  white[PieceToInt(kKnight)] =
      Bitboard().FromIndex(1) | Bitboard().FromIndex(6);
  white[PieceToInt(kPawn)] =
      Bitboard().FromIndex(8) | Bitboard().FromIndex(9) |
      Bitboard().FromIndex(10) | Bitboard().FromIndex(11) |
      Bitboard().FromIndex(12) | Bitboard().FromIndex(13) |
      Bitboard().FromIndex(14) | Bitboard().FromIndex(15);

  black[PieceToInt(kKing)] = Bitboard().FromIndex(60);
  black[PieceToInt(kQueen)] = Bitboard().FromIndex(59);
  black[PieceToInt(kRook)] =
      Bitboard().FromIndex(56) | Bitboard().FromIndex(63);
  black[PieceToInt(kBishop)] =
      Bitboard().FromIndex(58) | Bitboard().FromIndex(61);
  black[PieceToInt(kKnight)] =
      Bitboard().FromIndex(57) | Bitboard().FromIndex(62);
  black[PieceToInt(kPawn)] =
      Bitboard().FromIndex(48) | Bitboard().FromIndex(49) |
      Bitboard().FromIndex(50) | Bitboard().FromIndex(51) |
      Bitboard().FromIndex(52) | Bitboard().FromIndex(53) |
      Bitboard().FromIndex(54) | Bitboard().FromIndex(55);
}

Bitboard MoveEngine::AllBitboardsInOneBoard(std::vector<Bitboard> boards) {
  return boards[static_cast<int>(kKing)] | boards[static_cast<int>(kQueen)] |
         boards[static_cast<int>(kRook)] | boards[static_cast<int>(kBishop)] |
         boards[static_cast<int>(kKnight)] | boards[static_cast<int>(kPawn)];
}

Bitboard MoveEngine::Moving(const Bitboard& board, Direction direction) {
  // Prevent wraps when bit shifting (e.g., 1H cannot move to 2A).
  const Bitboard kAFileInverse(0xfefefefefefefefe);
  const Bitboard kHFileInverse(0x7f7f7f7f7f7f7f7f);

  // Indexing starts at bottom left (A1) and goes right until wrap.
  // The next level is one row above. Board layout:
  // 9.......
  // 12345678
  // Moving up: bit shift 8 left (LSB is on the right in binary strings).
  switch (direction) {
    case kNorth:
      return board << 8;
    case kSouth:
      return board >> 8;
    case kEast:
      return (board << 1) & kAFileInverse;
    case kWest:
      return (board >> 1) & kHFileInverse;
    case kNortheast:
      return (board << 9) & kAFileInverse;
    case kNorthwest:
      return (board << 7) & kHFileInverse;
    case kSoutheast:
      return (board >> 7) & kAFileInverse;
    case kSouthwest:
      return (board >> 9) & kHFileInverse;
    default:
      return Bitboard();
  }
}

Bitboard MoveEngine::KingMoves(const Bitboard& king, const Bitboard& self) {
  // The ~self ensures we do not move over our own piece.
  return (Moving(king, kNorth) | Moving(king, kSouth) | Moving(king, kEast) |
          Moving(king, kWest) | Moving(king, kNortheast) |
          Moving(king, kNorthwest) | Moving(king, kSoutheast) |
          Moving(king, kSouthwest)) &
         (~self);
}

Bitboard MoveEngine::KnightMoves(const Bitboard& knight, const Bitboard& self) {
  const Bitboard kAFileInverse(0xfefefefefefefefe);
  const Bitboard kHFileInverse(0x7f7f7f7f7f7f7f7f);
  const Bitboard kAbFileInverse(0xfcfcfcfcfcfcfcfc);
  const Bitboard kGhFileInverse(0x3f3f3f3f3f3f3f3f);

  return (((knight << 17) & kAFileInverse) |
          ((knight >> 15) & kAFileInverse) |
          ((knight << 15) & kHFileInverse) |
          ((knight >> 17) & kHFileInverse) |
          ((knight << 10) & kAbFileInverse) |
          ((knight >> 6) & kAbFileInverse) |
          ((knight >> 10) & kGhFileInverse) |
          ((knight << 6) & kGhFileInverse)) &
         (~self);
}

Bitboard MoveEngine::RookMoves(const Bitboard& rook, Bitboard self,
                               Bitboard enemy) {
  self = ~self;
  enemy = ~enemy;

  return (NorthMovesWithBlockers(rook, self & Moving(enemy, kNorth)) |
          SouthMovesWithBlockers(rook, self & Moving(enemy, kSouth)) |
          WestMovesWithBlockers(rook, self & Moving(enemy, kWest)) |
          EastMovesWithBlockers(rook, self & Moving(enemy, kEast))) ^
         rook;
}

Bitboard MoveEngine::BishopMoves(const Bitboard& bishop, Bitboard self,
                                 Bitboard enemy) {
  self = ~self;
  enemy = ~enemy;

  return (NortheastMovesWithBlockers(bishop,
                                     self & Moving(enemy, kNortheast)) |
          NorthwestMovesWithBlockers(bishop,
                                     self & Moving(enemy, kNorthwest)) |
          SoutheastMovesWithBlockers(bishop,
                                     self & Moving(enemy, kSoutheast)) |
          SouthwestMovesWithBlockers(bishop,
                                     self & Moving(enemy, kSouthwest))) ^
         bishop;
}

Bitboard MoveEngine::QueenMoves(const Bitboard& queen, Bitboard self,
                                Bitboard enemy) {
  self = ~self;
  enemy = ~enemy;

  return (NorthMovesWithBlockers(queen, self & Moving(enemy, kNorth)) |
          SouthMovesWithBlockers(queen, self & Moving(enemy, kSouth)) |
          WestMovesWithBlockers(queen, self & Moving(enemy, kWest)) |
          EastMovesWithBlockers(queen, self & Moving(enemy, kEast)) |
          NortheastMovesWithBlockers(queen,
                                     self & Moving(enemy, kNortheast)) |
          NorthwestMovesWithBlockers(queen,
                                     self & Moving(enemy, kNorthwest)) |
          SoutheastMovesWithBlockers(queen,
                                     self & Moving(enemy, kSoutheast)) |
          SouthwestMovesWithBlockers(queen,
                                     self & Moving(enemy, kSouthwest))) ^
         queen;
}

Bitboard MoveEngine::PawnMoves(const Bitboard& pawn, Bitboard self,
                               Bitboard enemy, Color self_color) {
  const Bitboard enemy_original = enemy;

  self = ~self;
  enemy = ~enemy;

  const Bitboard kSecondRank(0xff00);
  const Bitboard kSeventhRank(0xff000000000000);

  if (self_color == kWhite) {
    return (PawnNorthMovesWithBlockers(pawn, self & enemy) |
            PawnNorthNorthMovesWithBlockers(pawn & kSecondRank, self & enemy) |
            (Moving(pawn, kNortheast) & enemy_original) |
            (Moving(pawn, kNorthwest) & enemy_original)) ^
           pawn;
  } else {
    return (PawnSouthMovesWithBlockers(pawn, self & enemy) |
            PawnSouthSouthMovesWithBlockers(pawn & kSeventhRank, self & enemy) |
            (Moving(pawn, kSoutheast) & enemy_original) |
            (Moving(pawn, kSouthwest) & enemy_original)) ^
           pawn;
  }
}

Bitboard MoveEngine::CastlingMoves(const Bitboard& castling_squares,
                                   const Bitboard& all_white,
                                   const Bitboard& all_blacks) {
  const Bitboard kLongCastling(0x01);
  const Bitboard kShortCastling(0x08);
  const Bitboard kLongCastlingObstacles(0x0e);
  const Bitboard kShortCastlingObstacles(0x60);

  Bitboard obstacles = all_blacks | all_white;
  Bitboard short_castling_from = castling_squares & kShortCastling;
  Bitboard long_castling_from = castling_squares & kLongCastling;

  Bitboard result;

  // Calculate all castling squares (both white and black).
  if ((obstacles & kLongCastlingObstacles) == Bitboard(0) &&
      (long_castling_from & kLongCastling) != Bitboard(0)) {
    result |= kLongCastling;
  }

  if ((obstacles & kShortCastlingObstacles) == Bitboard(0) &&
      (short_castling_from & kShortCastling) != Bitboard(0)) {
    result |= kShortCastling;
  }

  return result;
}

Bitboard MoveEngine::EnpassantMoves(const Bitboard& enemy_enpassant_squares,
                                    const Bitboard& self_pawns) {
  // Check if an en passant square is next to one of our pawns.
  return (Moving(enemy_enpassant_squares, kEast) & self_pawns) |
         (Moving(enemy_enpassant_squares, kWest) & self_pawns);
}

}  // namespace ChessEngine
