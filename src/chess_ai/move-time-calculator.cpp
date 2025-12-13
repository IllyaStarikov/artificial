//
//  move-time-calculator.cpp
//  chess_ai
//
//  Created by Illya Starikov on 04/03/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "move-time-calculator.h"

namespace ChessEngine {

double MoveTimeCalculator::operator()(int move_number, double time_remaining) {
  const double kA = 0.035;
  const double kB = 80.0;
  const double kC = 35;

  return time_remaining * kA *
         (0.1 + std::exp(-std::pow(move_number - kB, 2) / (2 * kC * kC)));
}

}  // namespace ChessEngine
