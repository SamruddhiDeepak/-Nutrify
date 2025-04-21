# Nutrify 
Nutrify is a food information app designed to promote informed food choices. By scanning barcodes on food packages, Nutrify provides essential details such as ingredients, nutritional values, certifications, and food regulations. With an integrated Botpress-powered chatbot and recipe suggestions, Nutrify simplifies your journey toward better food awareness.

# Features
1. Barcode Scanner: Uload barcoe image/Manually enter food product barcodes to access:
-Ingredients
-Nutritional values
-Relevant food regulations
-Certifications (e.g., organic, GMO-free)
-Eco score
-Nutri Score
-Packaging details
2. Smart Chatbot: Get quick answers about food, regulations, and processing.
-Restricted to a curated knowledge base.
-Marks unrelated queries as "Out of Context."
3. Recipe Corner: Enter ingredients you have at home and explore recipes powered by Spoonacular API.
# Tech Stack🛠️
Streamlit: User interface for barcode scanning and recipe suggestions.
Python: Business logic and API integrations.
Botpress: Chatbot engine for answering food-related queries.
Open Food Facts API: Fetches product details from a comprehensive food database.

# Setup and Installation

Follow these steps to run Nutrify locally:

1. Clone the Repository

```bash
git clone https://github.com/SamruddhiDeepak/-Nutrify.git
cd Nutrify
```

2. Set Up the Environment

-Install Python 3.9+.
-Create and activate a virtual environment:

```bash
python -m venv venv
source env/bin/activate   # For Linux/macOS
venv\Scripts\activate      # For Windows
```

-Install dependencies(may take some time):
```bash
pip install -r requirements.txt
```

3. Run the App

```bash
streamlit run app.py
```

# Usage Instructions
1. Scan Barcodes: Use the camera on your device to capture a food product barcode, save it in your gallery and upload it or enter the barcode number manually.
View product details fetched from the Open Food Facts API.

2. Ask the Chatbot: Type your queries about food regulations, processing, or certifications.

3. Explore Recipes: Go to the "Recipe Corner." Enter the ingredients you have, and discover recipes you can make.


