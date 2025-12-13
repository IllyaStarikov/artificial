//
//  chess-ai.cpp
//  chess_ai
//
//  Created by Illya Starikov on 03/07/18.
//  Copyright 2018. Illya Starikov. All rights reserved.
//

#include "chess-ai.h"

namespace ChessEngine {

ChessAI::ChessAI(const std::string& fen_string)
    : current_state_(parser_(fen_string)),
      half_move_number_(2 * parser_.HalfMoves(fen_string)) {
  history_.Add(current_state_);
}

State ChessAI::InitialState() {
  std::vector<Bitboard> white_bitboard(6);
  std::vector<Bitboard> black_bitboard(6);
  Bitboard all_whites(0xffff);
  Bitboard all_blacks(0xffff000000000000);
  Bitboard en_passant_squares(0);
  Bitboard castling_squares = Bitboard(0x81) | Bitboard(0x8100000000000000);

  MoveEngine::GenerateInitialState(white_bitboard, black_bitboard);
  return State(kWhite, all_whites, all_blacks, white_bitboard, black_bitboard,
               en_passant_squares, castling_squares);
}

bool ChessAI::WasCapture(const Bitboard& enemy_bitboard, const Bitboard& move) {
  const Bitboard kZeroBitboard(0);
  return (enemy_bitboard & move) != kZeroBitboard;
}

Piece ChessAI::FindCapturePiece(const std::vector<Bitboard>& enemy_bitboards,
                                const Bitboard& enemy_bitboard,
                                const Bitboard& move) {
  if (!WasCapture(enemy_bitboard, move)) {
    return kKing;
  }

  for (int i = 0; i < kNumberOfPieces; i++) {
    if ((move & enemy_bitboards[i]) != Bitboard(0)) {
      return MoveEngine::IntToPiece(i);
    }
  }

  return kKing;
}

Bitboard ChessAI::EnpassantMoveGenerator(const Bitboard& en_passant_squares,
                                         const Bitboard& pawn,
                                         Color friendly_color) {
  const Bitboard kZeroBitboard(0);
  Bitboard valid_squares =
      MoveEngine::EnpassantMoves(en_passant_squares, pawn);

  if (valid_squares != kZeroBitboard) {
    if (friendly_color == kWhite) {
      return MoveEngine::Moving(en_passant_squares, kNorth);
    } else {
      return MoveEngine::Moving(en_passant_squares, kSouth);
    }
  }

  return kZeroBitboard;
}

Bitboard ChessAI::KingLocationAfterCastling(const Bitboard& rook_after) {
  const Bitboard kZeroBitboard(0);

  const Bitboard kWhiteLongSideAfter(0x08);
  const Bitboard kWhiteShortSideAfter(0x20);
  const Bitboard kBlackLongSideAfter(0x800000000000000);
  const Bitboard kBlackShortSideAfter(0x2000000000000000);

  const Bitboard kWhiteLongSideKingLocation(0x04);
  const Bitboard kWhiteShortSideKingLocation(0x40);
  const Bitboard kBlackLongSideKingLocation(0x400000000000000);
  const Bitboard kBlackShortSideKingLocation(0x4000000000000000);

  if (rook_after == kWhiteLongSideAfter) {
    return kWhiteLongSideKingLocation;
  } else if (rook_after == kWhiteShortSideAfter) {
    return kWhiteShortSideKingLocation;
  } else if (rook_after == kBlackLongSideAfter) {
    return kBlackLongSideKingLocation;
  } else if (rook_after == kBlackShortSideAfter) {
    return kBlackShortSideKingLocation;
  }

  return kZeroBitboard;
}

bool ChessAI::IsEightfoldRepetitionRule(const PerceptSequence& from_history) {
  if (from_history.Size() < 8) {
    return false;
  }

  for (int i = 0; i < 4; i++) {
    if (from_history[i] != from_history[i + 4]) {
      return false;
    }
  }

  return from_history.MovesSincePawnMovement() >= 8 &&
         from_history.MovesSinceCapture() >= 8;
}

bool ChessAI::InsufficientMaterial(const State& current_state) {
  // King vs King
  bool only_kings =
      current_state.whites_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0);

