from urllib import error, parse, request
import json
import logging

from mcp.server.fastmcp import FastMCP

LOGGER = logging.getLogger(__name__)
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

API_ROOT = "https://www.themealdb.com/api/json/v1/1/"
USER_AGENT = "MealHubMCP/1.0"
DEFAULT_TIMEOUT = 15  # seconds
SEARCH_LIMIT = 25
FILTER_LIMIT = 50
MAX_INGREDIENT_FIELDS = 20


class MealServiceError(RuntimeError):
    pass


class MealDBClient:
    def __init__(self, api_root=API_ROOT, timeout=DEFAULT_TIMEOUT):
        self.api_root = api_root if api_root.endswith("/") else f"{api_root}/"
        self.timeout = timeout

    def _url(self, endpoint, params=None):
        params = params or {}
        query = parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
        url = parse.urljoin(self.api_root, endpoint)
        return f"{url}?{query}" if query else url

    def _fetch(self, endpoint, params=None):
        url = self._url(endpoint, params)
        LOGGER.debug("Fetching %s", url)
        req = request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status != 200:
                    raise MealServiceError(f"TheMealDB returned HTTP {resp.status} for {url}")
                try:
                    return json.load(resp)
                except json.JSONDecodeError as exc:  # pragma: no cover - best effort parsing guard
                    raise MealServiceError("TheMealDB response was not valid JSON") from exc
        except error.URLError as exc:
            raise MealServiceError(f"Problem reaching TheMealDB ({url}): {exc}") from exc

    def search_by_name(self, query):
        payload = self._fetch("search.php", {"s": query})
        return payload.get("meals") or []

    def filter_by_ingredient(self, ingredient):
        payload = self._fetch("filter.php", {"i": ingredient})
        return payload.get("meals") or []

    def lookup(self, meal_id):
        payload = self._fetch("lookup.php", {"i": meal_id})
        return payload.get("meals") or []

    def random(self):
        payload = self._fetch("random.php")
        return payload.get("meals") or []


def _summarize_search(meal):
    return {
        "id": meal.get("idMeal"),
        "name": meal.get("strMeal"),
        "area": meal.get("strArea"),
        "category": meal.get("strCategory"),
        "thumb": meal.get("strMealThumb"),
    }


def _summarize_ingredient_card(meal):
    return {
        "id": meal.get("idMeal"),
        "name": meal.get("strMeal"),
        "thumb": meal.get("strMealThumb"),
    }


def _gather_ingredients(meal):
    items = []
    for index in range(1, MAX_INGREDIENT_FIELDS + 1):
        name = (meal.get(f"strIngredient{index}") or "").strip()
        measure = (meal.get(f"strMeasure{index}") or "").strip()
        if name:
            items.append({"name": name, "measure": measure or None})
    return items


def _normalize_detail(meal):
    return {
        "id": meal.get("idMeal"),
        "name": meal.get("strMeal"),
        "category": meal.get("strCategory"),
        "area": meal.get("strArea"),
        "instructions": meal.get("strInstructions"),
        "image": meal.get("strMealThumb"),
        "source": meal.get("strSource"),
        "youtube": meal.get("strYoutube"),
        "ingredients": _gather_ingredients(meal),
    }


client = MealDBClient()
mcp = FastMCP("meals")


def _clamp_limit(limit, *, ceiling):
    if not isinstance(limit, int):
        raise ValueError("limit must be an integer")
    return max(1, min(limit, ceiling))


@mcp.tool()
def search_meals_by_name(query, limit=5):
    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")

    limit = _clamp_limit(limit, ceiling=SEARCH_LIMIT)
    meals = client.search_by_name(query)
    if not meals:
        return {"message": "no matches", "results": []}

    return {"results": [_summarize_search(meal) for meal in meals[:limit]]}


@mcp.tool()
def meals_by_ingredient(ingredient, limit=12):
    ingredient = ingredient.strip()
    if not ingredient:
        raise ValueError("ingredient must not be empty")

    limit = _clamp_limit(limit, ceiling=FILTER_LIMIT)
    meals = client.filter_by_ingredient(ingredient)
    if not meals:
        return {"message": "no matches", "results": []}

    return {"results": [_summarize_ingredient_card(meal) for meal in meals[:limit]]}


@mcp.tool()
def meal_details(meal_id):
    normalized_id = str(meal_id).strip()
    if not normalized_id:
        raise ValueError("id must not be empty")

    meals = client.lookup(normalized_id)
    if not meals:
        return {"message": "no matches", "meal": None}

    return {"meal": _normalize_detail(meals[0])}


@mcp.tool()
def random_meal():
    meals = client.random()
    if not meals:
        return {"message": "no matches", "meal": None}
    return {"meal": _normalize_detail(meals[0])}


if __name__ == "__main__":
    mcp.run()
