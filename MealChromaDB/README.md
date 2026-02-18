# MealChromaDB - Semantic Recipe Search

A Python-based Semantic Search Engine that helps you find recipes from TheMealDB using vector similarity.

## Features
- **Fetch & Embed**: Fetches all meals (A-Z) from TheMealDB and creates local vector embeddings.
- **100% Local & Free**: Uses `sentence-transformers` models on your machine. No APIs required. 
- **Semantic Search**: Find recipes by meaning (e.g., "healthy breakfast" or "spicy chicken") even if keywords don't match exactly.

## Requirements
- Python 3.8+

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ingest Data** (Run once)
   Fetches meals and populates the local vector database.
   ```bash
   python ingest.py
   ```

3. **Run Search Engine**
   Start the interactive search CLI.
   ```bash
   python main.py
   ```

## Example Queries
- "Something with chicken and mushrooms"
- "Vegetarian pasta dish"
- "Sweet dessert"

Enjoy searching your local recipe database! 🍲
