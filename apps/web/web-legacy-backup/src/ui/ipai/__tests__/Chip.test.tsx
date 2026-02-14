import { render, screen } from "@testing-library/react";
import { Chip } from "../Chip";
import { tokens } from "@ipai/design-tokens";

describe("Chip", () => {
  it("renders default variant with correct token colors", () => {
    render(<Chip variant="default">Default chip</Chip>);

    const chip = screen.getByText("Default chip");
    const computedStyle = window.getComputedStyle(chip);

    // Verify token consumption
    expect(computedStyle.backgroundColor).toBe(tokens.color.canvas);
    expect(computedStyle.color).toBe(tokens.color.text.primary);
  });

  it("renders accent variant with teal token", () => {
    render(<Chip variant="accent">Accent chip</Chip>);

    const chip = screen.getByText("Accent chip");
    const computedStyle = window.getComputedStyle(chip);

    // Verify token consumption (with alpha channel)
    expect(computedStyle.color).toBe(tokens.color.accent.teal);
    expect(computedStyle.backgroundColor).toContain("rgba");
  });

  it("renders success variant with green token", () => {
    render(<Chip variant="success">Success chip</Chip>);

    const chip = screen.getByText("Success chip");
    const computedStyle = window.getComputedStyle(chip);

    // Verify token consumption (with alpha channel)
    expect(computedStyle.color).toBe(tokens.color.accent.green);
    expect(computedStyle.backgroundColor).toContain("rgba");
  });

  it("accepts custom className", () => {
    render(<Chip className="custom-class">Content</Chip>);

    const chip = screen.getByText("Content");
    expect(chip.className).toContain("custom-class");
  });

  it("forwards props correctly", () => {
    const handleClick = jest.fn();
    render(<Chip onClick={handleClick}>Clickable</Chip>);

    const chip = screen.getByText("Clickable");
    chip.click();

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
