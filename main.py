import streamlit as st
from ui import setup_ui, render_analysis_workflow
from config import DEFAULT_REST_NAME, DEFAULT_ZIP
from helpers import get_lat_lon, search_restaurants, get_menu_photos, load_images_parallel
import PIL.Image

def main():
    setup_ui()
    tab1, tab2 = st.tabs(["📸 Manual Upload", "🔍 Search Google Maps"])
    with tab1:
        st.header("Upload Menu")
        up_file = st.file_uploader("Snap a photo", type=["jpg", "png", "jpeg"])
        if up_file:
            img = PIL.Image.open(up_file)
            render_analysis_workflow(img, "manual")
    with tab2:
        st.header("Find a Restaurant")
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                name_input = st.text_input("Restaurant Name", DEFAULT_REST_NAME, label_visibility="collapsed")
            with col2:
                zip_input = st.text_input("Zip", DEFAULT_ZIP, label_visibility="collapsed")
            with col3:
                radius = st.number_input("Miles", 1, 20, 5, label_visibility="collapsed")
            with col4:
                if st.button("🔍 Search", type="primary"):
                    with st.spinner("Searching..."):
                        coords = get_lat_lon(zip_input)
                        if coords:
                            found = search_restaurants(name_input, coords[0], coords[1], radius)
                            st.session_state['places'] = found if found else []
                            if not found: st.warning("No places found.")
                        else: st.error("Invalid Zip")
        if 'places' in st.session_state and st.session_state['places']:
            opts = {f"{p['title']} ({p['distance_miles']:.1f} mi)": p for p in st.session_state['places']}
            sel_key = st.selectbox("Select Location", list(opts.keys()), label_visibility="collapsed")
            if sel_key:
                place = opts[sel_key]
                st.session_state['selected_place'] = place
                if st.button(f"📸 Fetch Menu for {place['title']}"):
                    with st.spinner("Downloading full gallery (this may take 10s)..."):
                        raw_urls = get_menu_photos(place['search_id'])
                        if raw_urls:
                            loaded_imgs = load_images_parallel(raw_urls)
                            st.session_state['menu_images'] = loaded_imgs
                            st.session_state['selected_menu_idx'] = None
                            st.success(f"Ready! Loading menu pages!")
                        else:
                            st.error("No photos found. Please try the manual upload feature if you have a menu photo!")
        if 'menu_images' in st.session_state:
            st.write("---")
            st.subheader("Select one menu page to scan")
            images = st.session_state['menu_images']
            cols = st.columns(min(len(images), 6))
            for i, img in enumerate(images[:6]):
                with cols[i]:
                    st.image(img, use_container_width=True)
                    if st.button(f"Select", key=f"sel_btn_{i}", use_container_width=True):
                        st.session_state['selected_menu_idx'] = i
            if st.session_state.get('selected_menu_idx') is not None:
                idx = st.session_state['selected_menu_idx']
                selected_img = images[idx]
                st.divider()
                render_analysis_workflow(selected_img, "maps")

if __name__ == "__main__":
    main()
