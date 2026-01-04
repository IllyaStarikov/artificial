//
//  fen-parser.h
//  chess_ai
//
//  Created by Illya Starikov on 03/08/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_FEN_PARSER_H_
#define CHESS_AI_FEN_PARSER_H_

#include <algorithm>
#include <iostream>
#include <map>
#include <regex>
#include <string>

#include "chess-engine.h"
#include "state.h"

namespace ChessEngine {

enum FenToken {
  kBoard,
  kColorAtPlay,
  kCastling,
  kEnPassant,
  kHalfTurns,
  kFullTurns
};

class FenParser {
 public:
  State operator()(const std::string& fen_string);

  short HalfMoves(const std::string& fen_string);
  short FullMoves(const std::string& fen_string);

 private:
  std::string fen_string_;

  std::string GetToken(FenToken token);

  void ParseBoard(std::vector<Bitboard>& white_bitboard,
                  std::vector<Bitboard>& black_bitboard);
  Color ParseColorAtPlay();
  Bitboard ParseCastling();
  Bitboard ParseEnPassant();

  short ParseHalfMoves();
  short ParseFullMoves();
};

}  // namespace ChessEngine

#endif  // CHESS_AI_FEN_PARSER_H_
