import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MovieCard } from "@/components/movies/MovieCard";
import { batman, dune } from "@/test/fixtures";
import { renderWithProviders } from "@/test/test-utils";

describe("MovieCard", () => {
  it("renders confirmed API fields, the poster, and a details link", () => {
    renderWithProviders(<MovieCard movie={dune} />);

    expect(screen.getByRole("heading", { name: dune.title })).toBeInTheDocument();
    expect(screen.getByText(String(dune.release_year))).toBeInTheDocument();
    expect(screen.getByText(dune.average_rating!.toFixed(1))).toBeInTheDocument();
    expect(screen.getByText("Science Fiction · Adventure")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: `Poster for ${dune.title}` })).toHaveAttribute("src", dune.poster_url);
    expect(screen.getByRole("link", { name: `View details for ${dune.title}` })).toHaveAttribute("href", `/movies/${dune.id}`);
  });

  it("renders a poster fallback while keeping the available metadata", () => {
    renderWithProviders(<MovieCard movie={batman} />);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.getAllByText(batman.title).length).toBeGreaterThan(0);
    expect(screen.getByText("2005")).toBeInTheDocument();
    expect(screen.getByText("8.2")).toBeInTheDocument();
  });

  it("handles a movie with no year, rating, genres, or poster", () => {
    const unavailable = {
      ...dune,
      average_rating: null,
      genres: [],
      poster_url: null,
      ratings_count: null,
      release_year: null,
    };

    renderWithProviders(<MovieCard movie={unavailable} />);

    expect(screen.getByText("Year unavailable")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.queryByText("·")).not.toBeInTheDocument();
  });
});
