import streamlit as st
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import requests
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import plotly.express as px
import pandas as pd


st.set_page_config(page_title="Nutrify", layout="wide")

st.markdown(
    """
    <style>
    .reportview-container {
        background-image: url("https://your-image-url-here.com/background.jpg");
        background-size: cover;
        background-position: center;
        height: 100vh;
    }
    .sidebar .sidebar-content {
        background-color: rgba(255, 255, 255, 0.8);
    }
    </style>
    """,
    unsafe_allow_html=True
)

#image preprocessing
def preprocess_image(image):
    """Preprocess the image for better barcode detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  
    edged = cv2.Canny(blurred, 50, 200)  
    return edged

#barcode detection
def detect_barcode_pyzbar(image):
    """Detect barcode using pyzbar."""
    decoded_objects = decode(image)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    return None

#barcode detection using opencv
def detect_barcode_opencv(image):
    """Detect barcode using OpenCV QRCodeDetector."""
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(image)
    if data:
        return data
    return None

#for image of product
def get_product_image(barcode):
    url = f'https://world.openfoodfacts.org/product/{barcode}'  
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tag = soup.find('img', {'class': 'product_image'})
    
    if img_tag:
        return img_tag['src']
    else:
        return None

#data fetching
def fetch_food_data(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to fetch data from Open Food Facts API."}
    data = response.json()
    if "product" in data and data["product"]:
        product = data["product"]
        nutrition = product.get("nutriments", {})
        allergens = product.get("allergens", "No allergens listed.")
        ingredients = product.get("ingredients_text", "No ingredients found.")
        additives=product.get("additives_tags","No additives added")
        categories=product.get("categories")
        quantity = product.get("quantity", "Not available")
        packaging = product.get("packaging", "Not available")
        labels = product.get("labels", "No labels available")
        nutriscore = product.get("nutriscore_grade", "Not available")
        ecoscore = product.get("ecoscore_score", "Not available")
        additives = product.get("additives", "No additives listed")
        carbon_footprint = product.get("carbon_footprint", "Not available")
        packaging_materials = product.get("packaging_materials", "Packaging materials not available")
        threatened_species = product.get("threatened_species", "No threatened species information")

        nutritional_info = {
            "🔥energy_kcal": nutrition.get("energy-kcal", "Not available"),
            "🧈fat(%)": nutrition.get("fat", "Not available"),
            "🍳saturated_fat(%)": nutrition.get("saturated-fat", "Not available"),
            "🥔carbohydrates": nutrition.get("carbohydrates", "Not available"),
            "🍭sugars(%)": nutrition.get("sugars", "Not available"),
            "🥦fiber": nutrition.get("fiber", "Not available"),
            "🥩proteins": nutrition.get("proteins", "Not available"),
            "🧂salt": nutrition.get("salt", "Not available"),
        }

        return {
            "nutritional_info": nutritional_info,
            "allergens": allergens,
            "ingredients": ingredients,
            "additives": additives,
            "categories":categories,
            "quantity":quantity,
            "packaging":packaging,
            "quantity": quantity,
            "packaging": packaging,
            "labels": labels,
            "nutriscore": nutriscore,
            "ecoscore": ecoscore,
            "additives": additives,
            "ingredients": ingredients,
            "carbon_footprint": carbon_footprint,
            "packaging_materials": packaging_materials,
            "threatened_species": threatened_species
        }
    
    return {"error": "Product not found or missing data."}

#graoh plotting
def make_graph(ing):
    df_nutrients = pd.DataFrame([
        {"Nutrient": key, "Amount (g)": value} 
        for key, value in ing.items() if value != "Not available" and key != "🔥energy_kcal"
    ])
    fig = px.pie(df_nutrients, names='Nutrient', values='Amount (g)', title='Nutritional Breakdown')
    st.plotly_chart(fig)
    st.write("This pie chart represents the nutritional breakdown of the food product.")

#carbon footprint
def get_carbon_footprint_from_web(barcode):
    url = f"https://world.openfoodfacts.org/product/{barcode}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    carbon_footprint = soup.find('span', string=lambda text: text and 'CO₂e' in text)

    if carbon_footprint:
        return carbon_footprint.get_text(strip=True)
    else:
        return "Carbon footprint not found on the page."

#additives
def extract_additives_info(barcode):
    url = f"https://world.openfoodfacts.org/product/{barcode}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    additives_section = soup.find('div', id='panel_additives')
    additives = additives_section.find_all('ul', class_='panel_accordion accordion')
    additives_info = {}
    
    for additive in additives:
        name_tag = additive.find('h4', style="font-size:1.1rem;")
        if name_tag:
            additive_name = name_tag.get_text().strip()  
            if additive_name.startswith('E'):  
                description_tag = additive.find_next('div', class_='panel_text')
                description = description_tag.get_text().strip() if description_tag else "No description available."
                additives_info[additive_name] = description

    return additives_info

#threatened species
def extract_threatened_species_info(barcode):
    url = f"https://world.openfoodfacts.org/product/{barcode}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    species_section = soup.find('h3', class_='panel_title_card', text='Threatened species')
    
    if not species_section:
        return {}
    
    species_panels = species_section.find_all_next('ul', class_='panel_accordion accordion')
    species_info = {}
    
    for panel in species_panels:
        species_name_tag = panel.find('h4', class_='evaluation_bad_title')
        description_tag = panel.find('span')
        panel_text_tag = panel.find('div', class_='panel_text')
        
        if species_name_tag and description_tag and panel_text_tag:
            species_name = species_name_tag.get_text(strip=True) 
            description = description_tag.get_text(strip=True) 
            detailed_description = panel_text_tag.get_text(strip=True)  
            
            species_info[species_name] = {
                'description': description,
                'detailed_description': detailed_description
            }
    
    return species_info


def check_fda_compliance(ingredients_list):

    fda_compliance_report = []
    
    for ingredient in ingredients_list:
        url = f"https://api.fda.gov/drug/label.json?search=active_ingredient:{ingredient}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                fda_compliance_report.append(f"{ingredient}: FDA approved.")
            else:
                fda_compliance_report.append(f"{ingredient}: Not found in FDA approved list.")
        else:
            fda_compliance_report.append(f"{ingredient}: Not found in FDA approved list.")
    
    return fda_compliance_report

def fetch_recipes(ingredients):
    api_key = 'b53a02ed9db94acda77b886384d1b261' 
    url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=5&apiKey={api_key}'
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch recipes. Please try again.")
        return []

# Sidebar navigation
st.sidebar.title("Nutrify Navigation")
page = st.sidebar.radio("Go to", ["Home", "Barcode Scanner","Recipe Corner","Chatbot"])

if page == "Home":
    st.title("Welcome to Nutrify!🔍")
    st.markdown(
        """
        Scan, discover, and empower your food choices in just a tap! 
        Explore ingredients, nutritional values, and certifications of your favorite foods. 
        Ready to make smarter, healthier choices? Start scanning now!
        """
    )

elif page == "Barcode Scanner":
    st.header("📲 Barcode Scanner or Manual Input")
    st.write("Choose an option below to provide a barcode:")
    input_method = st.radio("Select input method:", ["Scan Barcode", "Enter Barcode Manually"])
    barcode_data = None

    if input_method == "Scan Barcode":
        st.write("Capture an image to scan the barcode.")
        img_file = st.camera_input("Take a picture to scan the barcode")

        if img_file:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            st.image(img, caption="Captured Image", use_column_width=True)
            preprocessed_image = preprocess_image(img)
            barcode_data = detect_barcode_pyzbar(preprocessed_image)
            if not barcode_data:
                barcode_data = detect_barcode_opencv(img)
            if not barcode_data:
                st.warning("No barcode detected. Please ensure the barcode is visible and clear.")

    elif input_method == "Enter Barcode Manually":
        barcode_data = st.text_input("Enter the barcode number:")

    if barcode_data:
        st.success(f"Barcode Detected: {barcode_data}")

        food_data = fetch_food_data(barcode_data)
        if "error" in food_data:
            st.error(food_data["error"])
        else:
            product_image_url = get_product_image(barcode_data)
            if product_image_url:
                st.image(product_image_url, caption=f"Product Image for Barcode: {barcode_data}", width=332)
            else:
                st.write("Product image not found for this barcode.")
            st.title("🍽 Nutritional Information:")
            for key, value in food_data["nutritional_info"].items():
                st.write(f"{key.replace('_', ' ').capitalize()}: {value}")
            make_graph(food_data["nutritional_info"])
            st.title("⚖️ Quantity:")
            st.write(food_data["quantity"])
            st.title("📂 Categories:")
            st.write(food_data["categories"])
            st.title("🧪 Ingredients:")
            st.write(food_data["ingredients"])
            st.title("⚠️ Allergens:")
            st.write(food_data["allergens"])
            additives_info = extract_additives_info(barcode_data)
            st.subheader("⚗️ Additives:")
            for additive_name, description in additives_info.items():
                st.header(additive_name)
                st.write(description)
            if food_data["ingredients"]:
                fda_compliance_report = check_fda_compliance(food_data["ingredients"].split(","))
                st.title("FDA Compliance: ")
                for report in fda_compliance_report:
                    st.write(report)
            else:
                st.warning("No ingredients data found to check for FDA compliance.")
            st.title("📦 Packaging:")
            st.write(food_data["packaging"])
            st.title("🏷️ Labels:")
            st.write(food_data["labels"])
            st.title("🟢 Nutri-score:")
            st.write("The Nutri-Score is an overview of nutritional quality of products. The score from A to E is calculated based on nutrients and foods to favor (proteins, fiber, fruits, vegetables and legumes ...) and nutrients to limit (calories, saturated fat, sugars, salt).")
            st.subheader(food_data["nutriscore"])
            st.title("🌍 Eco-score:")
            st.write("The Eco-Score is an experimental score that summarizes the environmental impacts of food products. The Eco-Score formula is subject to change as it is regularly improved to make it more precise and better suited to each country. Its scored out of 100.")
            st.subheader(food_data["ecoscore"])
            carbon_footprint = get_carbon_footprint_from_web(barcode_data)
            st.title("🌱 Carbon Footprint:")
            st.write(carbon_footprint)
            species_info = extract_threatened_species_info(barcode_data)
            st.title('🐾Threatened Species Information')
            for species, info in species_info.items():
                st.subheader(species)
                st.write(info['description']) 
                st.write(info['detailed_description'])  


elif page == "Recipe Corner":
    st.title('Recipe Corner')
    st.write("Enter the ingredients you have, separated by commas, and find recipes you can make!")
    ingredients = st.text_input("Enter ingredients:")
    if st.button('Find Recipes'):
        if ingredients:
            recipes = fetch_recipes(ingredients)
        
            if recipes:
                st.subheader("Recipes you can make:")
                for recipe in recipes:
                    st.markdown(f"*{recipe['title']}*")
                    st.image(recipe['image'], width=332)
                    st.write("*Ingredients used:*")
                    st.write(", ".join([ingredient['name'] for ingredient in recipe['usedIngredients']]))
                    st.markdown(f"[View full recipe](https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']})")
                    st.write("\n")
            else:
                st.write("No recipes found. Try different ingredients.")
        else:
            st.warning("Please enter some ingredients.")

elif page == "Chatbot":
    st.title("Foodie🤖")
    st.markdown("Meet Foodie! Ask any food-related question, and our Foodie will assist you.")
    chatbot_url = "https://cdn.botpress.cloud/webchat/v2.2/shareable.html?configUrl=https://files.bpcontent.cloud/2024/12/07/18/20241207185412-QBTY0H6R.json"
    components.iframe(chatbot_url, width=800, height=600)