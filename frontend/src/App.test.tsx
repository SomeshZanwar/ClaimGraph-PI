import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("renders the product home page", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", {
        name: /claims investigation built around evidence/i,
      }),
    ).toBeInTheDocument();
  });

  it("renders a custom not found page", () => {
    render(
      <MemoryRouter initialEntries={["/missing-page"]}>
        <App />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { name: /page not found/i }),
    ).toBeInTheDocument();
  });
});
