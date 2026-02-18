import re
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

    def parse_query(self, query):
        """Extracts filters, intent, and result count from the query."""
        filters = {}
        limit = 5  # Default limit
        is_greeting = False
        
        # 0. Intent Detection: Greetings
        greetings = ["hello", "hi", "hey", "good morning", "good evening"]
        if query.lower().strip() in greetings:
            return query, {}, 0, True

        # 1. Extraction: "without <ingredient>"
        exclusion_match = re.search(r"without\s+([\w\s]+)", query, re.IGNORECASE)
        if exclusion_match:
            filters['exclude_ingredient'] = exclusion_match.group(1).strip()
            query = re.sub(r"without\s+[\w\s]+", "", query, flags=re.IGNORECASE)

        # 2. Constraint: "less than <X> ingredients"
        count_match = re.search(r"less than\s+(\d+)\s+ingredients", query, re.IGNORECASE)
        if count_match:
            filters['max_ingredients'] = int(count_match.group(1))
            query = re.sub(r"less than\s+\d+\s+ingredients", "", query, flags=re.IGNORECASE)

        # 3. Result Count: "one result", "2 results", "show 3 meals"
        # Look for a number explicitly mentioned regarding results/meals or just "one result"
        
        # A. "one result only" or "one result"
        if "one result" in query.lower():
            limit = 1
            query = re.sub(r"one result( only)?", "", query, flags=re.IGNORECASE)
        
        # B. "show <Number>" pattern (e.g. "show 3", "show 10")
        show_match = re.search(r"\bshow\s+(\d+)\b", query, re.IGNORECASE)
        if show_match:
            limit = int(show_match.group(1))
            query = re.sub(r"\bshow\s+\d+\b", "", query, flags=re.IGNORECASE)
            
        # C. "<Number> ... results/meals/recipes"
        # e.g. "3 vegetarian meals", "2 results", "5 recipes"
        # We restrict this to the START of the query to avoid matching "Chicken 65 meals"
        else:
            limit_match = re.search(r"^\s*(\d+)\b\s+(?:[\w\s]*?)(?:result|meal|recipe)s?", query, re.IGNORECASE)
            if limit_match:
                # Be careful not to match "Chicken 65" unless it says "Chicken 65 meals" (which is unlikely but possible)
                # If the match includes "result" or "meal" or "recipe", it's safer.
                matched_text = limit_match.group(0)
                if any(k in matched_text.lower() for k in ["result", "meal", "recipe"]):
                     limit = int(limit_match.group(1))
                     # We remove the number but maybe keep the rest? 
                     # "3 vegetarian meals" -> remove "3".
                     query = re.sub(r"\b" + str(limit) + r"\b", "", query, count=1)
                     
                     # If the word "result" or "results" follows immediately or later, remove it too.
                     query = re.sub(r"\bresults?\b", "", query, flags=re.IGNORECASE)

        return query.strip(), filters, limit, False

    def calculate_similarity(self, distance):
        """Converts L2 distance to similarity score (0-1)."""
        # User prompt example checks "best_score < 0.55".
        # Let's use: similarity = 1 / (1 + distance)
        return 1 / (1 + distance)

    def search_meals(self, query):
        """Searches ChromaDB with semantic search + post-filtering."""
        cleaned_query, filters, limit, is_greeting = self.parse_query(query)
        
        if is_greeting:
            return "GREETING", []

        # Check if query is empty after cleaning
        if not cleaned_query:
             return "EMPTY_QUERY", []

        query_embedding = self.model.encode([cleaned_query]).tolist()
        
        # Fetch more to allow for filtering and threshold checking
        fetch_k = max(50, limit * 5)
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=fetch_k,
            include=["documents", "metadatas", "distances"]
        )
        
        final_results = []
        seen_ids = set()
        
        if results['documents']:
            metas = results['metadatas'][0]
            docs = results['documents'][0]
            ids = results['ids'][0]
            dists = results['distances'][0]
            
            # --- SIMILARITY & THRESHOLD CHECK ---
            scores = [self.calculate_similarity(d) for d in dists]
            
            if not scores:
                return "NO_MATCH", []
            
            best_score = scores[0]
            # Average of top 5 (or fewer if less than 5 results)
            top_n_scores = scores[:min(5, len(scores))]
            avg_score = sum(top_n_scores) / len(top_n_scores)
            
            # Strict thresholds (Calibrated):
            # "Chicken" (Valid) ~ 0.49
            # "Aloo Paratha" (Invalid) ~ 0.41
            # Rejection Threshold: Best < 0.43 OR Avg < 0.40
            if best_score < 0.43 or avg_score < 0.40:
                return "LOW_CONFIDENCE", []

            for i, (meta, doc, mid, score) in enumerate(zip(metas, docs, ids, scores)):
                if mid in seen_ids: continue
                
                # --- APPLY FILTERS ---
                
                # 1. Exclusion (Ingredient)
                if 'exclude_ingredient' in filters:
                    excluded = filters['exclude_ingredient'].lower()
                    if excluded in doc.lower():
                        continue
                        
                # 2. Max Ingredients
                if 'max_ingredients' in filters:
                    if meta['ingredientCount'] >= filters['max_ingredients']:
                        continue
                        
                # Determine Confidence Level
                if score > 0.52:
                    confidence = "HIGH"
                elif score > 0.46:
                    confidence = "MEDIUM"
                else:
                    confidence = "LOW"
                    
                meta['score'] = f"{score:.2f}"
                meta['confidence'] = confidence
                
                # Pass
                final_results.append((meta, doc))
                seen_ids.add(mid)
                
                if len(final_results) >= limit:
                    break
                    
        return "SUCCESS", final_results

    def display_recipe(self, index, meta, doc):
        """Formats and prints recipe details."""
        print(f"==================================================")
        print(f"RESULT #{index + 1}: {meta['mealName']}")
        print(f"==================================================")
        print(f"Category: {meta['category']} | Area: {meta['area']}")
        print(f"Ingredients Count: {meta['ingredientCount']}")
        print(f"Confidence: {meta.get('confidence', 'N/A')} (Score: {meta.get('score', 'N/A')})")

        # Extract parts from document text
        try:
            lines = doc.split('\n')
            ingredients_line = next((line for line in lines if line.startswith("Ingredients:")), "Ingredients: N/A")
            instructions_start = next((i for i, line in enumerate(lines) if line.startswith("Instructions:")), -1)
            
            ingredients = ingredients_line.replace("Ingredients:", "").strip()
            
            if instructions_start != -1:
                instructions = "\n".join(lines[instructions_start:]).replace("Instructions:", "").strip()
                # Clean up instructions a bit (truncate if too long or format)
                instructions = textwrap.shorten(instructions, width=300, placeholder="...")
            else:
                instructions = "See details online."
            
            print(f"\nINGREDIENTS:\n{ingredients}")
            print(f"\nINSTRUCTIONS:\n{instructions}")
            
        except Exception:
            print("\n📄 RAW DETAILS:")
            print(doc)
            
        print(f"\n==================================================\n")

    def run(self):
        print("\n--- 🍲 Meal Semantic Search 🍲 ---")
        print("Type a query to find recipes! (e.g., 'spicy chicken', 'vegetarian pasta')")
        print("Type 'exit' to quit.\n")
        
        while True:
            try:
                user_input = input("Search: ").strip()
            except KeyboardInterrupt:
                print("\n\nGoodbye! Happy Cooking!")
                exit(0)
                
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye! Happy Cooking!")
                break
                
            if not user_input:
                continue

            print("Searching...", end="\r")
            status, results = self.search_meals(user_input)
            
            if status == "GREETING":
                print("\nHello 👋 I can help you find meals. Try something like 'chicken meal'.\n")
                continue
            elif status == "LOW_CONFIDENCE" or status == "NO_MATCH":
                  print("\nSorry, I couldn't find a close match for that meal.\n")
                  continue
            elif status == "EMPTY_QUERY":
                 print("\nPlease provide a food-related search term.\n")
                 continue
            
            if not results:
                print("No meals found matching your criteria.")
                continue
                
            # print(f"\nFound {len(results)} relevant recipes for '{user_input}':")
            
            for i, (meta, doc) in enumerate(results):
                self.display_recipe(i, meta, doc)

if __name__ == "__main__":
    app = MealSearchEngine()
    app.run()
