package com.codingame.game;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.codingame.gameengine.core.AbstractPlayer.TimeoutException;
import com.codingame.gameengine.core.AbstractReferee;
import com.codingame.gameengine.core.MultiplayerGameManager;
import com.codingame.gameengine.module.entities.GraphicEntityModule;
import com.google.inject.Inject;
import com.codingame.gameengine.module.tooltip.TooltipModule;

public class Referee extends AbstractReferee {
    @Inject private MultiplayerGameManager<Player> gameManager;
    @Inject private GraphicEntityModule graphicEntityModule;
    @Inject private TooltipModule tooltipModule;
    
    private Board board;
    private String lastActionStr = "NONE";
    private com.codingame.gameengine.module.entities.Text[] lastMoveTexts = new com.codingame.gameengine.module.entities.Text[2];
    private com.codingame.gameengine.module.entities.Rectangle[][] squareEntities = new com.codingame.gameengine.module.entities.Rectangle[7][7];
    private java.util.Map<Piece, com.codingame.gameengine.module.entities.Sprite> pieceEntities = new java.util.HashMap<>();
    private static final int CELL_SIZE = 126;
    private static final int OFFSET_X = 1920 / 2 - (Board.SIZE * CELL_SIZE) / 2;
    private static final int OFFSET_Y = 1080 / 2 - (Board.SIZE * CELL_SIZE) / 2;

    @Override
    public void init() {
        board = new Board();
        gameManager.setTurnMaxTime(100);
        gameManager.setMaxTurns(200);
        drawBoard();
        drawHud();
        updateTooltips();
    }
    
    private void drawHud() {
        for (Player player : gameManager.getPlayers()) {
            int x = player.getIndex() == 0 ? 100 : 1920 - 400;
            int y = 100;
            // HUD Background
            graphicEntityModule.createRectangle()
                .setX(x - 20).setY(y - 20)
                .setWidth(340).setHeight(120)
                .setFillColor(0x222222)
                .setLineColor(0x8B4513)
                .setLineWidth(4)
                .setAlpha(0.8);
                
            graphicEntityModule.createSprite()
                .setImage(player.getAvatarToken())
                .setX(x).setY(y)
                .setBaseWidth(80).setBaseHeight(80);
                
            graphicEntityModule.createText(player.getNicknameToken())
                .setX(x + 100).setY(y + 10)
                .setFontSize(35)
                .setFillColor(0xFFFFFF)
                .setFontWeight(com.codingame.gameengine.module.entities.Text.FontWeight.BOLD);
                
            graphicEntityModule.createText(player.getIndex() == 0 ? "ATTACKERS" : "DEFENDERS")
                .setX(x + 100).setY(y + 55)
                .setFontSize(22)
                .setFillColor(0xAAAAAA);
                
            // Last Move Box
            graphicEntityModule.createRectangle()
                .setX(x - 20).setY(y + 110)
                .setWidth(340).setHeight(40)
                .setFillColor(0x111111)
                .setLineColor(0x8B4513)
                .setLineWidth(4)
                .setAlpha(0.8);
                
            lastMoveTexts[player.getIndex()] = graphicEntityModule.createText("")
                .setX(x + 150).setY(y + 130)
                .setAnchor(0.5)
                .setFontSize(24)
                .setFillColor(0xEEEEEE);
        }
    }
    

