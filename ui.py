import streamlit as st
from config import GEMINI_MODEL, DEFAULT_REST_NAME, DEFAULT_ZIP
from helpers import get_lat_lon, search_restaurants, get_menu_photos, load_images_parallel
from analysis import analyze_image_text_only, render_dish_card
import PIL.Image

def render_analysis_workflow(selected_img, key_suffix):
    st.markdown("###  Selected Menu")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(selected_img, use_container_width=True)
        if st.button("Ask Chef", key=f"read_{key_suffix}", type="primary", use_container_width=True):
            with st.spinner("Chef is reading the menu..."):
                data = analyze_image_text_only(selected_img)
                if 'dishes' in data and data['dishes']:
                    st.session_state[f'dishes_{key_suffix}'] = data['dishes']
                    st.rerun()
                else:
                    st.error("No dishes found.")
    if f'dishes_{key_suffix}' in st.session_state:
        st.write("---")
        dishes = st.session_state[f'dishes_{key_suffix}']
        col_sel, col_vis = st.columns([1, 2])
        selected_indices = []
        with col_sel:
            st.subheader("📋 Select Dishes")
            with st.container(height=600):
                select_all = st.checkbox("Select All", value=False, key=f"all_{key_suffix}")
                for i, dish in enumerate(dishes):
                    if st.checkbox(f"{dish['name']}", key=f"chk_{key_suffix}_{i}", value=select_all):
                        selected_indices.append(i)
        with col_vis:
            st.subheader("🍽️ Visual Menu")
            visual_container = st.container(height=600)
        st.write("")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            visualize_clicked = st.button("Visualize Selected 🚀", key=f"vis_btn_{key_suffix}", type="primary", use_container_width=True)
        with visual_container:
            if visualize_clicked:
                if not selected_indices:
                    st.warning("Please select at least one dish.")
                else:
                    to_visualize = [dishes[i] for i in selected_indices]
                    prog_bar = st.progress(0)
                    for idx, dish in enumerate(to_visualize):
                        render_dish_card(dish)
                        prog_bar.progress((idx + 1) / len(to_visualize))
                    prog_bar.empty()
            else:
                st.info("👈 Select items on the left and click the button below to generate photos.")

def setup_ui():
    st.set_page_config(page_title="Menu Lens", page_icon="🍔", layout="wide")
    st.markdown("""
    <style>
        .dish-card { background-color: #262730; padding: 15px; border-radius: 10px; margin-bottom: 15px; display: flex; gap: 20px; align-items: start; }
        .dish-img { width: 256px; height: 256px; object-fit: cover; border-radius: 8px; flex-shrink: 0; }
        .dish-info { flex-grow: 1; }
        .tag { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 5px; margin-top: 5px; }
        .tag-meat { background-color: #FF4B4B; color: white; }
        .tag-allergen { background-color: #FFA500; color: black; }
        .tag-taste { background-color: #7D3C98; color: white; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1E1E1E; }
        ::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)
    st.title("🍔 Menu Lens")
    st.caption(f"AI-Powered Visual Menu Intelligence (Powered by {GEMINI_MODEL})")
