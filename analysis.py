import os
import json
import PIL.Image
import requests
from io import BytesIO
from config import GEMINI_MODEL, tavily_client
from google import genai
import streamlit as st

def analyze_image_text_only(image_input):
    SYSTEM_PROMPT = """
    You are a culinary expert API. 
    Analyze the menu image provided. 
    Return ONLY a valid JSON object.
    The JSON must contain a key \"dishes\" which is a list of objects.
    Each object must have:
    - \"name\": Name of the dish
    - \"search_query\": A specific query to find a delicious photo of this dish
    - \"description\": A 1-sentence tasty description.
    - \"meat_type\": The main protein (e.g. \"Beef\", \"Chicken\", \"Pork\", \"Fish\", \"Veg\").
    - \"allergens\": List of allergens (e.g. [\"Dairy\", \"Nuts\"]).
    - \"keywords\": List of 3 taste keywords.
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    # model = genai.GenerativeModel(GEMINI_MODEL, api_key=os.getenv("GOOGLE_API_KEY"))
    try:
        if isinstance(image_input, PIL.Image.Image):
            img = image_input
        elif isinstance(image_input, str): 
            response = requests.get(image_input, timeout=10)
            img = PIL.Image.open(BytesIO(response.content))
        else:
            return {"dishes": []}
        img.thumbnail((800, 800))
        response = client.models.generate_content(model=GEMINI_MODEL, contents=[SYSTEM_PROMPT, img])
        # response = model.generate_content([SYSTEM_PROMPT, img])
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"Extraction Error: {e}")
        return {"dishes": []}

def get_dish_image(query):
    try:
        response = tavily_client.search(query=query, search_depth="basic", include_images=True, max_results=1)
        if 'images' in response and response['images']:
            return response['images'][0]
        return "https://via.placeholder.com/256?text=No+Image"
    except:
        return "https://via.placeholder.com/256?text=Error"

def render_dish_card(dish):
    image_url = get_dish_image(dish['search_query'])
    meat_html = f'<span class="tag tag-meat">{dish["meat_type"]}</span>'
    allergens_html = "".join([f'<span class="tag tag-allergen">⚠️ {a}</span>' for a in dish['allergens']])
    taste_html = "".join([f'<span class="tag tag-taste">{k}</span>' for k in dish['keywords']])
    if "via.placeholder.com" in image_url:
        source_link = ""
    else:
        source_link = f'<br><a href="{image_url}" target="_blank" style="font-size: 0.8em; color: #aaa; text-decoration: none;">🔗 Image Source</a>'
    st.markdown(f"""
    <div class="dish-card">
        <img src="{image_url}" class="dish-img" onerror="this.src='https://via.placeholder.com/256?text=Image+Error'">
        <div class="dish-info">
            <h3>{dish['name']}</h3>
            <p><i>{dish['description']}</i></p>
            <p>{meat_html} {allergens_html}</p>
            <p>{taste_html}</p>
            {source_link}
        </div>
    </div>
    """, unsafe_allow_html=True)