    private void drawBoard() {
        graphicEntityModule.createSprite()
            .setImage("board.png")
            .setX(1920 / 2)
            .setY(1080 / 2)
            .setAnchorX(0.5)
            .setAnchorY(0.5)
            .setBaseWidth(1000)
            .setBaseHeight(1000)
            .setZIndex(-1);

        for (int i = 0; i < Board.SIZE; i++) {
            String col = String.valueOf((char)('a' + i));
            graphicEntityModule.createText(col).setX(OFFSET_X + i * CELL_SIZE + CELL_SIZE/2).setY(OFFSET_Y - 40).setAnchor(0.5).setFontSize(40).setFillColor(0xDDDDDD);
            graphicEntityModule.createText(col).setX(OFFSET_X + i * CELL_SIZE + CELL_SIZE/2).setY(OFFSET_Y + Board.SIZE * CELL_SIZE + 40).setAnchor(0.5).setFontSize(40).setFillColor(0xDDDDDD);
            String row = String.valueOf((char)('7' - i));
            graphicEntityModule.createText(row).setX(OFFSET_X - 40).setY(OFFSET_Y + i * CELL_SIZE + CELL_SIZE/2).setAnchor(0.5).setFontSize(40).setFillColor(0xDDDDDD);
            graphicEntityModule.createText(row).setX(OFFSET_X + Board.SIZE * CELL_SIZE + 40).setY(OFFSET_Y + i * CELL_SIZE + CELL_SIZE/2).setAnchor(0.5).setFontSize(40).setFillColor(0xDDDDDD);
        }

        for (int x = 0; x < Board.SIZE; x++) {
            for (int y = 0; y < Board.SIZE; y++) {
                squareEntities[x][y] = graphicEntityModule.createRectangle()
                    .setX(OFFSET_X + x * CELL_SIZE)
                    .setY(OFFSET_Y + y * CELL_SIZE)
                    .setWidth(CELL_SIZE)
                    .setHeight(CELL_SIZE)
                    .setFillColor(0x000000)
                    .setAlpha(0.0)
                    .setZIndex(50);
            }
        }
        
        for (Piece p : board.getPieces()) {
            String image = "attacker.png";
            if (p.getType() == PieceType.DEFENDER) image = "defender.png";
            else if (p.getType() == PieceType.KING) image = "king.png";
            
            com.codingame.gameengine.module.entities.Sprite s = graphicEntityModule.createSprite()
                .setImage(image)
                .setBaseWidth(CELL_SIZE - 20)
                .setBaseHeight(CELL_SIZE - 20)
                .setX(OFFSET_X + p.getX() * CELL_SIZE + 10)
                .setY(OFFSET_Y + p.getY() * CELL_SIZE + 10)
                .setZIndex(10);
            
            pieceEntities.put(p, s);
        }
    }
    
    private void updateTooltips() {
        for (int x = 0; x < Board.SIZE; x++) {
            for (int y = 0; y < Board.SIZE; y++) {
                String coord = String.format("%c%c", (char)('a' + x), (char)('7' - y));
                Piece p = board.getPiece(x, y);
                String text = coord;
                if (p != null) {
                    if (p.getType() == PieceType.KING) text += "\nKing";
                    else if (p.getType() == PieceType.ATTACKER) text += "\nAttacker";
                    else if (p.getType() == PieceType.DEFENDER) text += "\nDefender";
                } else if (board.isThrone(x, y)) {
                    text += "\nThrone";
                } else if (board.isCorner(x, y)) {
                    text += "\nCorner";
                }
                tooltipModule.setTooltipText(squareEntities[x][y], text);
            }
        }
    }

    private java.util.Map<String, Integer> stateHistory = new java.util.HashMap<>();

    private String getBoardStateHash(int currentPlayerIdx) {
        StringBuilder sb = new StringBuilder();
        sb.append(currentPlayerIdx).append(";");
        for (int y = 0; y < Board.SIZE; y++) {
            for (int x = 0; x < Board.SIZE; x++) {
                Piece p = board.getPiece(x, y);
                if (p != null) sb.append(p.getType().name().charAt(0));
                else sb.append(".");
            }
        }
        return sb.toString();
    }

    private int currentTurn;

    @Override
    public void gameTurn(int turn) {
        this.currentTurn = turn;
        
        int playerIdx = (turn - 1) % 2; // player 0: Attackers, player 1: Defenders
        Player player = gameManager.getPlayer(playerIdx);
        
        if (!hasValidMoves(playerIdx)) {
            gameManager.addTooltip(player, player.getNicknameToken() + " has no valid moves!");
            player.deactivate("No valid moves!");
            endGame(1 - playerIdx);
            return;
        }
        
        sendInputs(player);
        player.execute();

        try {
            List<String> outputs = player.getOutputs();
            String output = outputs.get(0).trim();
            Move move = parseMove(output);
            
            if (move == null) {
                throw new InvalidActionException("Invalid move format. Expected: d2 d4");
            }
            
            applyMove(playerIdx, move);
            checkCaptures(move);
            
            lastActionStr = String.format("%c%c%c%c", 
                (char)('a' + move.startX), (char)('7' - move.startY), 
                (char)('a' + move.endX), (char)('7' - move.endY));
            gameManager.addToGameSummary(player.getNicknameToken() + " played " + lastActionStr);
            lastMoveTexts[playerIdx].setText(lastActionStr);
            
            updateTooltips();
            
            String state = getBoardStateHash(1 - playerIdx);
            stateHistory.put(state, stateHistory.getOrDefault(state, 0) + 1);
            if (stateHistory.get(state) >= 3) {
                gameManager.addTooltip(player, "Repeated position 3 times! " + player.getNicknameToken() + " loses!");
                endGame(1 - playerIdx);
                return;
            }
            
            checkWinCondition();

        } catch (TimeoutException e) {
            gameManager.addToGameSummary(player.getNicknameToken() + " timeout!");
            player.setScore(-1);
            player.deactivate("Timeout!");
            endGame(1 - playerIdx);
        } catch (InvalidActionException e) {
            gameManager.addToGameSummary(player.getNicknameToken() + " made an invalid action: " + e.getMessage());
            player.setScore(-1);
            player.deactivate(e.getMessage());
            endGame(1 - playerIdx);
        }
    }
    
