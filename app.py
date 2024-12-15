import streamlit as st
import requests
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import plotly.express as px
import pandas as pd
from pyzbar.pyzbar import decode
import io
from PIL import Image
from streamlit_lottie import st_lottie

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

def scan_barcode(image):

    # Convert the uploaded file to a PIL image
    image = Image.open(io.BytesIO(uploaded_file.read()))

    # Decode the barcode from the image
    barcodes = decode(image)
    
    if barcodes:
        # Get the first barcode found (you can handle multiple barcodes if needed)
        barcode = barcodes[0]
        barcode_data = barcode.data.decode("utf-8")
        return barcode_data
    else:
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

import time

def load_lottie_home():
    try:
        response = requests.get("https://lottie.host/77c24cda-e336-4742-9cb9-f9a93be2c91c/4QyzvtBBPF.json")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Lottie animation: {e}")
        return {}
    
def load_lottie_recipe():
    try:
        response = requests.get("https://lottie.host/2a062245-f319-47e0-ba31-8414958f75a2/hSK03Wn6zG.json")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Lottie animation: {e}")
        return {}
    
def load_lottie_chat():
    try:
        response = requests.get("https://lottie.host/e34f7175-62eb-4711-8cdb-e2488465bf4e/Mxd3917aPS.json")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Lottie animation: {e}")
        return {}

def show_homepage_with_loading():
    lottie_animation = load_lottie_home()
    if lottie_animation:
        with st.empty():  # Create an empty container for the animation
            st_lottie(lottie_animation, height=200, key="loading-animation")
        
        # Wait for 4 seconds and then clear the animation
        time.sleep(4)
        st.empty()  # Completely remove the animation from the UI

def show_recipepage_with_loading():
    lottie_animation = load_lottie_recipe()
    if lottie_animation:
        with st.empty():  # Create an empty container for the animation
            st_lottie(lottie_animation, height=200, key="loading-animation")
        
        # Wait for 4 seconds and then clear the animation
        time.sleep(4)
        st.empty()  # Completely remove the animation from the UI

def show_chat_with_loading():
    lottie_animation = load_lottie_chat()
    if lottie_animation:
        with st.empty():  # Create an empty container for the animation
            st_lottie(lottie_animation, height=200, key="loading-animation")
        
        # Wait for 4 seconds and then clear the animation
        time.sleep(4)
        st.empty()  # Completely remove the animation from the UI

# Sidebar navigation
st.sidebar.title("Nutrify Navigation")
page = st.sidebar.radio("Go to", ["Home", "Barcode Scanner","Recipe Corner","Chatbot"])

if page == "Home":
    show_homepage_with_loading()
    st.title("Welcome to Nutrify!🔍")
    st.markdown("""
**Unlock the Secrets of Your Food, One Scan at a Time!** 📲✨  

*Ever wondered what’s REALLY in your food?* 
With *Nutrify*, you’re not just eating—you’re **empowered**!  

Here’s how we make food smarter:  
- 🥗 **Decode Ingredients**: Know exactly what’s inside your food  
- ⚠️ **Watch Out for Allergens & Additives**: Stay safe, stay informed!
- ✅ **FDA Compliance**: Trust that your food meets the highest standards  
- 📊 **NutriScore & EcoScore**: Healthier choices, eco-friendly impact! 
- 🌍 **Carbon Footprint Insights**: Make the planet-friendly choice  
- 🐾 **Ethical Eating**: Learn about threatened species and ethical sourcing  

🚀 **Need more info? Meet Foodie🤖!**  
Instantly get answers to all your burning questions about food, regulations, certifications, and more! Your personal food guide, always at your fingertips.  

🍝😋 **Hungry for Inspiration?**  
Check out our **Recipe Corner** to create delicious meals from the ingredients you already have! 🍳✨  

**Scan, Chat, Learn, and Eat Smarter!**  
With *Nutrify*, you're in control of what you eat—and the world you’re helping to create. 🌎💚  
"""
    )
     st.image(r'./assets/IMG.jpeg', use_container_width=True)



