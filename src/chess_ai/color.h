//
//  color.h
//  chess_ai
//
//  Created by Illya Starikov on 03/02/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_COLOR_H_
#define CHESS_AI_COLOR_H_

#include <cstddef>

namespace ChessEngine {

// Represents the two opposing colors in chess.
enum Color { kWhite, kBlack };

}  // namespace ChessEngine

namespace std {

template <>
struct hash<ChessEngine::Color> {
  size_t operator()(const ChessEngine::Color& color) const {
    return static_cast<size_t>(color);
  }
};

}  // namespace std

#endif  // CHESS_AI_COLOR_H_