    private void sendInputs(Player player) {
        int playerIdx = player.getIndex(); // 0 for Attackers, 1 for Defenders
        player.sendInputLine(String.valueOf(playerIdx));
        player.sendInputLine(lastActionStr);
        
        for (int y = 0; y < Board.SIZE; y++) {
            StringBuilder sb = new StringBuilder();
            for (int x = 0; x < Board.SIZE; x++) {
                Piece p = board.getPiece(x, y);
                if (p == null) sb.append(".");
                else if (p.getType() == PieceType.ATTACKER) sb.append("A");
                else if (p.getType() == PieceType.DEFENDER) sb.append("D");
                else if (p.getType() == PieceType.KING) sb.append("K");
            }
            player.sendInputLine(sb.toString());
        }
    }
    
    private Move parseMove(String output) throws InvalidActionException {
        Pattern p = Pattern.compile("^\\s*([a-gA-G])([1-7])\\s*([a-gA-G])([1-7])\\s*$");
        Matcher m = p.matcher(output);
        if (m.find()) {
            int x1 = Character.toLowerCase(m.group(1).charAt(0)) - 'a';
            int y1 = '7' - m.group(2).charAt(0);
            int x2 = Character.toLowerCase(m.group(3).charAt(0)) - 'a';
            int y2 = '7' - m.group(4).charAt(0);
            return new Move(x1, y1, x2, y2);
        }
        return null;
    }
    
    private void applyMove(int playerIdx, Move move) throws InvalidActionException {
        Piece p = board.getPiece(move.startX, move.startY);
        if (p == null) throw new InvalidActionException("No piece at start position");
        
        boolean isAttacker = p.getType() == PieceType.ATTACKER;
        if ((playerIdx == 0 && !isAttacker) || (playerIdx == 1 && isAttacker)) {
            throw new InvalidActionException("Piece belongs to opponent");
        }
        
        if (move.startX == move.endX && move.startY == move.endY) {
            throw new InvalidActionException("Start is the same as destination");
        }
        
        if (board.getPiece(move.endX, move.endY) != null) {
            throw new InvalidActionException("Destination is occupied");
        }
        
        if (move.startX != move.endX && move.startY != move.endY) {
            throw new InvalidActionException("Move is not orthogonal");
        }
        
        if (move.startX == move.endX) {
            int min = Math.min(move.startY, move.endY);
            int max = Math.max(move.startY, move.endY);
            for (int y = min + 1; y < max; y++) {
                if (board.getPiece(move.startX, y) != null) throw new InvalidActionException("Path is blocked");
            }
        } else {
            int min = Math.min(move.startX, move.endX);
            int max = Math.max(move.startX, move.endX);
            for (int x = min + 1; x < max; x++) {
                if (board.getPiece(x, move.startY) != null) throw new InvalidActionException("Path is blocked");
            }
        }
        
        if (board.isThrone(move.endX, move.endY) || board.isCorner(move.endX, move.endY)) {
            if (p.getType() != PieceType.KING) {
                throw new InvalidActionException("Moves a non-King piece to the Throne or a Corner");
            }
        }
        
        board.movePiece(p, move.endX, move.endY);
        com.codingame.gameengine.module.entities.Sprite s = pieceEntities.get(p);
        if (s != null) {
            s.setX(OFFSET_X + move.endX * CELL_SIZE + 10);
            s.setY(OFFSET_Y + move.endY * CELL_SIZE + 10);
        }
    }
    
