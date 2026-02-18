import requests
import chromadb
from sentence_transformers import SentenceTransformer
import string
from tqdm import tqdm
import os

# Configuration
CHROMA_PATH = "./chroma_data"
COLLECTION_NAME = "meal_collection"
MODEL_NAME = "all-MiniLM-L6-v2"
BASE_URL = "https://www.themealdb.com/api/json/v1/1/search.php?f="

def fetch_all_meals():
    """Fetches all meals from TheMealDB API (A-Z)."""
    all_meals = []
    print("Fetching meals from TheMealDB...")
    
    for letter in tqdm(string.ascii_lowercase, desc="Fetcher"):
        try:
            response = requests.get(f"{BASE_URL}{letter}", timeout=10)
            data = response.json()
            if data and data['meals']:
                all_meals.extend(data['meals'])
        except Exception as e:
            print(f"Error fetching letter {letter}: {e}")
            
    print(f"Total meals found: {len(all_meals)}")
    return all_meals

def prepare_meal_text(meal):
    """Formats meal data into structured text and extracts metadata."""
    ingredients = []
    count = 0
    
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}")
        if ing and ing.strip():
            ingredients.append(ing.strip())
            count += 1
            
    # Structured Text for RAG context
    structured_text = f"""Name: {meal['strMeal']}
Category: {meal['strCategory']}
Area: {meal['strArea']}
Ingredients: {', '.join(ingredients)}
Instructions: {meal['strInstructions']}
Total Ingredients: {count}
"""

    metadata = {
        "id": meal['idMeal'],
        "mealName": meal['strMeal'],
        "category": meal['strCategory'] or "Unknown",
        "area": meal['strArea'] or "Unknown",
        "ingredientCount": count
    }
    
    return structured_text, metadata, meal['idMeal']

def ingest_data():
    print("--- Starting Data Ingestion ---")
    
    # 1. Init Vector DB & Model
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Reset collection
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
        
    collection = client.create_collection(name=COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Fetch Data
    meals = fetch_all_meals()
    if not meals:
        print("No meals fetched. Exiting.")
        return

    # 3. Prepare Batches
    documents = []
    metadatas = []
    ids = []
    
    print("Processing meals...")
    for meal in tqdm(meals, desc="Processing"):
        text, meta, meal_id = prepare_meal_text(meal)
        
        # Avoid duplicates in local list (API might return dupes?)
        if meal_id not in ids:
            documents.append(text)
            metadatas.append(meta)
            ids.append(meal_id)
            
    # 4. Embed & Store
    print(f"Generating embeddings for {len(documents)} unique meals...")
    embeddings = model.encode(documents, show_progress_bar=True).tolist()
    
    print("Storing in ChromaDB...")
    batch_size = 100
    for i in tqdm(range(0, len(ids), batch_size), desc="Storing"):
        end = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end],
            embeddings=embeddings[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end]
        )
        
    print(f"Successfully stored {len(ids)} meals in ChromaDB.")

if __name__ == "__main__":
    ingest_data()
