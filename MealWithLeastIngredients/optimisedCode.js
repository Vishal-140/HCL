const axios = require("axios");

const BASE_URL = "https://www.themealdb.com/api/json/v1/1/search.php?f=";

/**
 * Count valid ingredients in a meal object
 */
function countValidIngredients(meal) {
    const ingredients = [];

    for (let i = 1; i <= 20; i++) {
        const ingredient = meal[`strIngredient${i}`];

        if (
            ingredient &&
            typeof ingredient === "string" &&
            ingredient.trim() !== ""
        ) {
            ingredients.push(ingredient.trim());
        }
    }

    return ingredients;
}

/**
 * Fetch meals for a specific letter
 */
async function fetchMealsByLetter(letter) {
    try {
        const response = await axios.get(`${BASE_URL}${letter}`);
        return response.data.meals; // may be null
    } catch (error) {
        console.error(`Error fetching meals for letter "${letter}"`);
        return null;
    }
}

/**
 * Main function to find meal with least ingredients
 */
async function findMealWithLeastIngredients() {
    let minMeal = null;
    let minCount = Infinity;
    const seenMealIds = new Set();

    for (let charCode = 97; charCode <= 122; charCode++) {
        const letter = String.fromCharCode(charCode);

        const meals = await fetchMealsByLetter(letter);

        if (!meals) continue;

        for (const meal of meals) {
            if (seenMealIds.has(meal.idMeal)) continue;

            seenMealIds.add(meal.idMeal);

            const ingredients = countValidIngredients(meal);
            const ingredientCount = ingredients.length;

            if (ingredientCount < minCount) {
                minCount = ingredientCount;
                minMeal = {
                    name: meal.strMeal,
                    id: meal.idMeal,
                    ingredients,
                };
            }
        }
    }

    if (!minMeal) {
        console.log("No meals found.");
        return;
    }

    console.log("Meal with least ingredients:");
    console.log(`Name: ${minMeal.name}`);
    console.log(`ID: ${minMeal.id}`);
    console.log(`Ingredient Count: ${minCount}`);
    console.log(`Ingredients: ${minMeal.ingredients.join(", ")}`);
}

findMealWithLeastIngredients();
