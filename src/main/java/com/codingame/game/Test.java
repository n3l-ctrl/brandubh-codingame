package com.codingame.game;
import java.lang.reflect.Method;
import com.codingame.gameengine.module.tooltip.TooltipModule;

public class Test {
    public static void main(String[] args) {
        for (Method m : TooltipModule.class.getDeclaredMethods()) {
            System.out.println(m.getName() + " " + m.getParameterCount());
        }
    }
}
