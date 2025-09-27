# Meal Hub

Meal Hub is a lightweight MCP server that wraps TheMealDB API so other projects can search, filter, and inspect recipes without dealing with HTTP plumbing.

## Quick Start
- Install dependencies with `uv sync`.
- Launch the server with `uv run mealhub.py`.

## Tools
- `search_meals_by_name(query, limit)` returns basic metadata for up to 25 meals that match a name.
- `meals_by_ingredient(ingredient, limit)` locates meals that include a given ingredient.
- `meal_details(meal_id)` fetches full instructions and ingredient list for a specific meal.
- `random_meal()` grabs a single random recipe for inspiration.
