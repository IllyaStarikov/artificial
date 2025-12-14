//
//  main.cpp
//  Chess AI - Standalone demonstration
//
//  Created by Illya Starikov on 03/06/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include <iostream>
#include <string>

#include "chess-ai.h"

void PrintUsage(const char* program_name) {
  std::cout << "Usage: " << program_name << " [OPTIONS] [FEN string]\n";
  std::cout << "If no FEN string is provided, uses the standard starting "
               "position.\n";
  std::cout << "\nOptions:\n";
  std::cout << "  --worst    Enable worst mode (AI picks worst moves)\n";
  std::cout << "  -h, --help Show this help message\n";
  std::cout << "\nExample:\n";
  std::cout << "  " << program_name << "\n";
  std::cout << "  " << program_name << " --worst\n";
  std::cout << "  " << program_name
            << " \"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 "
               "1\"\n";
  std::cout << "  " << program_name << " --worst \"<FEN string>\"\n";
}

int main(int argc, char* argv[]) {
  // Default to standard starting position.
  std::string fen_string =
      "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
  bool worst_mode = false;

  // Parse command line arguments.
  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg == "-h" || arg == "--help") {
      PrintUsage(argv[0]);
      return 0;
    } else if (arg == "--worst") {
      worst_mode = true;
    } else {
      // Assume it's a FEN string.
      fen_string = arg;
    }
  }

  // Set worst mode if enabled.
  ChessEngine::ChessAI::SetWorstMode(worst_mode);

  std::cout << "Chess AI - Minimax with Alpha-Beta Pruning\n";
  if (worst_mode) {
    std::cout << "*** WORST MODE ENABLED - AI will pick worst moves ***\n";
  }
  std::cout << "==========================================\n\n";

  std::cout << "Initializing from FEN: " << fen_string << "\n\n";

  ChessEngine::ChessAI ai(fen_string);

  std::cout << "Initial board state:\n";
  ai.current_state_.Print();
  std::cout << "\n";

  // Set time remaining (in seconds) - for demo, give it 60 seconds.
  ai.UpdateTimer(60.0);

  std::cout << "Computing best move...\n";

  // Get best move from the AI.
  ChessEngine::Action best_move = ai.Move();

  // Display the move.
  auto from =
      ChessEngine::MoveEngine::BitStringToDescription(best_move.PieceBefore())[0];
  auto to =
      ChessEngine::MoveEngine::BitStringToDescription(best_move.PieceAfter())[0];

  std::cout << "\nBest move: " << static_cast<char>(tolower(from.first))
            << from.second << " -> " << static_cast<char>(tolower(to.first))
            << to.second << "\n";

  if (best_move.WasCapture()) {
    std::cout << "  (Capture)\n";
  }
  if (best_move.WasPromotion()) {
    std::cout << "  (Pawn promotion)\n";
  }
  if (best_move.QueenSideCastling()) {
    std::cout << "  (Queen-side castle)\n";
  }
  if (best_move.KingSideCastling()) {
    std::cout << "  (King-side castle)\n";
  }

  std::cout << "\nBoard after move:\n";
  ai.current_state_.Print();

  return 0;
}
