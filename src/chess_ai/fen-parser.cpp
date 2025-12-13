//
//  fen-parser.cpp
//  chess_ai
//
//  Created by Illya Starikov on 03/08/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "fen-parser.h"

#include <stdexcept>

namespace ChessEngine {

std::string FenParser::GetToken(FenToken token) {
  const auto regex_string =
      R"((([pPnNbBrRqQkK0-8]{1,8}/?){8})\s*(w|b)\s*([KQkq-]{0,4})\s*([a-hA-H0-8\-]{1,2})\s*(\d+)\s*(\d+)*)";
  auto regex_expression = std::regex(regex_string);
  std::smatch match;

  if (std::regex_search(fen_string_, match, regex_expression)) {
    switch (token) {
      case kBoard:
        return match[1];
      case kColorAtPlay:
        return match[3];  // Offset due to regex capture groups.
      case kCastling:
        return match[4];
      case kEnPassant:
        return match[5];
      case kHalfTurns:
        return match[6];
      case kFullTurns:
        return match[7];
      default:
        throw std::logic_error("Invalid FEN token");
    }
  } else {
    std::cout << fen_string_;
    throw std::logic_error("Invalid FEN string format");
  }
}

void FenParser::ParseBoard(std::vector<Bitboard>& white_bitboard,
                           std::vector<Bitboard>& black_bitboard) {
  std::string token = GetToken(kBoard);
  token.erase(std::remove(token.begin(), token.end(), '/'), token.end());

  std::map<char, std::pair<Color, Piece>> pieces = {
      {'P', std::make_pair(kWhite, kPawn)},
      {'N', std::make_pair(kWhite, kKnight)},
      {'B', std::make_pair(kWhite, kBishop)},
      {'R', std::make_pair(kWhite, kRook)},
      {'Q', std::make_pair(kWhite, kQueen)},
      {'K', std::make_pair(kWhite, kKing)},
      {'p', std::make_pair(kBlack, kPawn)},
      {'n', std::make_pair(kBlack, kKnight)},
      {'b', std::make_pair(kBlack, kBishop)},
      {'r', std::make_pair(kBlack, kRook)},
      {'q', std::make_pair(kBlack, kQueen)},
      {'k', std::make_pair(kBlack, kKing)}};

  int i = 0;
  for (const char& ch : token) {
    // Convert from FEN top-left indexing to bitboard bottom-left indexing.
    int bitboard_index = (8 * ((63 - i) / 8) + (i % 8));

    if (isdigit(ch)) {
      i += static_cast<int>(ch) - 48 - 1;
    } else if (pieces.find(ch) != pieces.end()) {
      auto result = pieces[ch];

      if (result.first == kWhite) {
        white_bitboard[MoveEngine::PieceToInt(result.second)] |=
            Bitboard().FromIndex(bitboard_index);
      } else if (result.first == kBlack) {
        black_bitboard[MoveEngine::PieceToInt(result.second)] |=
            Bitboard().FromIndex(bitboard_index);
      } else {
        throw std::logic_error("FEN parser: color is not white or black");
      }
    } else {
      throw std::logic_error("Illegal character in FEN string");
    }

    i++;
  }
}

Color FenParser::ParseColorAtPlay() {
  std::string token = GetToken(kColorAtPlay);
  return (token == "w") ? kWhite : kBlack;
}

Bitboard FenParser::ParseCastling() {
  const Bitboard kWhiteShortSide(0x80);
  const Bitboard kWhiteLongSide(0x01);
  const Bitboard kBlackShortSide(0x8000000000000000);
  const Bitboard kBlackLongSide(0x100000000000000);

  const Bitboard kZeroBitboard(0);

  std::string token = GetToken(kCastling);
  Bitboard result = kZeroBitboard;

  if (token.find("Q") != std::string::npos) {
    result |= kWhiteLongSide;
  }
  if (token.find("K") != std::string::npos) {
    result |= kWhiteShortSide;
  }
  if (token.find("q") != std::string::npos) {
    result |= kBlackLongSide;
  }
  if (token.find("k") != std::string::npos) {
    result |= kBlackShortSide;
  }

  return result;
}

Bitboard FenParser::ParseEnPassant() {
  std::string token = GetToken(kEnPassant);
  const Bitboard kZeroBitboard(0);

  if (token == "-") {
    return kZeroBitboard;
  }

  int file_weight;
  if (token[0] <= 'z' && token[0] >= 'a') {
    file_weight = static_cast<int>(token[0]) - static_cast<int>('a');
  } else {
    file_weight = static_cast<int>(token[0]) - static_cast<int>('A');
  }
  int rank_weight = 8 * (static_cast<int>(token[1]) - 1 - 48);

  return Bitboard().FromIndex(rank_weight + file_weight);
}

short FenParser::ParseHalfMoves() {
  std::string token = GetToken(kHalfTurns);
  return static_cast<short>(stoi(token));
}

short FenParser::ParseFullMoves() {
  std::string token = GetToken(kFullTurns);
  return static_cast<short>(stoi(token));
}

State FenParser::operator()(const std::string& fen_string) {
  fen_string_ = fen_string;

  std::vector<Bitboard> white_bitboards(6);
  std::vector<Bitboard> black_bitboards(6);
  ParseBoard(white_bitboards, black_bitboards);

  Bitboard all_whites = MoveEngine::AllBitboardsInOneBoard(white_bitboards);
  Bitboard all_blacks = MoveEngine::AllBitboardsInOneBoard(black_bitboards);

  Color color_at_play = ParseColorAtPlay();
  Bitboard enpassant = ParseEnPassant();
  Bitboard castling = ParseCastling();

  return State(color_at_play, all_whites, all_blacks, white_bitboards,
               black_bitboards, enpassant, castling);
}

short FenParser::HalfMoves(const std::string& fen_string) {
  fen_string_ = fen_string;
  return ParseHalfMoves();
}

short FenParser::FullMoves(const std::string& fen_string) {
  fen_string_ = fen_string;
  return ParseFullMoves();
}

}  // namespace ChessEngine
