import chromadb
from sentence_transformers import SentenceTransformer
import textwrap

# Configuration
CHROMA_PATH = "./chroma_data"
COLLECTION_NAME = "meal_collection"
MODEL_NAME = "all-MiniLM-L6-v2"

class MealSearchEngine:
    def __init__(self):
        print("Initializing Meal Search Engine...")
        # 1. Connect to Vector DB
        try:
            self.client = chromadb.PersistentClient(path=CHROMA_PATH)
            self.collection = self.client.get_collection(COLLECTION_NAME)
        except Exception as e:
            print(f"Error connecting to ChromaDB: {e}")
            print("Did you run `ingest.py` first?")
            exit(1)
            
        # 2. Load Embedding Model (Local)
        print("Loading local embedding model...")
        self.model = SentenceTransformer(MODEL_NAME)

    def search_meals(self, query, n_results=3):
        """Searches ChromaDB for relevant meals using vector similarity."""
        query_embedding = self.model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas"]
        )
        return results

    def display_recipe(self, index, meta, doc):
        """Formats and prints recipe details."""
        print(f"\n{'='*50}")
        print(f"RESULT #{index + 1}: {meta['mealName']}")
        print(f"{'='*50}")
        print(f"Category: {meta['category']} | Area: {meta['area']}")
        print(f"Ingredients Count: {meta['ingredientCount']}")
        print("-" * 50)
        
        # Extract parts from document text for cleaner display
        # The document format is:
        # Name: ...
        # Category: ...
        # Area: ...
        # Ingredients: ...
        # Instructions: ...
        
        try:
            # Simple parsing based on known structure
            lines = doc.split('\n')
            ingredients_line = next((line for line in lines if line.startswith("Ingredients:")), "Ingredients: N/A")
            instructions_start = next((i for i, line in enumerate(lines) if line.startswith("Instructions:")), -1)
            
            ingredients = ingredients_line.replace("Ingredients:", "").strip()
            
            if instructions_start != -1:
                instructions = "\n".join(lines[instructions_start:]).replace("Instructions:", "").strip()
            else:
                instructions = "See details online."
            
            print(f"\n📝 INGREDIENTS:\n{textwrap.fill(ingredients, width=80)}")
            print(f"\n🍳 INSTRUCTIONS:\n{textwrap.fill(instructions, width=80)}")
            
        except Exception:
            # Fallback if parsing fails
            print("\n📄 RAW DETAILS:")
            print(doc)
            
        print(f"\n{'='*50}\n")

    def run(self):
        print("\n--- 🍲 Meal Semantic Search 🍲 ---")
        print("Type a query to find recipes! (e.g., 'spicy chicken', 'vegetarian pasta')")
        print("Type 'exit' to quit.\n")
        
        while True:
            user_input = input("Search: ").strip()
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye! Happy Cooking!")
                break
                
            if not user_input:
                continue

            print("Searching...", end="\r")
            results = self.search_meals(user_input)
            
            metas = results['metadatas'][0]
            docs = results['documents'][0]
            
            if not metas:
                print("No relevant meals found.")
                continue
                
            print(f"\nFound {len(metas)} relevant recipes for '{user_input}':")
            
            for i, (meta, doc) in enumerate(zip(metas, docs)):
                self.display_recipe(i, meta, doc)

if __name__ == "__main__":
    app = MealSearchEngine()
    app.run()
