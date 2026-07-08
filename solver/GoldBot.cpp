#pragma GCC optimize("O3,inline,omit-frame-pointer,unroll-loops")
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>

using namespace std;
using namespace std::chrono;

const int EMPTY = 0;
const int ATTACKER = 1;
const int DEFENDER = 2;
const int KING = 3;

const int THRONE = 24;
const int CORNERS[4] = {0, 6, 42, 48};
const int DIRS[4] = {1, -1, 7, -7};

int TIME_LIMIT_MS = 95;

long long getTimeMs() {
    return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

bool isCorner(int pos) {
    return pos == 0 || pos == 6 || pos == 42 || pos == 48;
}

struct Move {
    int start;
    int end;
    int score;
    Move(int s, int e) : start(s), end(e), score(0) {}
};

struct State {
    int board[49];
    int player_to_move;
    int king_pos;
    int attacker_count;
    int defender_count;

    State() {
        fill(board, board + 49, EMPTY);
        player_to_move = 0;
        king_pos = -1;
        attacker_count = 0;
        defender_count = 0;
    }

    void generateMoves(vector<Move>& moves) const {
        bool is_attacker = (player_to_move == 0);
        
        for (int pos = 0; pos < 49; ++pos) {
            int p = board[pos];
            if (p == EMPTY) continue;
            if (is_attacker && p != ATTACKER) continue;
            if (!is_attacker && p != DEFENDER && p != KING) continue;
            
            bool is_king = (p == KING);
            
            for (int d : DIRS) {
                int curr = pos;
                while (true) {
                    if (d == 1 && curr % 7 == 6) break;
                    if (d == -1 && curr % 7 == 0) break;
                    
                    curr += d;
                    if (curr < 0 || curr >= 49) break;
                    if (board[curr] != EMPTY) break;
                    
                    if (!is_king && (curr == THRONE || isCorner(curr))) {
                        continue;
                    }
                    
                    Move m(pos, curr);
                    if (is_king) m.score += 100;
                    moves.push_back(m);
                }
            }
        }
        
        // Simple move ordering
        for (auto& m : moves) {
            if (board[m.start] == KING) m.score += 1000;
        }
        
        sort(moves.begin(), moves.end(), [](const Move& a, const Move& b) {
            return a.score > b.score;
        });
    }

    bool isHostile(int x, int y, int capturing_type, bool capturing_king, int k_pos) const {
        if (x < 0 || x >= 7 || y < 0 || y >= 7) return false;
        int pos = y * 7 + x;
        if (isCorner(pos)) return true;
        if (pos == THRONE) {
            if (capturing_king) return false;
            if (capturing_type == ATTACKER) return true;
            if (capturing_type == DEFENDER) return k_pos != THRONE;
        }
        int p = board[pos];
        if (p != EMPTY) {
            if (capturing_type == ATTACKER) return p == ATTACKER;
            else return p != ATTACKER;
        }
        return false;
    }

    bool isKingCaptured(int king_x, int king_y, int k_pos) const {
        int dx[] = {1, -1, 0, 0};
        int dy[] = {0, 0, 1, -1};
        for (int i = 0; i < 4; ++i) {
            if (!isHostile(king_x + dx[i], king_y + dy[i], ATTACKER, true, k_pos)) return false;
        }
        return true;
    }

    State applyMove(const Move& move) const {
        State nextState = *this;
        int start = move.start;
        int end = move.end;
        
        int p = nextState.board[start];
        nextState.board[start] = EMPTY;
        nextState.board[end] = p;
        
        if (p == KING) nextState.king_pos = end;
            
        int end_x = end % 7;
        int end_y = end / 7;
        
        int capturing_type = (p == ATTACKER) ? ATTACKER : DEFENDER;
        
        int dx[] = {1, -1, 0, 0};
        int dy[] = {0, 0, 1, -1};
        
        for (int i = 0; i < 4; ++i) {
            int adj_x = end_x + dx[i];
            int adj_y = end_y + dy[i];
            int adj_pos = adj_y * 7 + adj_x;
            
            if (adj_x < 0 || adj_x >= 7 || adj_y < 0 || adj_y >= 7) continue;
            
            int adj_p = nextState.board[adj_pos];
            if (adj_p == EMPTY) continue;
            
            bool is_enemy = (capturing_type == ATTACKER && (adj_p == DEFENDER || adj_p == KING)) ||
                            (capturing_type == DEFENDER && adj_p == ATTACKER);
                            
            if (is_enemy) {
                if (adj_p == KING && adj_pos == THRONE) {
                    if (nextState.isKingCaptured(adj_x, adj_y, nextState.king_pos)) {
                        nextState.board[adj_pos] = EMPTY;
                        nextState.king_pos = -1;
                    }
                } else if (adj_p == KING && adj_pos != THRONE) {
                    int opp_x = adj_x + dx[i];
                    int opp_y = adj_y + dy[i];
                    if (nextState.isHostile(opp_x, opp_y, capturing_type, true, nextState.king_pos)) {
                        nextState.board[adj_pos] = EMPTY;
                        nextState.king_pos = -1;
                    }
                } else if (adj_p != KING) {
                    int opp_x = adj_x + dx[i];
                    int opp_y = adj_y + dy[i];
                    if (nextState.isHostile(opp_x, opp_y, capturing_type, false, nextState.king_pos)) {
                        nextState.board[adj_pos] = EMPTY;
                        if (adj_p == ATTACKER) nextState.attacker_count--;
                        else nextState.defender_count--;
                    }
                }
            }
        }
        
        nextState.player_to_move = 1 - player_to_move;
        return nextState;
    }

    bool isTerminal(int& winner) const {
        if (king_pos == -1) { winner = 0; return true; }
        if (isCorner(king_pos)) { winner = 1; return true; }
        return false;
    }

    int evaluate() const {
        int winner;
        if (isTerminal(winner)) {
            return (winner == 0) ? 999999 : -999999;
        }
        
        int score = 0;
        score += attacker_count * 100;
        score -= defender_count * 150;
        
        if (king_pos != -1) {
            int kx = king_pos % 7;
            int ky = king_pos / 7;
            
            int min_dist = 999;
            for (int c : CORNERS) {
                int cx = c % 7;
                int cy = c / 7;
                int dist = abs(kx - cx) + abs(ky - cy);
                if (dist < min_dist) min_dist = dist;
            }
            score += (min_dist - 3) * 50;
            
            int mobility = 0;
            bool open_corner_path = false;
            
            for (int d : DIRS) {
                int curr = king_pos;
                bool path_clear = true;
                while (true) {
                    if (d == 1 && curr % 7 == 6) break;
                    if (d == -1 && curr % 7 == 0) break;
                    curr += d;
                    if (curr < 0 || curr >= 49) break;
                    if (board[curr] != EMPTY) {
                        path_clear = false;
                        break;
                    }
                    mobility++;
                }
                if (path_clear) {
                    if (isCorner(curr) || (curr % 7 == 0 || curr % 7 == 6) && (curr / 7 == 0 || curr / 7 == 6)) {
                        open_corner_path = true;
                    }
                }
            }
            
            score -= mobility * 10;
            if (open_corner_path) {
                score -= 50000;
            }
        }
        return score;
    }
};

bool timeout = false;

int minimax(const State& state, int depth, int alpha, int beta, bool is_maximizing, long long start_time) {
    if (getTimeMs() - start_time > TIME_LIMIT_MS) {
        timeout = true;
        return 0;
    }
    
    int winner;
    if (state.isTerminal(winner)) {
        int score = state.evaluate();
        return (score > 0) ? score + depth : score - depth;
    }
    
    if (depth == 0) {
        return state.evaluate();
    }
    
    vector<Move> moves;
    moves.reserve(60);
    state.generateMoves(moves);
    
    if (moves.empty()) {
        return is_maximizing ? -999999 : 999999;
    }
    
    if (is_maximizing) {
        int max_eval = -2000000;
        for (const auto& move : moves) {
            State child = state.applyMove(move);
            int eval = minimax(child, depth - 1, alpha, beta, false, start_time);
            if (timeout) return 0;
            if (eval > max_eval) max_eval = eval;
            alpha = max(alpha, eval);
            if (beta <= alpha) break;
        }
        return max_eval;
    } else {
        int min_eval = 2000000;
        for (const auto& move : moves) {
            State child = state.applyMove(move);
            int eval = minimax(child, depth - 1, alpha, beta, true, start_time);
            if (timeout) return 0;
            if (eval < min_eval) min_eval = eval;
            beta = min(beta, eval);
            if (beta <= alpha) break;
        }
        return min_eval;
    }
}

Move getBestMove(const State& state) {
    long long start_time = getTimeMs();
    timeout = false;
    
    vector<Move> moves;
    moves.reserve(60);
    state.generateMoves(moves);
    
    if (moves.empty()) return Move(-1, -1);
    
    Move best_move = moves[0];
    
    for (int depth = 1; depth < 20; ++depth) {
        Move current_best = moves[0];
        bool is_maximizing = (state.player_to_move == 0);
        int alpha = -2000000;
        int beta = 2000000;
        
        if (is_maximizing) {
            int max_eval = -2000000;
            for (const auto& move : moves) {
                State child = state.applyMove(move);
                int eval = minimax(child, depth - 1, alpha, beta, false, start_time);
                if (timeout) break;
                if (eval > max_eval) {
                    max_eval = eval;
                    current_best = move;
                }
                alpha = max(alpha, eval);
            }
        } else {
            int min_eval = 2000000;
            for (const auto& move : moves) {
                State child = state.applyMove(move);
                int eval = minimax(child, depth - 1, alpha, beta, true, start_time);
                if (timeout) break;
                if (eval < min_eval) {
                    min_eval = eval;
                    current_best = move;
                }
                beta = min(beta, eval);
            }
        }
        
        if (timeout) {
            cerr << "Timeout at depth " << depth << endl;
            break;
        }
        best_move = current_best;
        cerr << "Completed depth " << depth << endl;
    }
    
    return best_move;
}

int main() {
    while (true) {
        int player_idx;
        if (!(cin >> player_idx)) break;
        
        State state;
        state.player_to_move = player_idx;
        
        for (int y = 0; y < 7; y++) {
            string row;
            cin >> row;
            for (int x = 0; x < 7; x++) {
                int pos = y * 7 + x;
                char p_type = row[x];
                if (p_type == 'K') {
                    state.board[pos] = KING;
                    state.king_pos = pos;
                } else if (p_type == 'A') {
                    state.board[pos] = ATTACKER;
                    state.attacker_count++;
                } else if (p_type == 'D') {
                    state.board[pos] = DEFENDER;
                    state.defender_count++;
                }
            }
        }
        
        Move m = getBestMove(state);
        
        if (m.start != -1) {
            int sx = m.start % 7;
            int sy = m.start / 7;
            int ex = m.end % 7;
            int ey = m.end / 7;
            cout << sx << " " << sy << " " << ex << " " << ey << endl;
        } else {
            cout << "WAIT" << endl;
        }
    }
    return 0;
}