    private void checkCaptures(Move move) {
        Piece moved = board.getPiece(move.endX, move.endY);
        if (moved == null) return;
        
        int[][] dirs = {{1,0}, {-1,0}, {0,1}, {0,-1}};
        for (int[] d : dirs) {
            int adjX = move.endX + d[0];
            int adjY = move.endY + d[1];
            Piece adj = board.getPiece(adjX, adjY);
            
            if (adj != null && isEnemy(moved, adj)) {
                if (adj.getType() == PieceType.KING && adj.getX() == 3 && adj.getY() == 3) {
                    if (isKingCaptured(adj)) {
                        board.removePiece(adj);
                        com.codingame.gameengine.module.entities.Sprite s = pieceEntities.get(adj);
                        if (s != null) s.setVisible(false);
                    }
                } else {
                    int oppX = adjX + d[0];
                    int oppY = adjY + d[1];
                    boolean capturingKing = adj.getType() == PieceType.KING;
                    if (isHostileSquare(oppX, oppY, moved.getType(), capturingKing)) {
                        board.removePiece(adj);
                        com.codingame.gameengine.module.entities.Sprite s = pieceEntities.get(adj);
                        if (s != null) s.setVisible(false);
                    }
                }
            }
        }
    }
    
    private boolean isEnemy(Piece p1, Piece p2) {
        if (p1.getType() == PieceType.ATTACKER) return p2.getType() != PieceType.ATTACKER;
        return p2.getType() == PieceType.ATTACKER;
    }
    
    private boolean isHostileSquare(int x, int y, PieceType capturingType, boolean capturingKing) {
        if (x < 0 || x >= Board.SIZE || y < 0 || y >= Board.SIZE) return false;
        
        if (board.isCorner(x, y)) return true;
        
        if (board.isThrone(x, y)) {
            if (capturingKing) return false;
            if (capturingType == PieceType.ATTACKER) return true;
            if (capturingType == PieceType.DEFENDER) {
                return board.getPiece(3, 3) == null; // only hostile to defenders if King is not on it
            }
        }
        
        Piece p = board.getPiece(x, y);
        if (p != null) {
            if (capturingType == PieceType.ATTACKER) return p.getType() == PieceType.ATTACKER;
            return p.getType() != PieceType.ATTACKER;
        }
        return false;
    }
    
    private boolean isKingCaptured(Piece king) {
        // This is only called when King is on the throne
        int[][] dirs = {{1,0}, {-1,0}, {0,1}, {0,-1}};
        for (int[] d : dirs) {
            int x = king.getX() + d[0];
            int y = king.getY() + d[1];
            if (!isHostileSquare(x, y, PieceType.ATTACKER, true)) {
                return false;
            }
        }
        return true;
    }
    
    private boolean hasValidMoves(int playerIdx) {
        boolean isAttacker = playerIdx == 0;
        for (Piece p : board.getPieces()) {
            if ((p.getType() == PieceType.ATTACKER) == isAttacker) {
                int[][] dirs = {{1,0}, {-1,0}, {0,1}, {0,-1}};
                for (int[] d : dirs) {
                    int nx = p.getX() + d[0];
                    int ny = p.getY() + d[1];
                    if (nx >= 0 && nx < Board.SIZE && ny >= 0 && ny < Board.SIZE) {
                        if (board.getPiece(nx, ny) == null) {
                            if (board.isThrone(nx, ny) || board.isCorner(nx, ny)) {
                                if (p.getType() == PieceType.KING) return true;
                            } else {
                                return true;
                            }
                        }
                    }
                }
            }
        }
        return false;
    }

    private boolean checkEncirclement() {
        boolean[][] visited = new boolean[Board.SIZE][Board.SIZE];
        java.util.Queue<int[]> queue = new java.util.LinkedList<>();
        
        for (int x = 0; x < Board.SIZE; x++) {
            for (int y = 0; y < Board.SIZE; y++) {
                if (x == 0 || x == Board.SIZE - 1 || y == 0 || y == Board.SIZE - 1) {
                    Piece p = board.getPiece(x, y);
                    if (p != null) {
                        if (p.getType() == PieceType.KING || p.getType() == PieceType.DEFENDER) {
                            return false; 
                        }
                    }
                    if (p == null || p.getType() != PieceType.ATTACKER) {
                        queue.add(new int[]{x, y});
                        visited[x][y] = true;
                    }
                }
            }
        }
        
        int[][] dirs = {{1,0}, {-1,0}, {0,1}, {0,-1}};
        while (!queue.isEmpty()) {
            int[] curr = queue.poll();
            int cx = curr[0];
            int cy = curr[1];
            
            Piece p = board.getPiece(cx, cy);
            if (p != null && (p.getType() == PieceType.KING || p.getType() == PieceType.DEFENDER)) {
                return false; 
            }
            
            for (int[] d : dirs) {
                int nx = cx + d[0];
                int ny = cy + d[1];
                if (nx >= 0 && nx < Board.SIZE && ny >= 0 && ny < Board.SIZE && !visited[nx][ny]) {
                    Piece np = board.getPiece(nx, ny);
                    if (np == null || np.getType() != PieceType.ATTACKER) {
                        visited[nx][ny] = true;
                        queue.add(new int[]{nx, ny});
                    }
                }
            }
        }
        return true;
    }
    
