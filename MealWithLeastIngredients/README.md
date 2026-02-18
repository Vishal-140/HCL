# MealWithLeastIngredients

## Prompt to Generate This code

you are a software developer. your task is to write a code in node.js that finds the meal with the least number of ingredients using TheMealDB API. use this API endpoint to fetch meals by first letter, iterate over letter a - z to get all meal, 

https://www.themealdb.com/api/json/v1/1/search.php?f={letter}

api response is something like this, 

{
"meals": [
{
"idMeal": "53262",
"strMeal": "Adana kebab",
"strMealAlternate": null,
"strCategory": "Lamb",
"strArea": "Turkish",
"strInstructions": "step 1\r\nFinely chop the peppers in a food processor, then tip them in a sieve and press into the sieve so that the peppers release all of their juices. Tip into a bowl along with the mince, red pepper paste, pul biber, 1½ tsp flaky sea salt, and 2 tbsp of the oil. Mix together, kneading well for at least 2-3 mins. If you need to, wet your hands with cold water to prevent the mixture from sticking. The mixture should be sticky when ready. Cover and chill for at least 2 hrs, or up to 12 hrs.\r\n\r\nstep 2\r\nWhen ready to cook, heat the grill to high or an oven to 220C/200C fan/gas 6. Divide the mixture into 12 equal portions, around 85g each. If you’d like to skewer them, divide into 8 equal portions and roll into balls. Using wet hands, thread the balls onto the end of the skewers, massaging the mixture down the skewers in between the palms of your hands, until evenly distributed. Ensure that the mixture is fully wrapped tightly around the skewers without any exposed metal. Alternatively, lay them on a large baking tray lined with parchment paper if cooking in the oven, or foil if cooking under the grill. Shape into 20cm-long köfte. Wet your fingers with a little cold water and make indents all along the köfte for the traditional shape.\r\n\r\nstep 3\r\nGently brush each köfte with the remaining 1 tbsp oil and cook under the grill, on the top shelf for 10-12 mins, turning regularly, or cook in the oven for 16-18 mins, until crispy on the outside and juicy in the middle",
"strMealThumb": "https://www.themealdb.com/images/media/meals/04axct1763793018.jpg",
"strTags": null,
"strYoutube": "https://www.youtube.com/watch?v=Wj7sXu9B_ME",
"strIngredient1": "Romano Pepper",
"strIngredient2": "Lamb Mince",
"strIngredient3": "Red Pepper Paste",
"strIngredient4": "Pul Biber",
"strIngredient5": "Sunflower Oil",
"strIngredient6": "",
"strIngredient7": "",
"strIngredient8": "",
"strIngredient9": "",
"strIngredient10": "",
"strIngredient11": "",
"strIngredient12": "",
"strIngredient13": "",
"strIngredient14": "",
"strIngredient15": "",
"strIngredient16": "",
"strIngredient17": "",
"strIngredient18": "",
"strIngredient19": "",
"strIngredient20": "",
"strMeasure1": "2 large",
"strMeasure2": "800g",
"strMeasure3": "3  tablespoons",
"strMeasure4": "1 tablespoon",
"strMeasure5": "3  tablespoons",
"strMeasure6": " ",
"strMeasure7": " ",
"strMeasure8": " ",
"strMeasure9": " ",
"strMeasure10": " ",
"strMeasure11": " ",
"strMeasure12": " ",
"strMeasure13": " ",
"strMeasure14": " ",
"strMeasure15": " ",
"strMeasure16": " ",
"strMeasure17": " ",
"strMeasure18": " ",
"strMeasure19": " ",
"strMeasure20": " ",
"strSource": "https://www.bbcgoodfood.com/recipes/adana-kebab",
"strImageSource": null,
"strCreativeCommonsConfirmed": null,
"dateModified": "2025-11-22 06:28:49"
},


]
}




## Optimized Prompt - MealWithLeastIngredients

Objective

You are a senior Node.js developer.

Write a clean, efficient, and production-ready Node.js script that finds the meal with the least number of valid ingredients using TheMealDB API.

API Details

Use the following endpoint to fetch meals by first letter:

https://www.themealdb.com/api/json/v1/1/search.php?f={letter}

Requirements:

Iterate from a to z

Fetch all meals

Skip letters that return "meals": null

Ingredient Counting Rules

Each meal contains the following fields:

strIngredient1 ... strIngredient20


Count only ingredients that:

Are not null

Are not empty string ""

Are not whitespace " "

Are not undefined

Ignore all empty ingredient fields.

Optimization Requirements

The solution must:

Use axios

Use async/await

Handle API errors properly using try/catch

Avoid duplicate meals (use idMeal if necessary)

Be memory efficient

Avoid unnecessary console logs

Fetch letters sequentially (to prevent rate limits)

Keep only the current minimum meal (do not store all meals)

Expected Output

At the end, print:

Meal Name

Meal ID

Total Ingredient Count

List of Ingredients

Example Output
Meal with least ingredients:
Name: XYZ
ID: 12345
Ingredient Count: 3
Ingredients: Salt, Oil, Egg

Code Quality Guidelines

Use clean and meaningful variable names

Write modular functions where appropriate

Add short and clear comments

Follow Node.js best practices

Edge Case Handling

If no meals are found, print:

No meals found.