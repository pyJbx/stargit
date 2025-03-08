import os


def fire():
    """Main entry point to start the UI."""
    print("🚀 Starting CodeScope UI...")
    os.system("streamlit run ui/app.py")  # Runs Streamlit UI from the root directory


if __name__ == "__main__":
    fire()