elif page == "Barcode Scanner":
    # Page Header with Style
    st.title('Barcode Scanner')
    st.markdown(
        """
**📲 Scan, Learn, Decide! 🍴**   

*Nutrify’s **Barcode Scanner** is here to make your food choices smarter, healthier, and more informed.✨\n Just a quick scan, and you'll unlock a world of information waiting to guide your next meal or grocery run. 😍📦*  

- 🔍 **Quick Scan, Instant Insights:** Know what’s on your plate—trace the journey from farm to fork!
- 🌱 **Stay Informed:** In seconds, we’ll transform your ingredients into a variety of mouth-watering recipes, tailored just for you.
- 🛒 **Shop Smarter:** Choose products that align with your health goals and dietary needs.

💡 **Pro Tip:** For best results, ensure the barcode is well-lit and free from any obstructions or damage.

""",
        unsafe_allow_html=True
    )

    st.write("## Select an Input Method")
    input_method = st.radio("How would you like to provide a barcode?", ["Scan Barcode", "Enter Barcode Manually"])
    barcode_data = None

    # Input Methods
    if input_method == "Scan Barcode":
        uploaded_file = st.file_uploader("Upload a barcode image", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            with st.spinner("Scanning barcode..."):
                barcode_data = scan_barcode(uploaded_file)
            if barcode_data:
                st.success(f"Barcode Detected: {barcode_data}")
            else:
                st.error("No barcode found in the image. Please try again.")
    elif input_method == "Enter Barcode Manually":
        barcode_data = st.text_input("Enter the barcode number:")
        if barcode_data:
            st.success(f"Barcode Detected: {barcode_data}")

    # Process and Display Food Data
    if barcode_data:
        st.markdown("---")
        st.write("## Fetching Data...")
        food_data = fetch_food_data(barcode_data)
        if "error" in food_data:
            st.error(food_data["error"])
        else:
            # Display Product Image
            product_image_url = get_product_image(barcode_data)
            if product_image_url:
                st.image(product_image_url, caption=f"Product Image for Barcode: {barcode_data}", width=332)
            else:
                st.warning("No product image found for this barcode.")

            # Nutritional Information with Progress Bars
            st.write("## 🍽 Nutritional Information")
            for key, value in food_data["nutritional_info"].items():\
                st.write(f"{key.replace('_', ' ').capitalize()}: {value}")

            # Generate Graph for Nutritional Data
            make_graph(food_data["nutritional_info"])

            # Other Food Information Sections
            st.write("## ⚖️ Quantity")
            st.info(food_data["quantity"])
            st.write("## 📂 Categories")
            st.write(food_data["categories"])
            st.write("## 🧪 Ingredients")
            st.write(food_data["ingredients"])
            st.write("## ⚠️ Allergens")
            st.write(food_data["allergens"])

            # Additives Information
            additives_info = extract_additives_info(barcode_data)
            st.write("## ⚗️ Additives")
            for additive_name, description in additives_info.items():
                st.markdown(f"**{additive_name}:** {description}")

            # FDA Compliance Check
            if food_data["ingredients"]:
                st.write("## 🏛 FDA Compliance")
                fda_compliance_report = check_fda_compliance(food_data["ingredients"].split(","))
                for report in fda_compliance_report:
                    st.success(report)
            else:
                st.warning("No ingredients data found to check for FDA compliance.")

            # Packaging and Labels
            st.write("## 📦 Packaging")
            st.write(food_data["packaging"])
            st.write("## 🏷️ Labels")
            st.write(food_data["labels"])

            # Nutri-score and Eco-score
            st.write("## 🟢 Nutri-score")
            st.info(food_data["nutriscore"])
            st.write("## 🌍 Eco-score")
            st.info(food_data["ecoscore"])

            # Carbon Footprint Information
            carbon_footprint = get_carbon_footprint_from_web(barcode_data)
            st.write("## 🌱 Carbon Footprint")
            st.write(carbon_footprint)

            # Threatened Species Information
            species_info = extract_threatened_species_info(barcode_data)
            st.write("## 🐾 Threatened Species Information")
            for species, info in species_info.items():
                st.markdown(f"### {species}")
                st.write(info["description"])
                st.write(info["detailed_description"])


elif page == "Recipe Corner":
    show_recipepage_with_loading()
    st.title('Recipe Corner')
    st.markdown(
        """
**💡 Got Ingredients? We’ve Got Recipes! 💡**   

*Unleash your inner chef with **Recipe Corner**—your ultimate kitchen assistant.\n Whether you’ve got a handful of ingredients or a fridge full of mystery items, we’ll help you whip up something delicious in no time. 😋✨*  

- 🍅 **Add Your Ingredients:** Got tomatoes, eggs, or even a lonely potato? Just type in the ingredients you have, **separated by commas**, and we’ll do the rest.
- 🍽️ **Recipe Magic:** In seconds, we’ll transform your ingredients into a variety of mouth-watering recipes, tailored just for you.
""",
        unsafe_allow_html=True
    )
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
    show_chat_with_loading()
    st.title("Meet Foodie – Your Culinary Sidekick!🍽️🤖")
    st.markdown(
        """

*Say hello👋 to Foodie, your trusty AI kitchen companion! Whether you’re a food enthusiast or someone just trying to figure out what’s in your pantry, Foodie is here to make your life easier!🍏🍔🥑*  

- **🔍Ask About Ingredients:** Curious if a certain ingredient is healthy or how to use it in a dish? Just ask Foodie!
- **📜Food Regulations:** Get accurate info on food processing, packaging standards, and certifications.
- **💬 Food Facts:** Get interesting facts about the food you eat, from its origins to nutritional benefits.
""",
        unsafe_allow_html=True
    )
    chatbot_url = "https://cdn.botpress.cloud/webchat/v2.2/shareable.html?configUrl=https://files.bpcontent.cloud/2024/12/07/18/20241207185412-QBTY0H6R.json"
    components.iframe(chatbot_url, width=800, height=600)
