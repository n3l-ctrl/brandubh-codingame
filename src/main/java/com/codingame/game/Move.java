package com.codingame.game;

public class Move {
    public int startX, startY;
    public int endX, endY;

    public Move(int startX, int startY, int endX, int endY) {
        this.startX = startX;
        this.startY = startY;
        this.endX = endX;
        this.endY = endY;
    }
}
