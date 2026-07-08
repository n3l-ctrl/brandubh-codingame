package com.codingame.game;

import java.util.ArrayList;
import java.util.List;

public class Board {
    public static final int SIZE = 7;
    private Piece[][] grid;
    private List<Piece> pieces;

    public Board() {
        grid = new Piece[SIZE][SIZE];
        pieces = new ArrayList<>();
        initBoard();
    }

    private void initBoard() {
        // Attackers (8)
        addPiece(new Piece(PieceType.ATTACKER, 3, 0));
        addPiece(new Piece(PieceType.ATTACKER, 3, 1));
        addPiece(new Piece(PieceType.ATTACKER, 0, 3));
        addPiece(new Piece(PieceType.ATTACKER, 1, 3));
        addPiece(new Piece(PieceType.ATTACKER, 6, 3));
        addPiece(new Piece(PieceType.ATTACKER, 5, 3));
        addPiece(new Piece(PieceType.ATTACKER, 3, 6));
        addPiece(new Piece(PieceType.ATTACKER, 3, 5));

        // Defenders (4)
        addPiece(new Piece(PieceType.DEFENDER, 3, 2));
        addPiece(new Piece(PieceType.DEFENDER, 2, 3));
        addPiece(new Piece(PieceType.DEFENDER, 4, 3));
        addPiece(new Piece(PieceType.DEFENDER, 3, 4));

        // King (1)
        addPiece(new Piece(PieceType.KING, 3, 3));
    }

    private void addPiece(Piece p) {
        grid[p.getX()][p.getY()] = p;
        pieces.add(p);
    }

    public Piece getPiece(int x, int y) {
        if (x < 0 || x >= SIZE || y < 0 || y >= SIZE) return null;
        return grid[x][y];
    }
    
    public void movePiece(Piece p, int destX, int destY) {
        grid[p.getX()][p.getY()] = null;
        p.setPosition(destX, destY);
        grid[destX][destY] = p;
    }

    public void removePiece(Piece p) {
        grid[p.getX()][p.getY()] = null;
        pieces.remove(p);
    }
    
    public List<Piece> getPieces() {
        return pieces;
    }
    
    public boolean isCorner(int x, int y) {
        return (x == 0 && y == 0) || (x == 0 && y == SIZE - 1) || 
               (x == SIZE - 1 && y == 0) || (x == SIZE - 1 && y == SIZE - 1);
    }
    
    public boolean isThrone(int x, int y) {
        return x == 3 && y == 3;
    }
}
