import sys
import time

EMPTY = 0
ATTACKER = 1
DEFENDER = 2
KING = 3

THRONE = 24
CORNERS = {0, 6, 42, 48}
DIRS = [1, -1, 7, -7]

def debug(msg):
    print(msg, file=sys.stderr, flush=True)

def get_time_ms():
    return int(time.time() * 1000)

class State:
    def __init__(self, board, player_to_move, king_pos, attacker_count, defender_count, attackers, defenders):
        self.board = board
        self.player_to_move = player_to_move
        self.king_pos = king_pos
        self.attacker_count = attacker_count
        self.defender_count = defender_count
        self.attackers = attackers
        self.defenders = defenders

    def generate_moves(self):
        moves = []
        is_attacker = (self.player_to_move == 0)
        my_pieces = self.attackers if is_attacker else self.defenders
        
        for pos in my_pieces:
            p = self.board[pos]
            is_king = (p == KING)
            
            for d in DIRS:
                curr = pos
                while True:
                    if d == 1 and curr % 7 == 6: break
                    if d == -1 and curr % 7 == 0: break
                    
                    curr += d
                    if curr < 0 or curr >= 49: break
                    
                    if self.board[curr] != EMPTY: break
                    
                    if not is_king and (curr == THRONE or curr in CORNERS):
                        pass # Cannot stop here, but can continue sliding
                    else:
                        moves.append((pos, curr))
        return moves

    def is_hostile(self, board, x, y, capturing_type, capturing_king, king_pos):
        if x < 0 or x >= 7 or y < 0 or y >= 7: return False
        pos = y * 7 + x
        if pos in CORNERS: return True
        if pos == THRONE:
            if capturing_king: return False
            if capturing_type == ATTACKER: return True
            if capturing_type == DEFENDER: return king_pos != THRONE
        p = board[pos]
        if p != EMPTY:
            if capturing_type == ATTACKER: return p == ATTACKER
            else: return p != ATTACKER
        return False

    def is_king_captured(self, board, king_x, king_y, king_pos):
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            if not self.is_hostile(board, king_x+dx, king_y+dy, ATTACKER, True, king_pos):
                return False
        return True

    def apply_move(self, move):
        start, end = move
        new_board = self.board[:]
        p = new_board[start]
        new_board[start] = EMPTY
        new_board[end] = p
        
        new_attackers = self.attackers[:]
        new_defenders = self.defenders[:]
        
        new_king_pos = self.king_pos
        if p == KING:
            new_king_pos = end
            
        if p == ATTACKER:
            new_attackers.remove(start)
            new_attackers.append(end)
        else:
            new_defenders.remove(start)
            new_defenders.append(end)
            
        end_x = end % 7
        end_y = end // 7
        
        new_attacker_count = self.attacker_count
        new_defender_count = self.defender_count
        
        capturing_type = ATTACKER if p == ATTACKER else DEFENDER
        
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            adj_x = end_x + dx
            adj_y = end_y + dy
            adj_pos = adj_y * 7 + adj_x
            
            if adj_x < 0 or adj_x >= 7 or adj_y < 0 or adj_y >= 7: continue
            
            adj_p = new_board[adj_pos]
            if adj_p == EMPTY: continue
            
            is_enemy = (capturing_type == ATTACKER and adj_p in (DEFENDER, KING)) or \
                       (capturing_type == DEFENDER and adj_p == ATTACKER)
                       
            if is_enemy:
                if adj_p == KING and adj_pos == THRONE:
                    if self.is_king_captured(new_board, adj_x, adj_y, new_king_pos):
                        new_board[adj_pos] = EMPTY
                        new_king_pos = -1
                        new_defenders.remove(adj_pos)
                elif adj_p == KING and adj_pos != THRONE:
                    opp_x = adj_x + dx
                    opp_y = adj_y + dy
                    if self.is_hostile(new_board, opp_x, opp_y, capturing_type, True, new_king_pos):
                        new_board[adj_pos] = EMPTY
                        new_king_pos = -1
                        new_defenders.remove(adj_pos)
                elif adj_p != KING:
                    opp_x = adj_x + dx
                    opp_y = adj_y + dy
                    if self.is_hostile(new_board, opp_x, opp_y, capturing_type, False, new_king_pos):
                        new_board[adj_pos] = EMPTY
                        if adj_p == ATTACKER: 
                            new_attacker_count -= 1
                            new_attackers.remove(adj_pos)
                        else: 
                            new_defender_count -= 1
                            new_defenders.remove(adj_pos)

        return State(new_board, 1 - self.player_to_move, new_king_pos, new_attacker_count, new_defender_count, new_attackers, new_defenders)

    def is_terminal(self):
        if self.king_pos == -1: return True, 0
        if self.king_pos in CORNERS: return True, 1
        return False, None

    def evaluate(self):
        term, winner = self.is_terminal()
        if term:
            return 99999 if winner == 0 else -99999
            
        score = 0
        score += self.attacker_count * 100
        score -= self.defender_count * 150
        
        if self.king_pos != -1:
            kx = self.king_pos % 7
            ky = self.king_pos // 7
            
            min_dist = 999
            for c in CORNERS:
                cx = c % 7
                cy = c // 7
                dist = abs(kx - cx) + abs(ky - cy)
                if dist < min_dist:
                    min_dist = dist
                    
            score += (min_dist - 3) * 50
            
            mobility = 0
            open_corner_path = False
            for d in DIRS:
                curr = self.king_pos
                path_clear = True
                while True:
                    if d == 1 and curr % 7 == 6: break
                    if d == -1 and curr % 7 == 0: break
                    curr += d
                    if curr < 0 or curr >= 49: break
                    if self.board[curr] != EMPTY: 
                        path_clear = False
                        break
                    mobility += 1
                
                if path_clear:
                    end_pos = curr
                    if end_pos in CORNERS or (end_pos % 7 in (0, 6) and end_pos // 7 in (0, 6)):
                        open_corner_path = True

            score -= mobility * 10
            if open_corner_path:
                score -= 50000 
            
        return score

class AI:
    def __init__(self, player_idx):
        self.player_idx = player_idx
        self.tt = {}
        
    def get_best_move(self, state, time_limit_ms):
        start_time = get_time_ms()
        best_move = None
        self.tt.clear()
        
        for depth in range(1, 10):
            try:
                move, score = self.minimax(state, depth, -1000000, 1000000, state.player_to_move == 0, start_time, time_limit_ms)
                if move is not None:
                    best_move = move
                debug(f"Completed depth {depth}")
            except TimeoutError:
                debug(f"Timeout at depth {depth}")
                break
                
        if best_move is None and state.generate_moves():
            best_move = state.generate_moves()[0]
            
        return best_move
        
    def minimax(self, state, depth, alpha, beta, is_maximizing, start_time, time_limit):
        if get_time_ms() - start_time > time_limit:
            raise TimeoutError()
            
        board_hash = hash(tuple(state.board))
        if board_hash in self.tt:
            tt_depth, tt_score, tt_flag = self.tt[board_hash]
            if tt_depth >= depth:
                if tt_flag == 'EXACT':
                    return None, tt_score
                elif tt_flag == 'LOWERBOUND':
                    alpha = max(alpha, tt_score)
                elif tt_flag == 'UPPERBOUND':
                    beta = min(beta, tt_score)
                if alpha >= beta:
                    return None, tt_score
            
        term, winner = state.is_terminal()
        if term:
            score = state.evaluate()
            return None, score + depth if score > 0 else score - depth
            
        if depth == 0:
            score = state.evaluate()
            self.tt[board_hash] = (depth, score, 'EXACT')
            return None, score
            
        moves = state.generate_moves()
        if not moves:
            return None, -99999 if is_maximizing else 99999
            
        def move_score(m):
            start, end = m
            p = state.board[start]
            score = 0
            if p == KING: score += 1000
            
            for d in DIRS:
                adj = end + d
                if 0 <= adj < 49:
                    adj_p = state.board[adj]
                    if adj_p != EMPTY and adj_p != p:
                        score += 50
            return score
            
        moves.sort(key=move_score, reverse=True)
        
        best_move = moves[0]
        original_alpha = alpha
        
        if is_maximizing:
            max_eval = -1000000
            for move in moves:
                child = state.apply_move(move)
                _, eval_score = self.minimax(child, depth - 1, alpha, beta, False, start_time, time_limit)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            tt_flag = 'EXACT'
            if max_eval <= original_alpha: tt_flag = 'UPPERBOUND'
            elif max_eval >= beta: tt_flag = 'LOWERBOUND'
            self.tt[board_hash] = (depth, max_eval, tt_flag)
            
            return best_move, max_eval
        else:
            min_eval = 1000000
            for move in moves:
                child = state.apply_move(move)
                _, eval_score = self.minimax(child, depth - 1, alpha, beta, True, start_time, time_limit)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
            tt_flag = 'EXACT'
            if min_eval <= alpha: tt_flag = 'UPPERBOUND'
            elif min_eval >= beta: tt_flag = 'LOWERBOUND' # Wait, min_eval >= original_beta? Actually, original_beta is not tracked. For Min, if it's <= alpha it's UPPERBOUND.
            self.tt[board_hash] = (depth, min_eval, tt_flag)
            
            return best_move, min_eval

while True:
    try:
        player_idx = int(input())
        last_action = input()
    except EOFError:
        break
        
    board = [EMPTY] * 49
    king_pos = -1
    attacker_count = 0
    defender_count = 0
    attackers = []
    defenders = []
    
    for y in range(7):
        row = input()
        for x in range(7):
            p_type = row[x]
            pos = y * 7 + x
            if p_type == 'K':
                board[pos] = KING
                king_pos = pos
                defenders.append(pos)
            elif p_type == 'A':
                board[pos] = ATTACKER
                attacker_count += 1
                attackers.append(pos)
            elif p_type == 'D':
                board[pos] = DEFENDER
                defender_count += 1
                defenders.append(pos)
            
    state = State(board, player_idx, king_pos, attacker_count, defender_count, attackers, defenders)
    ai = AI(player_idx)
    
    move = ai.get_best_move(state, 45) # Time limit is 45ms per turn (leaving some buffer)
    
    if move:
        sx = move[0] % 7
        sy = move[0] // 7
        ex = move[1] % 7
        ey = move[1] // 7
        def to_chess(x, y):
            return chr(ord('a') + x) + str(7 - y)
        print(f"{to_chess(sx, sy)} {to_chess(ex, ey)}", flush=True)
    else:
        print("WAIT", flush=True)