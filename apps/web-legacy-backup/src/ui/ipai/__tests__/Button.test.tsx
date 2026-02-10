import { render, screen } from "@testing-library/react";
import { Button } from "../Button";
import { tokens } from "@ipai/design-tokens";

describe("Button", () => {
  it("renders primary variant with correct token colors", () => {
    render(<Button variant="primary">Click me</Button>);

    const button = screen.getByText("Click me");
    const computedStyle = window.getComputedStyle(button);

    // Verify token consumption
    expect(computedStyle.backgroundColor).toBe(tokens.color.accent.green);
    expect(computedStyle.color).toBe(tokens.color.text.onAccent);
  });

  it("renders secondary variant with border", () => {
    render(<Button variant="secondary">Secondary</Button>);

    const button = screen.getByText("Secondary");
    const computedStyle = window.getComputedStyle(button);

    // Verify token consumption for border
    expect(computedStyle.border).toContain(tokens.color.accent.teal);
    expect(computedStyle.color).toBe(tokens.color.accent.teal);
  });

  it("renders ghost variant with minimal styling", () => {
    render(<Button variant="ghost">Ghost</Button>);

    const button = screen.getByText("Ghost");
    const computedStyle = window.getComputedStyle(button);

    // Verify token consumption
    expect(computedStyle.color).toBe(tokens.color.primary);
  });

  it("handles different sizes correctly", () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    const button = screen.getByText("Small");

    expect(button.className).toContain("h-10");

    rerender(<Button size="lg">Large</Button>);
    const largeButton = screen.getByText("Large");
    expect(largeButton.className).toContain("h-16");
  });

  it("forwards props correctly", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    const button = screen.getByText("Click");
    button.click();

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("can be disabled", () => {
    render(<Button disabled>Disabled</Button>);

    const button = screen.getByText("Disabled");
    expect(button).toBeDisabled();
  });
});
