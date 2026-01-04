//
//  timer.cpp
//  chess_ai
//
//  Created by Illya Starikov on 04/03/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "timer.h"

namespace ChessEngine {

void Timer::Start() { begin_ = std::chrono::steady_clock::now(); }

void Timer::Stop() { end_ = std::chrono::steady_clock::now(); }

double Timer::Elapsed() {
  const double kMillion = 1000000.0;
  return std::chrono::duration_cast<std::chrono::microseconds>(
             std::chrono::steady_clock::now() - begin_)
             .count() /
         kMillion;
}

}  // namespace ChessEngine
