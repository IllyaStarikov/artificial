//
//  move-time-calculator.h
//  chess_ai
//
//  Created by Illya Starikov on 04/03/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_MOVE_TIME_CALCULATOR_H_
#define CHESS_AI_MOVE_TIME_CALCULATOR_H_

#include <cmath>

namespace ChessEngine {

class MoveTimeCalculator {
 public:
  double operator()(int move_number, double time_remaining);
};

}  // namespace ChessEngine

#endif  // CHESS_AI_MOVE_TIME_CALCULATOR_H_
