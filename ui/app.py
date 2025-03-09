import streamlit as st
import os

from core.code_parser import CodeParser
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

if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = {"files": {}, "dependencies": {}}

if "project_root" not in st.session_state:
    st.session_state.project_root = None

st.title("✨ StarGit - Exploring Unexplored")

# Create Three Columns for Layout
col1, col2, col3 = st.columns([1.5, 3, 1.5])

with col1:
    st.subheader("📂 File Explorer")

    search_query = st.text_input("🔍 Search Files", "").strip().lower()

    # Filter files based on search query
    filtered_files = [
        file for file in st.session_state.file_list
        if search_query in os.path.basename(file).lower()
    ] if search_query else st.session_state.file_list

    # Display Matching Files
    if st.session_state.file_list:
        if filtered_files:
            selected = st.radio(
                "Select a file:",
                filtered_files,
                index=filtered_files.index(st.session_state.selected_file)
                if st.session_state.selected_file in filtered_files else 0
            )
            # Update session state when user selects a file
            if selected != st.session_state.selected_file:
                st.session_state.selected_file = selected
                st.rerun()  # Refresh UI to reflect selection
        else:
            st.warning("No matching files found.")
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
            project_root = os.path.dirname(extracted_files[0])
            st.session_state.project_root = project_root
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
    st.subheader("📌 Code Analysis")

    if st.session_state.selected_file and st.session_state.selected_file.endswith(".py"):
        # Check if project is already parsed
        if not st.session_state.parsed_data or not st.session_state.parsed_data["files"]:
            print("📂 Project Root:", st.session_state.project_root)
            if st.session_state.project_root:  # Ensure project root is valid
                parser = CodeParser(st.session_state.project_root)
                parser.scan_project()

                st.session_state.parsed_data = parser.get_summary()
                print("✅ Parsed Data in session state:", st.session_state.parsed_data)

                if "dependencies" not in st.session_state.parsed_data:
                    st.session_state.parsed_data["dependencies"] = {}
            else:
                st.warning("No project uploaded yet. Please upload a ZIP file.")

        selected_rel_path = os.path.relpath(st.session_state.selected_file, st.session_state.project_root)
        selected_rel_path = selected_rel_path.replace("\\", "/")  # Force uniform format

        print("🔍 Selected Rel Path:", selected_rel_path)
        print("📁 Available Keys in Parsed Data:", st.session_state.parsed_data["files"].keys())

        file_data = st.session_state.parsed_data["files"].get(selected_rel_path, {})
        dependencies = st.session_state.parsed_data["dependencies"].get(selected_rel_path, [])

        print("📌 Retrieved File Data:", file_data)
        print("🔗 Retrieved Dependencies:", dependencies)

        file_data = st.session_state.parsed_data["files"].get(selected_rel_path, {})
        dependencies = st.session_state.parsed_data["dependencies"].get(selected_rel_path, [])

        # Display extracted details
        if file_data.get("Classes"):
            st.write("### 📌 Classes")
            for cls in file_data["Classes"]:
                st.write(f"- `{cls}`")

        if file_data.get("Functions"):
            st.write("### 🔹 Functions")
            for func in file_data["Functions"]:
                st.write(f"- `{func}()`")

        if file_data.get("Imports"):
            st.write("### 📦 Imports")
            for imp in file_data["Imports"]:
                st.write(f"- `{imp}`")

        # Display Dependency Analysis
        if dependencies:
            st.write("### 🔗 Cross-File Dependencies")
            for dep in dependencies:
                st.write(f"- Imports from `{dep}`")

                # Show specific functions used from this file
                used_functions = st.session_state.parsed_data["usage_map"].get(dep, [])
                if used_functions:
                    st.write("  - Uses functions:")
                    for func in used_functions:
                        st.write(f"    - `{func}`")
    else:
        st.info("Select a Python file to analyze.")