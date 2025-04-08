import json
import re
from typing import Any, Dict, List

def load_data(file_path: str) -> List[Dict[str, Any]]:
    """Load and preprocess the manga data from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return preprocess_data(data)

def parse_int(value: str) -> int:
    """Strip non‑digits and convert to int, defaulting to 0."""
    # Remove everything except digits
    digits = re.sub(r'[^\d]', '', value or '')
    return int(digits) if digits.isdigit() else 0

def preprocess_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean and normalize the manga data."""
    cleaned_data = []
    for entry in data:
        cleaned = {}

        # Title
        cleaned['Title'] = entry.get('Title', '').strip()

        # Score → float
        score_str = entry.get('Score', '').strip()
        cleaned['Score'] = float(score_str) if re.match(r'^\d+(\.\d+)?$', score_str) else 0.0

        # Rank → int (strip '#')
        cleaned['Rank'] = parse_int(entry.get('Rank', ''))

        # Popularity → int (strip '#')
        cleaned['Popularity'] = parse_int(entry.get('Popularity', ''))

        # Members → int
        cleaned['Members'] = parse_int(entry.get('Members', ''))

        # Favourites → int
        cleaned['Favourites'] = parse_int(entry.get('Favourites', ''))

        # Recommended / Mixed Feelings / Not Recommended → int
        cleaned['Recommended']     = parse_int(entry.get('Recommended', ''))
        cleaned['Mixed Feelings'] = parse_int(entry.get('Mixed Feelings', ''))
        cleaned['Not Recommended']= parse_int(entry.get('Not Recommended', ''))

        # Genres → list of lowercase strings
        genres = entry.get('Genres', [])
        cleaned['Genres'] = [g.strip().lower() for g in genres] if isinstance(genres, list) else []

        # Themes → list of lowercase strings
        themes = entry.get('Themes', [])
        cleaned['Themes'] = [t.strip().lower() for t in themes] if isinstance(themes, list) else []

        # Synopsis → single‑line string
        synopsis = entry.get('Synopsis', '')
        cleaned['Synopsis'] = re.sub(r'[\r\n]+', ' ', synopsis).strip()

        # Demographic → lowercase, default 'unknown'
        demo = entry.get('Demographic', '') or 'Unknown'
        cleaned['Demographic'] = demo.strip().lower()

        # Image URL → keep as‑is
        cleaned['Image URL'] = entry.get('Image URL', '').strip()

        cleaned_data.append(cleaned)

    return cleaned_data

def save_cleaned_data(cleaned_data: List[Dict[str, Any]], output_path: str) -> None:
    """Save the cleaned data to a new JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file  = "manga_data_new.json"
    output_file = "cleaned_manga_data.json"

    cleaned = load_data(input_file)
    save_cleaned_data(cleaned, output_file)
    print(f"Cleaned data saved to {output_file}")