  // King vs King + Knight (black has knight)
  bool king_vs_king_knight_black =
      current_state.whites_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kKnight)].NumberOfBits() ==
          1 &&
      current_state.blacks_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0);

  // King vs King + Bishop (black has bishop)
  bool king_vs_king_bishop_black =
      current_state.whites_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kBishop)].NumberOfBits() ==
          1 &&
      current_state.blacks_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0);

  // King vs King + Knight (white has knight)
  bool king_vs_king_knight_white =
      current_state.whites_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kKnight)].NumberOfBits() ==
          1 &&
      current_state.whites_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0);

  // King vs King + Bishop (white has bishop)
  bool king_vs_king_bishop_white =
      current_state.whites_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kBishop)].NumberOfBits() ==
          1 &&
      current_state.whites_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.whites_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kRook)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kBishop)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kQueen)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kKnight)] == Bitboard(0) &&
      current_state.blacks_[MoveEngine::PieceToInt(kPawn)] == Bitboard(0);

  return only_kings || king_vs_king_knight_black || king_vs_king_bishop_black ||
         king_vs_king_knight_white || king_vs_king_bishop_white;
}

bool ChessAI::FiftyMoveRule(const PerceptSequence& history) {
  return history.MovesSinceCapture() >= 50 &&
         history.MovesSincePawnMovement() > 50;
}

std::shared_ptr<Action> ChessAI::DepthLimitedMinimax(
    int depth_limit, int quiescence_limit, double time_limit,
    const State& state, std::map<Action, int>& history_table,
    const PerceptSequence& history) {
  Color friendly_color = state.color_at_play_;
  std::vector<Action> possible_actions = Actions(state);

  float alpha = -std::numeric_limits<float>::infinity();
  float beta = std::numeric_limits<float>::infinity();

  Action best_action = possible_actions.back();
  std::shared_ptr<float> current_max_value =
      MinValue(depth_limit - 1, quiescence_limit, time_limit,
               Result(state, best_action), best_action, alpha, beta,
               friendly_color, history_table, history);

  possible_actions.pop_back();

  for (const Action& action : possible_actions) {
    std::shared_ptr<float> value =
        MinValue(depth_limit - 1, quiescence_limit, time_limit,
                 Result(state, action), action, alpha, beta, friendly_color,
                 history_table, history);
    if (value == nullptr) {
      return nullptr;
    }

    if (value > current_max_value) {
      current_max_value = value;
      best_action = action;
    }
  }

  return std::make_shared<Action>(best_action);
}

std::shared_ptr<float> ChessAI::MaxValue(int depth_limit, int quiescence_limit,
                                         double time_limit, const State& state,
                                         const Action& action, float alpha,
                                         float beta, Color color,
                                         std::map<Action, int>& history_table,
                                         const PerceptSequence& history) {
  if (TerminalTest(state, history) != kNonterminal) {
    return std::make_shared<float>(UtilityFunction(state, color, history));
  }
  if (move_timer_.Elapsed() > time_limit) {
    return nullptr;
  }
  if (depth_limit <= 0 && IsNonQuiescenceState(action)) {
    quiescence_limit--;
  } else if (depth_limit <= 0) {
    return std::make_shared<float>(UtilityHeuristic(state, color));
  }

  std::vector<Action> possible_actions = Actions(state);
  auto sort_function = [&](const Action& action1, const Action& action2) {
    int val1 = (history_table.find(action1) != history_table.end())
                   ? history_table[action1]
                   : 0;
    int val2 = (history_table.find(action2) != history_table.end())
                   ? history_table[action2]
                   : 0;
    return val1 > val2;
  };
  std::sort(possible_actions.begin(), possible_actions.end(), sort_function);

  float value = -std::numeric_limits<float>::infinity();
  Action best_action;

  for (const Action& act : possible_actions) {
    PerceptSequence new_history = history;
    State resultant_state = Result(state, act);

    new_history.Add(resultant_state);
    new_history.Add(act);

    std::shared_ptr<float> new_value =
        MinValue(depth_limit - 1, quiescence_limit, time_limit, resultant_state,
                 act, alpha, beta, color, history_table, new_history);

    if (new_value == nullptr) {
      return nullptr;
    }

    if (*new_value > value) {
      value = *new_value;
      best_action = act;
    }

    if (value >= beta) {
      AddToHistoryTable(history_table, act);
      return std::make_shared<float>(value);
    }

    alpha = std::max(alpha, value);
  }

  AddToHistoryTable(history_table, best_action);
  return std::make_shared<float>(value);
}

