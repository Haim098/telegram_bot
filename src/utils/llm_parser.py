import google.generativeai as genai
import json
from typing import List, Dict

# שימוש במפתח ה-API הנכון
GOOGLE_API_KEY = "AIzaSyCbtz8BeP-j5ltgL4Vq8pheHvaY1w-ktSo"

genai.configure(api_key=GOOGLE_API_KEY)

def parseUnstructuredList(text: str) -> List[Dict[str, str]]:
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Parse the following unstructured shopping list in Hebrew into structured items.
    Each item should have:
    - name: The exact name of the item as written by the user (do not change plural to singular or vice versa)
    - quantity: The number of items (default to 1 if not specified)
    - notes: Any additional information or instructions about the item
    - category: Choose the most appropriate category from: כללי, פירות וירקות, מוצרי חלב וביצים, בשר ועופות, מאפים, מוצרי יסוד, מוצרי ניקיון וטיפוח, משקאות

    Be sure to:
    1. Keep the item name exactly as written by the user, whether it's singular or plural
    2. Extract the quantity, even if it's written as a word (e.g., "שלוש" should be converted to 3)
    3. Capture any notes or special instructions about the item
    4. Categorize each item based on its nature
    5. If no quantity is specified, set it to 1, but keep the item name as is (e.g., "ביצים" should remain "ביצים" with quantity 1, not changed to "ביצה")

    Unstructured list:
    {text}

    Please respond with only the JSON array, without any additional text or formatting:
    [
      {{"name": "item name as written", "quantity": number, "notes": "additional notes", "category": "category name"}},
      ...
    ]
    """

    try:
        result = model.generate_content(prompt)
        parsed_text = result.text

        # Remove any potential Markdown formatting
        parsed_text = parsed_text.replace('```json', '').replace('```', '').strip()

        # Try to find a valid JSON array within the response
        import re
        match = re.search(r'\[[\s\S]*\]', parsed_text)
        if match:
            parsed_text = match.group(0)

        try:
            return json.loads(parsed_text)
        except json.JSONDecodeError as e:
            print(f'Failed to parse JSON: {parsed_text}', e)
            raise ValueError('Invalid JSON response from AI model')

    except Exception as e:
        print(f'Error parsing unstructured list with Gemini: {e}')
        raise
