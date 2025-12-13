//
//  action.cpp
//  chess_ai
//
//  Created by Illya Starikov on 04/01/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "action.h"

namespace ChessEngine {

uint32_t Action::ColorToBitboard(Color color) {
  static std::unordered_map<Color, uint32_t> mappings = {{kWhite, 0x00},
                                                         {kBlack, 0x01}};
  return mappings[color];
}

Color Action::ActionToColor(uint32_t board) {
  static std::unordered_map<uint32_t, Color> mappings = {{0x00, kWhite},
                                                         {0x01, kBlack}};
  return mappings[board & 0x01];
}

uint32_t Action::PieceBeforeToBitboard(const Bitboard& before) {
  static std::unordered_map<uint64_t, uint32_t> mappings = {
      {0x01, 0x00},
      {0x02, 0x02},
      {0x04, 0x04},
      {0x08, 0x06},
      {0x10, 0x08},
      {0x20, 0x0a},
      {0x40, 0x0c},
      {0x80, 0x0e},
      {0x100, 0x10},
      {0x200, 0x12},
      {0x400, 0x14},
      {0x800, 0x16},
      {0x1000, 0x18},
      {0x2000, 0x1a},
      {0x4000, 0x1c},
      {0x8000, 0x1e},
      {0x10000, 0x20},
      {0x20000, 0x22},
      {0x40000, 0x24},
      {0x80000, 0x26},
      {0x100000, 0x28},
      {0x200000, 0x2a},
      {0x400000, 0x2c},
      {0x800000, 0x2e},
      {0x1000000, 0x30},
      {0x2000000, 0x32},
      {0x4000000, 0x34},
      {0x8000000, 0x36},
      {0x10000000, 0x38},
      {0x20000000, 0x3a},
      {0x40000000, 0x3c},
      {0x80000000, 0x3e},
      {0x100000000, 0x40},
      {0x200000000, 0x42},
      {0x400000000, 0x44},
      {0x800000000, 0x46},
      {0x1000000000, 0x48},
      {0x2000000000, 0x4a},
      {0x4000000000, 0x4c},
      {0x8000000000, 0x4e},
      {0x10000000000, 0x50},
      {0x20000000000, 0x52},
      {0x40000000000, 0x54},
      {0x80000000000, 0x56},
      {0x100000000000, 0x58},
      {0x200000000000, 0x5a},
      {0x400000000000, 0x5c},
      {0x800000000000, 0x5e},
      {0x1000000000000, 0x60},
      {0x2000000000000, 0x62},
      {0x4000000000000, 0x64},
      {0x8000000000000, 0x66},
      {0x10000000000000, 0x68},
      {0x20000000000000, 0x6a},
      {0x40000000000000, 0x6c},
      {0x80000000000000, 0x6e},
      {0x100000000000000, 0x70},
      {0x200000000000000, 0x72},
      {0x400000000000000, 0x74},
      {0x800000000000000, 0x76},
      {0x1000000000000000, 0x78},
      {0x2000000000000000, 0x7a},
      {0x4000000000000000, 0x7c},
      {0x8000000000000000, 0x7e}};
  return mappings[before.board_];
}

Bitboard Action::ActionToPieceBefore(uint32_t board) {
  static std::unordered_map<uint32_t, uint64_t> mappings = {
      {0x00, 0x01},
      {0x02, 0x02},
      {0x04, 0x04},
      {0x06, 0x08},
      {0x08, 0x10},
      {0x0a, 0x20},
      {0x0c, 0x40},
      {0x0e, 0x80},
      {0x10, 0x100},
      {0x12, 0x200},
      {0x14, 0x400},
      {0x16, 0x800},
      {0x18, 0x1000},
      {0x1a, 0x2000},
      {0x1c, 0x4000},
      {0x1e, 0x8000},
      {0x20, 0x10000},
      {0x22, 0x20000},
      {0x24, 0x40000},
      {0x26, 0x80000},
      {0x28, 0x100000},
      {0x2a, 0x200000},
      {0x2c, 0x400000},
      {0x2e, 0x800000},
      {0x30, 0x1000000},
      {0x32, 0x2000000},
      {0x34, 0x4000000},
      {0x36, 0x8000000},
      {0x38, 0x10000000},
      {0x3a, 0x20000000},
      {0x3c, 0x40000000},
      {0x3e, 0x80000000},
      {0x40, 0x100000000},
      {0x42, 0x200000000},
      {0x44, 0x400000000},
      {0x46, 0x800000000},
      {0x48, 0x1000000000},
      {0x4a, 0x2000000000},
      {0x4c, 0x4000000000},
      {0x4e, 0x8000000000},
      {0x50, 0x10000000000},
      {0x52, 0x20000000000},
      {0x54, 0x40000000000},
      {0x56, 0x80000000000},
      {0x58, 0x100000000000},
      {0x5a, 0x200000000000},
      {0x5c, 0x400000000000},
      {0x5e, 0x800000000000},
      {0x60, 0x1000000000000},
      {0x62, 0x2000000000000},
      {0x64, 0x4000000000000},
      {0x66, 0x8000000000000},
      {0x68, 0x10000000000000},
      {0x6a, 0x20000000000000},
      {0x6c, 0x40000000000000},
      {0x6e, 0x80000000000000},
      {0x70, 0x100000000000000},
      {0x72, 0x200000000000000},
      {0x74, 0x400000000000000},
      {0x76, 0x800000000000000},
      {0x78, 0x1000000000000000},
      {0x7a, 0x2000000000000000},
      {0x7c, 0x4000000000000000},
      {0x7e, 0x8000000000000000}};
  return Bitboard(mappings[board & 0x7e]);
}

uint32_t Action::PieceAfterToBitboard(const Bitboard& after) {
  static std::unordered_map<uint64_t, uint32_t> mappings = {
      {0x01, 0x00},
      {0x02, 0x80},
      {0x04, 0x100},
      {0x08, 0x180},
      {0x10, 0x200},
      {0x20, 0x280},
      {0x40, 0x300},
      {0x80, 0x380},
      {0x100, 0x400},
      {0x200, 0x480},
      {0x400, 0x500},
      {0x800, 0x580},
      {0x1000, 0x600},
      {0x2000, 0x680},
      {0x4000, 0x700},
      {0x8000, 0x780},
      {0x10000, 0x800},
      {0x20000, 0x880},
      {0x40000, 0x900},
      {0x80000, 0x980},
      {0x100000, 0xa00},
      {0x200000, 0xa80},
      {0x400000, 0xb00},
      {0x800000, 0xb80},
      {0x1000000, 0xc00},
      {0x2000000, 0xc80},
      {0x4000000, 0xd00},
      {0x8000000, 0xd80},
      {0x10000000, 0xe00},
      {0x20000000, 0xe80},
      {0x40000000, 0xf00},
      {0x80000000, 0xf80},
      {0x100000000, 0x1000},
      {0x200000000, 0x1080},
      {0x400000000, 0x1100},
      {0x800000000, 0x1180},
      {0x1000000000, 0x1200},
      {0x2000000000, 0x1280},
      {0x4000000000, 0x1300},
      {0x8000000000, 0x1380},
      {0x10000000000, 0x1400},
      {0x20000000000, 0x1480},
      {0x40000000000, 0x1500},
      {0x80000000000, 0x1580},
      {0x100000000000, 0x1600},
      {0x200000000000, 0x1680},
      {0x400000000000, 0x1700},
      {0x800000000000, 0x1780},
      {0x1000000000000, 0x1800},
      {0x2000000000000, 0x1880},
      {0x4000000000000, 0x1900},
      {0x8000000000000, 0x1980},
      {0x10000000000000, 0x1a00},
      {0x20000000000000, 0x1a80},
      {0x40000000000000, 0x1b00},
      {0x80000000000000, 0x1b80},
      {0x100000000000000, 0x1c00},
      {0x200000000000000, 0x1c80},
      {0x400000000000000, 0x1d00},
      {0x800000000000000, 0x1d80},
      {0x1000000000000000, 0x1e00},
      {0x2000000000000000, 0x1e80},
      {0x4000000000000000, 0x1f00},
      {0x8000000000000000, 0x1f80}};
  return mappings[after.board_];
}

Bitboard Action::ActionToPieceAfter(uint32_t board) {
  static std::unordered_map<uint32_t, uint64_t> mappings = {
      {0x00, 0x01},
      {0x80, 0x02},
      {0x100, 0x04},
      {0x180, 0x08},
      {0x200, 0x10},
      {0x280, 0x20},
      {0x300, 0x40},
      {0x380, 0x80},
      {0x400, 0x100},
      {0x480, 0x200},
      {0x500, 0x400},
      {0x580, 0x800},
      {0x600, 0x1000},
      {0x680, 0x2000},
      {0x700, 0x4000},
      {0x780, 0x8000},
      {0x800, 0x10000},
      {0x880, 0x20000},
      {0x900, 0x40000},
      {0x980, 0x80000},
      {0xa00, 0x100000},
      {0xa80, 0x200000},
      {0xb00, 0x400000},
      {0xb80, 0x800000},
      {0xc00, 0x1000000},
      {0xc80, 0x2000000},
      {0xd00, 0x4000000},
      {0xd80, 0x8000000},
      {0xe00, 0x10000000},
      {0xe80, 0x20000000},
      {0xf00, 0x40000000},
      {0xf80, 0x80000000},
      {0x1000, 0x100000000},
      {0x1080, 0x200000000},
      {0x1100, 0x400000000},
      {0x1180, 0x800000000},
      {0x1200, 0x1000000000},
      {0x1280, 0x2000000000},
      {0x1300, 0x4000000000},
      {0x1380, 0x8000000000},
      {0x1400, 0x10000000000},
      {0x1480, 0x20000000000},
      {0x1500, 0x40000000000},
      {0x1580, 0x80000000000},
      {0x1600, 0x100000000000},
      {0x1680, 0x200000000000},
      {0x1700, 0x400000000000},
      {0x1780, 0x800000000000},
      {0x1800, 0x1000000000000},
      {0x1880, 0x2000000000000},
      {0x1900, 0x4000000000000},
      {0x1980, 0x8000000000000},
      {0x1a00, 0x10000000000000},
      {0x1a80, 0x20000000000000},
      {0x1b00, 0x40000000000000},
      {0x1b80, 0x80000000000000},
      {0x1c00, 0x100000000000000},
      {0x1c80, 0x200000000000000},
      {0x1d00, 0x400000000000000},
      {0x1d80, 0x800000000000000},
      {0x1e00, 0x1000000000000000},
      {0x1e80, 0x2000000000000000},
      {0x1f00, 0x4000000000000000},
      {0x1f80, 0x8000000000000000}};
  return Bitboard(mappings[board & 0x1f80]);
}

uint32_t Action::PieceMovedToBitboard(Piece piece) {
  static std::unordered_map<uint32_t, uint64_t> mappings = {
      {kKing, 0x10000},   {kPawn, 0x20000},   {kBishop, 0x30000},
      {kKnight, 0x40000}, {kRook, 0x50000}, {kQueen, 0x60000}};
  return mappings[piece];
}

Piece Action::ActionToPieceMoved(uint32_t board) {
  static std::unordered_map<uint32_t, Piece> mappings = {
      {0x10000, kKing},   {0x20000, kPawn},   {0x30000, kBishop},
      {0x40000, kKnight}, {0x50000, kRook}, {0x60000, kQueen}};
  return mappings[board & 0x70000];
}

uint32_t Action::DoublePawnForwardToBitboard(bool double_pawn_forward) {
  return double_pawn_forward ? 0x80000 : 0x00;
}

bool Action::ActionToDoublePawnForward(uint32_t board) {
  return (board & 0x80000) != 0;
}

uint32_t Action::QueenSideCastleToBitboard(bool queen_side_castling) {
  return queen_side_castling ? 0x100000 : 0x00;
}

bool Action::ActionToQueenSideCastle(uint32_t board) {
  return (board & 0x100000) != 0;
}

uint32_t Action::KingSideCastleToBitboard(bool king_side_castling) {
  return king_side_castling ? 0x200000 : 0x00;
}

bool Action::ActionToKingSideCastle(uint32_t board) {
  return (board & 0x200000) != 0;
}

uint32_t Action::EnemyInCheckToBitboard(bool enemy_in_check) {
  return enemy_in_check ? 0x400000 : 0x00;
}

bool Action::ActionToEnemyInCheck(uint32_t board) {
  return (board & 0x400000) != 0;
}

uint32_t Action::PieceCapturedToBitboard(bool was_capture, Piece piece) {
  static std::unordered_map<Piece, uint32_t> mappings = {
      {kPawn, 0x800000},    {kBishop, 0x1000000}, {kKnight, 0x1800000},
      {kRook, 0x2000000}, {kQueen, 0x2800000},  {kKing, 0x80000000}};

  if (was_capture) {
    return mappings[piece];
  }
  return 0x00;
}

Piece Action::ActionToPieceCaptured(uint32_t board) {
  static std::unordered_map<uint32_t, Piece> mappings = {
      {0x800000, kPawn},    {0x1000000, kBishop}, {0x1800000, kKnight},
      {0x2000000, kRook}, {0x2800000, kQueen},  {0x80000000, kKing}};
  return mappings[board & 0x83800000];
}

bool Action::ActionToWasCapture(uint32_t board) {
  return (board & 0x83800000) != 0;
}

uint32_t Action::WasEnPassantCaptureToBitboard(bool was_en_passant_capture) {
  return was_en_passant_capture ? 0x4000000 : 0x00;
}

bool Action::ActionToWasEnpassantCapture(uint32_t board) {
  return (board & 0x4000000) != 0;
}

uint32_t Action::WasEqualPieceCaptureToBitboard(bool was_capture, Piece piece,
                                                Piece capture_piece) {
  if (was_capture && piece == capture_piece) {
    return 0x8000000;
  }
  return 0x00;
}

bool Action::ActionToWasEqualPieceCapture(uint32_t board) {
  return (board & 0x8000000) != 0;
}

uint32_t Action::PromotionToBitboard(bool was_promotion, Piece promoted_to) {
  static std::unordered_map<Piece, uint32_t> mappings = {{kBishop, 0x10000000},
                                                         {kKnight, 0x20000000},
                                                         {kRook, 0x30000000},
                                                         {kQueen, 0x40000000}};
  if (!was_promotion) {
    return 0x00;
  }
  return mappings[promoted_to];
}

bool Action::ActionToWasPromotion(uint32_t board) {
  return (board & 0x70000000) != 0;
}

Piece Action::ActionToPromotedTo(uint32_t board) {
  static std::unordered_map<uint32_t, Piece> mappings = {{0x10000000, kBishop},
                                                         {0x20000000, kKnight},
                                                         {0x30000000, kRook},
                                                         {0x40000000, kQueen}};
  return mappings[board & 0x70000000];
}

}  // namespace ChessEngine
