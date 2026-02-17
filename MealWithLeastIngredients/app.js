const axios = require("axios");

const BASE_URL = "https://www.themealdb.com/api/json/v1/1/search.php?f=";

async function getMealWithLeastIngredients() {
    let leastMeal = null;
    let leastCount = Infinity;

    for (let charCode = 97; charCode <= 122; charCode++) {
        const letter = String.fromCharCode(charCode);

        try {
            const response = await axios.get(`${BASE_URL}${letter}`);
            const meals = response.data.meals;

            if (!meals) continue;

            for (const meal of meals) {
                let count = 0;

                for (let i = 1; i <= 20; i++) {
                    const ingredient = meal[`strIngredient${i}`];

                    if (ingredient && ingredient.trim() !== "") {
                        count++;
                    }
                }

                if (count < leastCount) {
                    leastCount = count;
                    leastMeal = meal;
                }
            }

        } catch (error) {
            console.error(`Error fetching meals for letter ${letter}`);
        }
    }

    if (leastMeal) {
        console.log("Meal with least ingredients:");
        console.log("Name:", leastMeal.strMeal);
        console.log("Ingredients count:", leastCount);
    } else {
        console.log("No meals found.");
    }
}

getMealWithLeastIngredients();