    private void checkWinCondition() {
        Piece king = null;
        for (Piece p : board.getPieces()) {
            if (p.getType() == PieceType.KING) king = p;
        }
        
        if (king == null) {
            gameManager.addTooltip(gameManager.getPlayer(0), "Attackers captured the King!");
            gameManager.addToGameSummary("Attackers captured the King!");
            endGame(0);
        } else if (board.isCorner(king.getX(), king.getY())) {
            gameManager.addTooltip(gameManager.getPlayer(1), "The King escaped!");
            gameManager.addToGameSummary("The King escaped!");
            endGame(1);
        } else if (checkEncirclement()) {
            gameManager.addTooltip(gameManager.getPlayer(0), "Attackers encircled Defenders!");
            gameManager.addToGameSummary("Attackers encircled Defenders!");
            endGame(0);
        }
    }
    
    private void endGame(int winnerIdx) {
        if (winnerIdx != -1) {
            gameManager.getPlayer(winnerIdx).setScore(1);
            gameManager.getPlayer(1 - winnerIdx).setScore(-1);
        } else {
            gameManager.getPlayer(0).setScore(0);
            gameManager.getPlayer(1).setScore(0);
        }
        
        // --- Outro Cinematic ---
        graphicEntityModule.createRectangle()
            .setX(0).setY(0).setWidth(1920).setHeight(1080)
            .setFillColor(0x000000).setAlpha(0.0)
            .setZIndex(100)
            .setAlpha(0.8, com.codingame.gameengine.module.entities.Curve.EASE_IN_AND_OUT);
            
        if (winnerIdx != -1) {
            Player winner = gameManager.getPlayer(winnerIdx);
            graphicEntityModule.createText(winner.getNicknameToken() + " WINS!")
                .setX(1920/2).setY(1080/2 - 50)
                .setAnchor(0.5)
                .setFontSize(100)
                .setFillColor(0xFFD700)
                .setFontWeight(com.codingame.gameengine.module.entities.Text.FontWeight.BOLD)
                .setZIndex(101)
                .setAlpha(0.0)
                .setScale(0.0)
                .setAlpha(1.0, com.codingame.gameengine.module.entities.Curve.EASE_IN_AND_OUT)
                .setScale(1.0, com.codingame.gameengine.module.entities.Curve.ELASTIC);
                
            graphicEntityModule.createText(winner.getIndex() == 0 ? "ATTACKERS" : "DEFENDERS")
                .setX(1920/2).setY(1080/2 + 70)
                .setAnchor(0.5)
                .setFontSize(60)
                .setFillColor(0xAAAAAA)
                .setZIndex(101)
                .setAlpha(0.0)
                .setScale(0.0)
                .setAlpha(1.0, com.codingame.gameengine.module.entities.Curve.EASE_IN_AND_OUT)
                .setScale(1.0, com.codingame.gameengine.module.entities.Curve.ELASTIC);
        } else {
            graphicEntityModule.createText("DRAW")
                .setX(1920/2).setY(1080/2)
                .setAnchor(0.5)
                .setFontSize(150)
                .setFillColor(0xAAAAAA)
                .setFontWeight(com.codingame.gameengine.module.entities.Text.FontWeight.BOLD)
                .setZIndex(101)
                .setAlpha(0.0)
                .setScale(0.0)
                .setAlpha(1.0, com.codingame.gameengine.module.entities.Curve.EASE_IN_AND_OUT)
                .setScale(1.0, com.codingame.gameengine.module.entities.Curve.ELASTIC);
        }
        // -----------------------
        
        gameManager.endGame();
    }
}
