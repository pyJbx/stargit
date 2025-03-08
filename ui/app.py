import streamlit as st
import os

from core.zip_handler import ZipHandler

st.set_page_config(layout="wide")

# Ensure extraction directory exists
EXTRACTED_FOLDER = "extracted_files"
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)

# Initialize session state variables
if "file_list" not in st.session_state:
    st.session_state.file_list = []
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

st.title("✨ StarGit - Exploring Unexplored")

# Create Three Columns for Layout
col1, col2, col3 = st.columns([1.5, 3, 1.5])

with col1:
    st.subheader("📂 File Explorer")

    # Display extracted files
    if st.session_state.file_list:
        # Use radio button to select a file
        selected = st.radio(
            "Select a file:",
            st.session_state.file_list,
            index=st.session_state.file_list.index(st.session_state.selected_file)
            if st.session_state.selected_file in st.session_state.file_list else 0
        )
        # Update session state when user selects a file
        if selected != st.session_state.selected_file:
            st.session_state.selected_file = selected
            st.rerun()  # Refresh UI to reflect selection

    else:
        st.write("No files uploaded yet.")

    # --- File Upload Section ---
    st.markdown("---")  # Divider line
    st.subheader("📤 Upload Files Below")
    uploaded_file = st.file_uploader("Upload a ZIP file", type=["zip"])

    if uploaded_file:
        zip_files = ZipHandler(uploaded_file)
        zip_files.save_zip()
        zip_files.extract_zip()
        extracted_files = zip_files.get_files()

        if extracted_files:
            st.session_state.file_list = extracted_files  # Update file list
            st.session_state.selected_file = extracted_files[0]  # Select first file by default
            st.success(f"Extracted {len(extracted_files)} files.")
            st.rerun()  # Force UI refresh

with col2:
    st.subheader("📜 File Preview")
    if st.session_state.selected_file:
        try:
            with open(st.session_state.selected_file, "r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("File Content:", content, height=500, disabled=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

with col3:
    st.subheader("💬 Chat (Coming Soon)")
    st.text_area("Chat Here:", "Chat functionality will be added in future.", height=200, disabled=True)
