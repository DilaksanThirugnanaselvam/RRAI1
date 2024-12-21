import openai
import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# Set up your OpenAI API key
openai.api_key = ""

# Custom CSS for color matching and improved appearance
st.markdown("""
    <style>
        .main {
            background-color: #FEE6E7;
        }
        .stTextArea label {
            font-family: 'Arial', sans-serif;
            color: #E94F52;
            font-size: 20px;
        }
        .stButton button {
            background-color: #E94F52;
            color: white;
            border: 2px solid #E94F52;
            font-size: 18px;
            font-family: 'Arial', sans-serif;
            padding: 10px 20px;
            border-radius: 10px;
        }
        .stTextArea textarea {
            background-color: #FFF9F9;
            color: #333;
            font-family: 'Arial', sans-serif;
            font-size: 18px;
        }
        .stMarkdown h1 {
            color: #E94F52;
            font-family: 'Arial', sans-serif;
            font-size: 36px;
        }
        .generated-text {
            font-family: 'Arial', sans-serif;
            font-size: 16px;
            color: #333;
            line-height: 1.5;
            padding: 15px;
            border-radius: 10px;
            background-color: #FFF9F9;
            border: 1px solid #E94F52;
            margin-top: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .highlight {
            color: #E94F52;
            font-weight: bold;
        }
        .important {
            font-size: 18px;
            font-weight: bold;
            color: #E94F52;
        }
    </style>
""", unsafe_allow_html=True)

# Function to generate a recipe using GPT-4
def generate_recipe_with_gpt4(ingredients_list, max_tokens=1000):
    if not ingredients_list:
        return "No ingredients provided. Please provide a list of ingredients."

    prompt = (f"Create a detailed and delicious recipe using the following ingredients: "
              f"{', '.join(ingredients_list)}. Include estimated times for preparation and cooking. "
              "Please add emojis to the recipe steps.")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"An error occurred: {e}"

# Function to generate a related recipe image using DALL·E
def generate_recipe_image(ingredients_list):
    prompt = f"A beautifully plated dish using the following ingredients: {', '.join(ingredients_list)}. Capture the essence of these ingredients in a vibrant, colorful dish."

    try:
        image_response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return image_response['data'][0]['url']
    except Exception as e:
        return f"An error occurred while generating the image: {e}"

