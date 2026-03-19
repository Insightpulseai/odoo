import { render, screen } from "@testing-library/react";
import { Card } from "../Card";
import { tokens } from "@ipai/design-tokens";

describe("Card", () => {
  it("renders default variant with correct token styles", () => {
    render(<Card variant="default">Card content</Card>);

    const card = screen.getByText("Card content");
    const computedStyle = window.getComputedStyle(card);

    // Verify token consumption
    expect(computedStyle.backgroundColor).toBe(tokens.color.surface);
    expect(computedStyle.boxShadow).toBe(tokens.shadow.default);
  });

  it("renders glass variant with backdrop filter", () => {
    render(<Card variant="glass">Glass card</Card>);

    const card = screen.getByText("Glass card");
    const computedStyle = window.getComputedStyle(card);

    // Verify glass effect properties
    expect(computedStyle.backdropFilter).toContain("blur");
    expect(computedStyle.backgroundColor).toContain("rgba");
  });

  it("renders elevated variant with shadow", () => {
    render(<Card variant="elevated">Elevated card</Card>);

    const card = screen.getByText("Elevated card");
    const computedStyle = window.getComputedStyle(card);

    // Verify token consumption
    expect(computedStyle.backgroundColor).toBe(tokens.color.surface);
    expect(computedStyle.boxShadow).toBe(tokens.shadow.lg);
  });

  it("accepts custom className", () => {
    render(<Card className="custom-class">Content</Card>);

    const card = screen.getByText("Content");
    expect(card.className).toContain("custom-class");
  });

  it("forwards props correctly", () => {
    const handleClick = jest.fn();
    render(<Card onClick={handleClick}>Clickable</Card>);

    const card = screen.getByText("Clickable");
    card.click();

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