std::shared_ptr<float> ChessAI::MinValue(int depth_limit, int quiescence_limit,
                                         double time_limit, const State& state,
                                         const Action& action, float alpha,
                                         float beta, Color color,
                                         std::map<Action, int>& history_table,
                                         const PerceptSequence& history) {
  if (TerminalTest(state, history) != kNonterminal) {
    return std::make_shared<float>(UtilityFunction(state, color, history));
  }
  if (move_timer_.Elapsed() > time_limit) {
    return nullptr;
  }
  if (depth_limit <= 0 && IsNonQuiescenceState(action)) {
    quiescence_limit--;
  } else if (depth_limit <= 0) {
    return std::make_shared<float>(UtilityHeuristic(state, color));
  }

  std::vector<Action> possible_actions = Actions(state);
  auto sort_function = [&](const Action& action1, const Action& action2) {
    int val1 = (history_table.find(action1) != history_table.end())
                   ? history_table[action1]
                   : 0;
    int val2 = (history_table.find(action2) != history_table.end())
                   ? history_table[action2]
                   : 0;
    return val1 > val2;
  };

  std::sort(possible_actions.begin(), possible_actions.end(), sort_function);

  float value = std::numeric_limits<float>::infinity();
  Action best_action;

  for (const Action& act : possible_actions) {
    PerceptSequence new_history = history;
    State resultant_state = Result(state, act);

    new_history.Add(resultant_state);
    new_history.Add(act);

    std::shared_ptr<float> new_value =
        MaxValue(depth_limit - 1, quiescence_limit, time_limit, resultant_state,
                 act, alpha, beta, color, history_table, new_history);

    if (new_value == nullptr) {
      return nullptr;
    }

    if (*new_value < value) {
      value = *new_value;
      best_action = act;
    }

    if (value <= alpha) {
      AddToHistoryTable(history_table, act);
      return std::make_shared<float>(value);
    }

    beta = std::min(beta, value);
  }

  AddToHistoryTable(history_table, best_action);
  return std::make_shared<float>(value);
}

void ChessAI::AddToHistoryTable(std::map<Action, int>& history_table,
                                const Action& action) {
  if (history_table.find(action) == history_table.end()) {
    history_table[action] = 0;
  }
  history_table[action]++;
}

Bitboard ChessAI::CastlingMoveGenerator(const Bitboard& all_whites,
                                        const Bitboard& all_blacks,
                                        const Bitboard& castling_squares,
                                        const Bitboard& rook) {
  const Bitboard kZeroBitboard(0);

  const Bitboard kWhiteLongSideBefore(0x01);
  const Bitboard kWhiteShortSideBefore(0x80);
  const Bitboard kBlackLongSideBefore(0x100000000000000);
  const Bitboard kBlackShortSideBefore(0x8000000000000000);

  const Bitboard kWhiteLongSideAfter(0x08);
  const Bitboard kWhiteShortSideAfter(0x20);
  const Bitboard kBlackLongSideAfter(0x800000000000000);
  const Bitboard kBlackShortSideAfter(0x2000000000000000);

  Bitboard possible_castles =
      MoveEngine::CastlingMoves(castling_squares, all_whites, all_blacks);
  Bitboard to_return = kZeroBitboard;

  if ((kWhiteLongSideBefore & possible_castles & rook) != kZeroBitboard) {
    to_return |= kWhiteLongSideAfter;
  }
  if ((kWhiteShortSideBefore & possible_castles & rook) != kZeroBitboard) {
    to_return |= kWhiteShortSideAfter;
  }
  if ((kBlackLongSideBefore & possible_castles & rook) != kZeroBitboard) {
    to_return |= kBlackLongSideAfter;
  }
  if ((kBlackShortSideBefore & possible_castles & rook) != kZeroBitboard) {
    to_return |= kBlackShortSideAfter;
  }

  return to_return;
}

