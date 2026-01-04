//
//  timer.h
//  chess_ai
//
//  Created by Illya Starikov on 04/03/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#ifndef CHESS_AI_TIMER_H_
#define CHESS_AI_TIMER_H_

#include <chrono>

namespace ChessEngine {

class Timer {
 public:
  void Start();
  void Stop();
  double Elapsed();

 private:
  std::chrono::steady_clock::time_point begin_;
  std::chrono::steady_clock::time_point end_;
};

}  // namespace ChessEngine

#endif  // CHESS_AI_TIMER_H_
