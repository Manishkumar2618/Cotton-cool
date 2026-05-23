package com.trendlab;

public class CustomizationProcessor {
    public static String formatDesign(String productId, String font, String color, String placement) {
        return String.format("Product: %s | Font: %s | Color: %s | Placement: %s", productId, font, color, placement);
    }

    public static double calculateCustomizationCost(boolean hasUpload, String placement) {
        double base = 49.99;
        if (placement != null && placement.toLowerCase().contains("back")) {
            base += 20.0;
        }
        return hasUpload ? base : 0.0;
    }

    public static void main(String[] args) {
        System.out.println(formatDesign("shirt-01", "Arial", "Black", "Center"));
        System.out.println("Customization fee: " + calculateCustomizationCost(true, "Back"));
    }
}