std::vector<Action> ChessAI::Actions(const State& state) {
  const Bitboard kZeroBitboard(0);
  const Bitboard kFirstEighthRank(0xff000000000000ff);
  const Bitboard kSecondSeventhRank(0xff00000000ff00);
  const Bitboard kFourthFifthRank(0xffff000000);

  const Bitboard kQueenSideCastlingBefore(0x100000000000001);
  const Bitboard kQueenSideCastlingAfter(0x800000000000008);

  const Bitboard kKingSideCastlingBefore(0x8000000000000080);
  const Bitboard kKingSideCastlingAfter(0x2000000000000020);

  std::vector<Action> actions;

  Color friendly_color = state.color_at_play_;
  Color enemy_color = static_cast<Color>((state.color_at_play_ + 1) % 2);

  const std::vector<Bitboard>& friendly =
      friendly_color == kWhite ? state.whites_ : state.blacks_;
  const std::vector<Bitboard>& enemy =
      enemy_color == kWhite ? state.whites_ : state.blacks_;

  const Bitboard& all_friendly =
      friendly_color == kWhite ? state.all_whites_ : state.all_blacks_;
  const Bitboard& all_enemy =
      enemy_color == kWhite ? state.all_whites_ : state.all_blacks_;

  const Bitboard& en_passant_squares = state.en_passant_squares_;
  const Bitboard& castling_squares = state.castling_squares_;

  // Move generators: piece type, is castling, is en passant, move function.
  const std::vector<
      std::tuple<Piece, bool, bool, std::function<Bitboard(Bitboard)>>>
      move_generators = {
          std::make_tuple(
              kKing, false, false,
              [&](const Bitboard& king_board) {
                return MoveEngine::KingMoves(king_board, all_friendly);
              }),
          std::make_tuple(
              kKnight, false, false,
              [&](const Bitboard& knight_board) {
                return MoveEngine::KnightMoves(knight_board, all_friendly);
              }),
          std::make_tuple(
              kRook, false, false,
              [&](const Bitboard& rook_board) {
                return MoveEngine::RookMoves(rook_board, all_friendly,
                                             all_enemy);
              }),
          std::make_tuple(
              kBishop, false, false,
              [&](const Bitboard& bishop_board) {
                return MoveEngine::BishopMoves(bishop_board, all_friendly,
                                               all_enemy);
              }),
          std::make_tuple(
              kQueen, false, false,
              [&](const Bitboard& queen_board) {
                return MoveEngine::QueenMoves(queen_board, all_friendly,
                                              all_enemy);
              }),
          std::make_tuple(
              kPawn, false, false,
              [&](const Bitboard& pawn_board) {
                return MoveEngine::PawnMoves(pawn_board, all_friendly, all_enemy,
                                             friendly_color);
              }),
          std::make_tuple(
              kPawn, false, true,
              [&](const Bitboard& pawn_board) {
                return EnpassantMoveGenerator(pawn_board, en_passant_squares,
                                              friendly_color);
              }),
          std::make_tuple(kRook, true, false, [&](const Bitboard& rook_board) {
            return CastlingMoveGenerator(all_friendly, all_enemy,
                                         castling_squares, rook_board);
          })};

  const std::initializer_list<Piece> promotable_pieces = {kQueen, kRook,
                                                          kBishop, kKnight};

  for (const auto& piece_and_attack : move_generators) {
    Piece piece = std::get<0>(piece_and_attack);
    bool is_castling = std::get<1>(piece_and_attack);
    bool is_en_passant = std::get<2>(piece_and_attack);
    auto move_generator = std::get<3>(piece_and_attack);

    Bitboard current_board = friendly[MoveEngine::PieceToInt(piece)];

    for (const Bitboard& piece_inside_board : current_board.Separated()) {
      if (move_generator(piece_inside_board) == kZeroBitboard) {
        continue;
      }

      std::vector<Bitboard> locations =
          move_generator(piece_inside_board).Separated();

      for (const Bitboard& new_location : locations) {
        // Remove piece from old position, place at new position.
        Bitboard new_all_friendly =
            (all_friendly & (~current_board)) | new_location;
        Bitboard new_all_enemy = (all_enemy & (~new_location));

        // Handle capture: update enemy bitboards.
        std::vector<Bitboard> temp_all_enemy = enemy;
        for (Bitboard& pieces : temp_all_enemy) {
          pieces &= new_all_enemy;
        }

        // Check all enemy moves after this move.
        Bitboard all_enemy_moves = MoveEngine::AllStandardMovesInOneBitboard(
            temp_all_enemy, new_all_enemy, new_all_friendly, enemy_color);

        // Determine king position.
        Bitboard king_piece =
            piece == kKing ? new_location : friendly[MoveEngine::PieceToInt(kKing)];
        if (is_castling) {
          king_piece = KingLocationAfterCastling(new_location);
        }

        // Check if this move leads to a pinned king.
        Bitboard enemies_attacking_king = all_enemy_moves & king_piece;

        if (enemies_attacking_king == kZeroBitboard) {
          bool was_a_capture = WasCapture(all_enemy, new_location);
          Piece captured_piece = FindCapturePiece(enemy, all_enemy, new_location);

          Bitboard before = piece_inside_board;
          Bitboard after = new_location;

          bool double_pawn_forward =
              (piece == kPawn) && ((before & kSecondSeventhRank) != kZeroBitboard) &&
              ((after & kFourthFifthRank) != kZeroBitboard);
          bool queen_side_castling =
              is_castling
                  ? ((before & kQueenSideCastlingBefore) != kZeroBitboard) &&
                        ((after & kQueenSideCastlingAfter) != kZeroBitboard)
                  : false;
          bool king_side_castling =
              is_castling
                  ? ((before & kKingSideCastlingBefore) != kZeroBitboard) &&
                        ((after & kKingSideCastlingAfter) != kZeroBitboard)
                  : false;

          bool enemy_in_check = false;

          // Handle pawn promotions.
          if ((piece == kPawn) &&
              ((new_location & kFirstEighthRank) != kZeroBitboard)) {
            bool was_promotion = true;

            for (Piece promoted_piece : promotable_pieces) {
              Action action(piece, friendly_color, before, after,
                            double_pawn_forward, queen_side_castling,
                            king_side_castling, enemy_in_check, was_a_capture,
                            is_en_passant, captured_piece, was_promotion,
                            promoted_piece);
              actions.push_back(action);
            }
          } else {
            bool was_promotion = false;
            Piece promoted_to = kKing;

            Action action(piece, friendly_color, before, after,
                          double_pawn_forward, queen_side_castling,
                          king_side_castling, enemy_in_check, was_a_capture,
                          is_en_passant, captured_piece, was_promotion,
                          promoted_to);
            actions.push_back(action);
          }
        }
      }
    }
  }

  std::sort(actions.begin(), actions.end());
  return actions;
}

