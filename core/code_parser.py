import ast
import os


class CodeParser:
    """Extracts functions, classes, and imports from multiple Python files in a project."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.file_data = {}  # Stores parsed data for each file
        self.dependency_map = {}  # Tracks which files import which modules
        self.definitions = {}  # Maps function/class names to file paths
        self.module_map = {}  # Maps module names to file paths
        self.usage_map = {}  # Tracks function/class usage in files
        self.variable_map = {}  # Maps variable names to their assigned classes/modules

    def parse_file(self, file_path):
        """Parses a single Python file and extracts elements."""
        file_data = {"Classes": [], "Functions": [], "Imports": [], "depends_on": [], "used_by": [], "calls": {}}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)

            module_path = os.path.relpath(file_path, self.project_root).replace("\\", "/")
            module_name = module_path.replace("/", ".").rstrip(".py")  # Convert to module format

            self.module_map[module_name] = module_path  # Track module → file path mapping
            self.variable_map[module_path] = {}  # Initialize variable map for this file

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    file_data["Classes"].append(node.name)
                    self.definitions[f"{module_name}.{node.name}"] = module_path  # Track class location
                elif isinstance(node, ast.FunctionDef):
                    file_data["Functions"].append(node.name)
                    self.definitions[f"{module_name}.{node.name}"] = module_path  # Track function location
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        file_data["Imports"].append(alias.name)  # Store imports
                elif isinstance(node, ast.ImportFrom):
                    self.track_imports(node, module_path, file_data)
                elif isinstance(node, ast.Assign):
                    self.resolve_variable_assignment(node, module_path)  # Track variable-class assignment
                elif isinstance(node, ast.Call):
                    self.track_function_call(node, module_path, file_data)

        except Exception as e:
            return f"Error parsing {file_path}: {e}"

        return file_data

    def track_imports(self, node, module_path, file_data):
        """Tracks imports like `from core.zip_handler import ZipHandler`."""
        if node.module:
            imported_module = node.module
            for alias in node.names:
                imported_name = alias.name  # Class or function name
                full_import = f"{imported_module}.{imported_name}"
                file_data["Imports"].append(full_import)
                self.variable_map[module_path][imported_name] = full_import  # Store imported name reference

    def resolve_variable_assignment(self, node, module_path):
        """Tracks variable assignments to class instantiations or imported classes."""
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            class_name = node.value.func.id  # Extract class name
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_name = target.id  # Extract variable name
                    # Resolve if class_name is imported
                    resolved_class = self.variable_map[module_path].get(class_name, class_name)
                    self.variable_map[module_path][variable_name] = resolved_class  # Map variable to class

    def track_function_call(self, node, module_path, file_data):
        """Tracks function calls and resolves them to their class/module if applicable."""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr  # Extract function name
            base = node.func.value.id if isinstance(node.func.value, ast.Name) else None

            if base and base in self.variable_map[module_path]:
                resolved_class = self.variable_map[module_path][base]
                full_call = f"{resolved_class}.{func_name}"  # Map to class.method
                file_data["calls"].setdefault(module_path, set()).add(full_call)

    def scan_project(self):
        """Scans all Python files in the project and builds dependency maps."""
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.project_root).replace("\\", "/")  # Normalize paths

                    self.file_data[relative_path] = self.parse_file(full_path)

        # Build dependency map by resolving imports
        for file, data in self.file_data.items():
            depends_on = set()
            external_imports = []

            for imp in data["Imports"]:
                source_file = self.resolve_import_dependency(imp)

                if source_file:
                    depends_on.add(source_file)
                else:
                    external_imports.append(imp)  # If it doesn't exist in the project, mark as external

            self.file_data[file]["depends_on"] = list(depends_on)
            self.file_data[file]["Imports"] = external_imports  # Only store external imports
            self.dependency_map[file] = list(depends_on)  # Store resolved dependencies

    def resolve_import_dependency(self, imp):
        """Resolves an import to a file inside the project, or marks it as an external import."""
        if imp in self.module_map:
            return self.module_map[imp]  # Found a direct match
        else:
            module_base = ".".join(imp.split(".")[:-1])
            return self.module_map.get(module_base)

    def get_summary(self):
        """Returns the parsed data, dependency map, and function usage details."""
        return {
            "files": self.file_data,
            "dependencies": self.dependency_map,
            "usage_map": self.usage_map,
        }
