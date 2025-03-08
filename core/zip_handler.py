import zipfile
import os


class ZipHandler:
    """Handles ZIP file extraction and management."""

    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.temp_dir = "extracted_files"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.zip_path = os.path.join(self.temp_dir, self.uploaded_file.name)
        self.extracted_files = []

    def save_zip(self):
        """Saves uploaded ZIP to a temporary directory."""
        try:
            with open(self.zip_path, "wb") as f:
                f.write(self.uploaded_file.getvalue())
        except Exception as e:
            raise RuntimeError(f"Error saving ZIP file: {e}")

    def extract_zip(self):
        """Extracts ZIP file and stores file paths."""
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                if not zip_ref.namelist():
                    raise ValueError("ZIP file is empty.")
                extract_path = os.path.join(self.temp_dir, self.uploaded_file.name.replace(".zip", ""))
                zip_ref.extractall(extract_path)

                self.extracted_files = [os.path.normpath(os.path.join(extract_path, f)) for f in zip_ref.namelist()]
        except zipfile.BadZipFile:
            raise ValueError("Invalid or corrupt ZIP file.")
        except Exception as e:
            raise RuntimeError(f"Error extracting ZIP file: {e}")

    def get_files(self):
        """Returns list of extracted files."""
        return self.extracted_files

    def read_file(self, file_path):
        """Reads the content of a selected file."""
        full_path = os.path.join(self.temp_dir, file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"
        return "File not found."


if __name__ == '__main__':
    pass