State ChessAI::Result(const State& state, const Action& action) {
  const Bitboard kZeroBitboard(0);
  const Bitboard kFourthFifthRank(0xffff000000);
  const Bitboard kSecondSeventhRank(0xff00000000ff00);

  Piece piece = action.GetPiece();
  Bitboard piece_before = action.PieceBefore();
  Bitboard piece_after = action.PieceAfter();

  bool was_capture = action.WasCapture();
  Piece captured_piece = action.PieceCaptured();

  bool was_promotion = action.WasPromotion();
  Piece promoted_to = action.PromotedTo();

  Color old_color_at_play = state.color_at_play_;
  Color new_color_at_play =
      static_cast<Color>((state.color_at_play_ + 1) % 2);

  std::vector<Bitboard> whites = state.whites_;
  std::vector<Bitboard> blacks = state.blacks_;

  bool was_en_passant = action.WasEnPassantCapture();
  bool was_castling =
      action.QueenSideCastling() || action.KingSideCastling();

  Bitboard en_passant_squares = kZeroBitboard;
  Bitboard castling_squares = state.castling_squares_;

  if (was_promotion) {
    if (old_color_at_play == kWhite) {
      whites[MoveEngine::PieceToInt(kPawn)] &= ~piece_before;
      whites[MoveEngine::PieceToInt(promoted_to)] |= piece_after;

      if (was_capture) {
        blacks[MoveEngine::PieceToInt(captured_piece)] &= ~piece_after;
      }
    } else {
      blacks[MoveEngine::PieceToInt(kPawn)] &= ~piece_before;
      blacks[MoveEngine::PieceToInt(promoted_to)] |= piece_after;

      if (was_capture) {
        whites[MoveEngine::PieceToInt(captured_piece)] &= ~piece_after;
      }
    }
  } else if (old_color_at_play == kWhite) {
    whites[MoveEngine::PieceToInt(piece)] &= ~piece_before;
    whites[MoveEngine::PieceToInt(piece)] |= piece_after;

    if (was_capture) {
      blacks[MoveEngine::PieceToInt(captured_piece)] &= ~piece_after;
    }

    if (was_en_passant) {
      blacks[MoveEngine::PieceToInt(kPawn)] &= ~state.en_passant_squares_;
    }

    if (was_castling) {
      whites[MoveEngine::PieceToInt(kKing)] =
          KingLocationAfterCastling(piece_after);
    }

  } else {
    blacks[MoveEngine::PieceToInt(piece)] &= ~piece_before;
    blacks[MoveEngine::PieceToInt(piece)] |= piece_after;

    if (was_capture) {
      whites[MoveEngine::PieceToInt(captured_piece)] &= ~piece_after;
    }

    if (was_en_passant) {
      whites[MoveEngine::PieceToInt(kPawn)] &= ~state.en_passant_squares_;
    }

    if (was_castling) {
      whites[MoveEngine::PieceToInt(kKing)] =
          KingLocationAfterCastling(piece_after);
    }
  }

  // If rook moved, disable castling from that side.
  if (piece == kRook) {
    castling_squares &= ~piece_before;
  } else if (piece == kPawn) {
    // If pawn moved two squares, set en passant square.
    if ((piece_before & kSecondSeventhRank) != kZeroBitboard &&
        (piece_after & kFourthFifthRank) != kZeroBitboard) {
      en_passant_squares |= piece_after;
    }
  }

  Bitboard all_whites = MoveEngine::AllBitboardsInOneBoard(whites);
  Bitboard all_blacks = MoveEngine::AllBitboardsInOneBoard(blacks);

  return State(new_color_at_play, all_whites, all_blacks, whites, blacks,
               en_passant_squares, castling_squares);
}

