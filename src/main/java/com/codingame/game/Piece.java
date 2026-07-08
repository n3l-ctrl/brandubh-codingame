package com.codingame.game;

public class Piece {
    private PieceType type;
    private int x;
    private int y;
    
    public Piece(PieceType type, int x, int y) {
        this.type = type;
        this.x = x;
        this.y = y;
    }
    
    public PieceType getType() { return type; }
    public int getX() { return x; }
    public int getY() { return y; }
    
    public void setPosition(int x, int y) {
        this.x = x;
        this.y = y;
    }
}