# Streamlit app with Recipe Rendezvous Theme
def main():
    st.markdown("<h1 style='text-align: center; color: #E94F52;'>🍽️ Recipe Rendezvous: Generating AI🤖 Powered Recipes 🍲</h1>", unsafe_allow_html=True)

    # List of over 1000 common ingredients, including Singapore-specific ones
    common_ingredients = list({
    # Vegetables & Greens
    "Bok Choy 🥬", "Kang Kong 🌿", "Choy Sum 🥦", "Chinese Cabbage 🥬", "Long Beans 🌱",
    "Eggplant 🍆", "Bitter Gourd 🍈", "Bean Sprouts 🌱", "Water Chestnuts 🥔", "Taro Root 🍠",
    "Lady’s Finger (Okra) 🌿", "Cabbage 🥬", "Kale 🌿", "Spinach 🌿", "Mustard Greens 🥬",

    # Meat & Poultry
    "Chicken 🍗", "Beef 🥩", "Pork 🥓", "Duck 🦆", "Lamb 🍖", "Frog Legs 🐸", "Quail Eggs 🥚",

    # Seafood
    "Prawns 🍤", "Squid 🦑", "Fish Fillets 🐟", "Crab 🦀", "Clams 🦪", "Mussels 🦪",
    "Scallops 🍥", "Dried Shrimp 🍤", "Anchovies 🐟", "Oysters 🦪", "Salmon 🐟",
    "Tuna 🐟", "Barramundi 🐟", "Cod 🐟", "Seabass 🐟",

    # Singaporean Ingredients
    "Curry Leaves 🌿", "Kaffir Lime Leaves 🍃", "Lemongrass 🌾", "Galangal 🌾", "Turmeric 🌾",
    "Star Anise ✨", "Cinnamon Stick 🧂", "Soy Sauce 🍶", "Dark Soy Sauce 🍶", "Fish Sauce 🐟",
    "Oyster Sauce 🦪", "Shrimp Paste 🍤", "Sambal 🌶️", "Gochujang 🌶️", "Chili Sauce 🌶️",
    "Hoisin Sauce 🍯", "Black Bean Paste 🍲", "Sesame Oil 🥜", "Peanut Oil 🥜", "Coconut Oil 🥥",
    "Palm Oil 🥥", "Lard 🥓", "Ghee 🧈", "Clarified Butter 🧈", "Vegetable Oil 🥗",
    "Olive Oil 🫒", "Belacan 🍤", "Pandan Leaves 🍃", "Laksa Paste 🍜", "Gula Melaka 🍯",

    # Noodles & Rice
    "Jasmine Rice 🍚", "Basmati Rice 🍚", "Glutinous Rice 🍘", "Red Rice 🍚", "Rice Flour 🍚",
    "Rice Vermicelli 🍜", "Hokkien Noodles 🍜", "Kway Teow 🍜", "Laksa Noodles 🍜", "Mee Pok 🍜",
    "Mee Goreng 🍜", "Glass Noodles 🍜", "Wonton Noodles 🍜", "Bee Hoon 🍜",

    # Singaporean Dishes/Snacks
    "Satay 🍢", "Hainanese Chicken Rice 🍛", "Chili Crab 🦀", "Bak Kut Teh 🍲", "Roti Prata 🍞",
    "Nasi Lemak 🍚", "Char Kway Teow 🍜", "Mee Siam 🍜", "Hokkien Mee 🍜", "Lontong 🍲", "Laksa 🍜",

    # Fruits
    "Mango 🥭", "Pineapple 🍍", "Jackfruit 🍈", "Durian 🍈", "Lychee 🍒", "Rambutan 🍒",
    "Papaya 🍈", "Starfruit 🍏", "Guava 🍏", "Coconut 🥥", "Banana 🍌", "Dragonfruit 🍒",

    # Legumes & Beans
    "Green Beans 🌿", "Mung Beans 🌱", "Black-Eyed Peas 🌱", "Red Beans 🌱", "Kidney Beans 🌱",
    "Lentils 🌾", "Chickpeas 🌿", "Black Beans 🌱", "White Beans 🌱", "Yellow Split Peas 🌾",

    # Dairy & Eggs
    "Coconut Milk 🥥", "Evaporated Milk 🥛", "Condensed Milk 🥛", "Yakult 🥛", "Cream 🥛",
    "Butter 🧈", "Ghee 🧈", "Salted Duck Egg 🥚", "Century Egg 🥚", "Milk Powder 🥛",

    # Nuts & Seeds
    "Peanuts 🥜", "Cashews 🥜", "Almonds 🌰", "Sesame Seeds 🌰", "Sunflower Seeds 🌻",
    "Pumpkin Seeds 🎃", "Pine Nuts 🌲", "Coconut 🥥", "Palm Sugar 🍯", "Macadamia Nuts 🌰",

    # Herbs & Spices
    "Garlic 🧄", "Ginger 🌿", "Shallots 🧅", "Turmeric 🌾", "Peppercorns 🧂", "Coriander Seeds 🌱",
    "Cumin Seeds 🌱", "Fennel Seeds 🌱", "Cardamom Pods 🧂", "Bay Leaves 🍃", "Cloves 🌿",

    # Sauces & Condiments
    "Sweet Soy Sauce 🍶", "Chili Oil 🌶️", "Peanut Sauce 🥜", "Rojak Sauce 🍯", "Soybean Paste 🍲",
    "Fermented Black Beans 🌱", "Fermented Tofu 🥘", "Sambal Belacan 🌶️", "Tamarind Paste 🍬",
    "Chili Padi 🌶️", "Pickled Ginger 🌾", "Mustard Sauce 🧴", "Vinegar 🧴", "Ketchup 🍅",

    # Sweeteners & Flours
    "Coconut Sugar 🍯", "Honey 🍯", "Palm Sugar 🍯", "Brown Sugar 🍬", "Corn Flour 🌽",
    "Tapioca Flour 🍠", "Sweet Potato Flour 🍠", "All-Purpose Flour 🍞", "Rice Flour 🍚",
    "Sago Pearls 🍡", "Agar Agar 🍮", "Gelatin 🍮",

    # Miscellaneous
    "Kueh 🧁", "Cendol 🍧", "Red Bean Paste 🍘", "Sweet Corn 🌽", "Sago Pearls 🍡",
    "Durian Paste 🍬", "Coconut Shavings 🥥", "Rice Cake 🍘", "Fish Balls 🍥",

    # Drinks
    "Soy Milk 🥛", "Coconut Water 🥥", "Bandung 🥛", "Teh Tarik ☕", "Kopi ☕", "Lemongrass Tea 🍵",
    "Sugarcane Juice 🥤", "Grass Jelly Drink 🍵"


    })

    st.subheader("📝 Type your own ingredients :")

    # Create an input box for typing ingredients
    user_ingredients = st.text_input("Enter ingredients here(separated by commas) :")
    user_ingredients_list = [ingredient.strip() for ingredient in user_ingredients.split(',') if ingredient.strip()]

    st.subheader("🔍 Select your ingredients :")

    # Multiselect to choose ingredients from the pre-defined list
    selected_common_ingredients = st.multiselect(
        "Choose from common ingredients:",
        options=common_ingredients
    )

    # Generate recipe button
    if st.button("🍳 Generate Recipe"):
        if selected_common_ingredients or user_ingredients_list:
            # Combine selected common and user-inputted ingredients separately
            combined_ingredients = selected_common_ingredients + user_ingredients_list
            recipe = generate_recipe_with_gpt4(combined_ingredients)

            # Display Recipe with the title highlighted in red
            st.markdown(f"<div class='generated-text'><h4 style='color: red;'>Your Recipe 🍽️</h4><p>{recipe}</p></div>", unsafe_allow_html=True)

            # Automatically generate and display an image using DALL·E
            recipe_image_url = generate_recipe_image(combined_ingredients)
            if "An error occurred" not in recipe_image_url:
                response = requests.get(recipe_image_url)
                image = Image.open(BytesIO(response.content))
                st.image(image, caption="Your Recipe Image", use_column_width=True)
            else:
                st.error(recipe_image_url)

        else:
            st.warning("⚠️ Please select or type some ingredients.")

    # Footer
    st.markdown("<p style='text-align: center;'>Created with ❤️ by Team Recipe Rendezvous👨‍🍳</p>", unsafe_allow_html=True)

# Run the Streamlit app
if __name__ == "__main__":
    main()