ChessOutcome ChessAI::TerminalTest(const State& state,
                                   const PerceptSequence& history) {
  const Bitboard kZeroBitboard(0);

  Color friendly_color = state.color_at_play_;
  Color enemy_color = static_cast<Color>((friendly_color + 1) % 2);

  const std::vector<Bitboard>& friendly =
      friendly_color == kWhite ? state.whites_ : state.blacks_;
  const std::vector<Bitboard>& enemy =
      enemy_color == kWhite ? state.whites_ : state.blacks_;

  const Bitboard& all_friendly =
      friendly_color == kWhite ? state.all_whites_ : state.all_blacks_;
  const Bitboard& all_enemy =
      enemy_color == kWhite ? state.all_whites_ : state.all_blacks_;

  State friendly_state = state;

  Bitboard all_enemy_moves = MoveEngine::AllStandardMovesInOneBitboard(
      enemy, all_enemy, all_friendly, enemy_color);

  if (Actions(friendly_state).empty()) {
    if ((friendly[MoveEngine::PieceToInt(kKing)] & all_enemy_moves) ==
        kZeroBitboard) {
      return kDraw;
    } else {
      return kLoss;
    }
  } else if (IsEightfoldRepetitionRule(history)) {
    return kDraw;
  } else if (InsufficientMaterial(friendly_state)) {
    return kDraw;
  } else if (FiftyMoveRule(history)) {
    return kDraw;
  }

  return kNonterminal;
}

float ChessAI::UtilityFunction(const State& state, Color friendly_color,
                               const PerceptSequence& history) {
  ChessOutcome terminal_result = TerminalTest(state, history);
  ChessOutcome outcome;

  if (state.color_at_play_ == friendly_color) {
    outcome = terminal_result;
  } else {
    if (terminal_result == kNonterminal) {
      outcome = terminal_result;
    } else if (terminal_result == kWin) {
      outcome = kLoss;
    } else {
      outcome = kWin;
    }
  }

  if (outcome == kWin) {
    return std::numeric_limits<float>::infinity();
  } else if (outcome == kLoss) {
    return -std::numeric_limits<float>::infinity();
  } else {
    return 0;
  }
}

float ChessAI::UtilityHeuristic(const State& state, Color player_color) {
  return ChessAIHeuristic<float>::MaterialAdvantage(state, player_color);
}

void ChessAI::UpdateTimer(double time_remaining_seconds) {
  time_remaining_ = time_remaining_seconds;
}

Action ChessAI::Move() {
  move_timer_.Start();

  double time_limit = time_calculator_(half_move_number_, time_remaining_);
  Action move = Minimax(time_limit, current_state_, history_);

  current_state_ = Result(current_state_, move);
  history_.Add(current_state_);
  history_.Add(move);

  half_move_number_ += 1;
  time_remaining_ -= move_timer_.Elapsed();

  move_timer_.Stop();

  return move;
}

void ChessAI::UpdateMove(const Action& action) {
  current_state_ = Result(current_state_, action);

  history_.Add(current_state_);
  history_.Add(action);

  half_move_number_ += 1;
}

Action ChessAI::Minimax(double time_limit, const State& state,
                        const PerceptSequence& history) {
  static Timer local_timer;

  int depth_limit = 1;
  int quiescence_limit = 4;

  Action last_move = Actions(state)[0];
  std::map<Action, int> history_table;

  std::shared_ptr<Action> move;

  do {
    local_timer.Start();
    move = DepthLimitedMinimax(depth_limit++, quiescence_limit, time_limit,
                               state, history_table, history);
    local_timer.Stop();

    if (move != nullptr) {
      last_move = *move;
    }
  } while (move_timer_.Elapsed() + local_timer.Elapsed() < time_limit);

  return last_move;
}

}  // namespace ChessEngine
