import {
  webLightTheme,
  webDarkTheme,
  BrandVariants,
  createLightTheme,
  createDarkTheme,
  Theme,
} from "@fluentui/react-components";

/**
 * TBWA Brand Colors
 * Primary: Yellow (#F1C100)
 * Secondary: Black (#000000)
 */
const tbwaBrand: BrandVariants = {
  10: "#060400", // Darkest black
  20: "#140F00",
  30: "#2A1F00",
  40: "#3D2E00",
  50: "#513E00",
  60: "#6B5300",
  70: "#8C6C00",
  80: "#B88E00",
  90: "#F1C100", // TBWA Yellow (primary)
  100: "#FFD84D",
  110: "#FFE680",
  120: "#FFF0B3",
  130: "#FFF7D6",
  140: "#FFFBEB",
  150: "#FFFEF6",
  160: "#FFFFFF",
};

/**
 * Light theme with TBWA yellow as primary brand color
 */
export const tbwaLightTheme: Theme = {
  ...createLightTheme(tbwaBrand),
  colorBrandForeground1: "#F1C100", // TBWA Yellow
  colorBrandForeground2: "#B88E00", // Darker yellow for hover
  colorNeutralForeground1: "#000000", // Black text
  colorNeutralForeground2: "#3D2E00", // Slightly lighter for secondary text
};

/**
 * Dark theme with TBWA yellow as primary brand color
 * (Optional - use if you implement dark mode toggle)
 */
export const tbwaDarkTheme: Theme = {
  ...createDarkTheme(tbwaBrand),
  colorBrandForeground1: "#FFD84D", // Lighter yellow for dark backgrounds
  colorBrandForeground2: "#F1C100", // TBWA Yellow
  colorNeutralForeground1: "#FFFFFF", // White text
};

/**
 * Export default theme (light)
 */
export const tbwaTheme = tbwaLightTheme;
