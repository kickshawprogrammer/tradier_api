import os
from ruamel.yaml import YAML

# Directories to process
SOURCE_DIRS = {
    "Tradier_api": "tradier_api",
    "Examples": "examples",
    "Tests": "tests",
}

# Docs output directory
DOCS_OUTPUT_DIR = "docs/source_code"

# MkDocs YAML file path
MKDOCS_YML_PATH = "mkdocs.yml"

def generate_markdown_files():
    """
    Generate Markdown files for source files in specified directories.
    """
    nav_structure = []
    for section, directory in SOURCE_DIRS.items():
        section_nav = {section: []}

        # Create a subdirectory for each section in the docs output
        section_output_dir = os.path.join(DOCS_OUTPUT_DIR, directory)
        os.makedirs(section_output_dir, exist_ok=True)

        for file_name in sorted(os.listdir(directory)):
            if file_name.endswith(".py") and file_name != "__init__.py":
                base_name = os.path.splitext(file_name)[0]
                src_path = os.path.join(directory, file_name)

                # Create Markdown file in the respective subdirectory
                md_file_path = os.path.join(section_output_dir, f"{base_name}.md")
                with open(md_file_path, "w") as md_file:
                    md_file.write(f"# {base_name}\n\n")
                    md_file.write(f"```python\n--8<-- \"{src_path}\"\n```\n")

                # Add entry to the navigation structure under the section
                section_nav[section].append({file_name: f"source_code/{directory}/{base_name}.md"})

        nav_structure.append(section_nav)

    return nav_structure


def update_mkdocs_yml(nav_structure):
    """
    Update the `mkdocs.yml` file to include the generated navigation structure.
    """
    yaml = YAML()
    yaml.preserve_quotes = True  # Preserve formatting in mkdocs.yml

    with open(MKDOCS_YML_PATH, "r") as f:
        mkdocs_config = yaml.load(f)

    # Ensure the navigation section exists
    if "nav" not in mkdocs_config:
        mkdocs_config["nav"] = []

    # Remove existing "Source Code" section
    mkdocs_config["nav"] = [item for item in mkdocs_config["nav"] if "Source Code" not in item]

    # Add the new "Source Code" section with nested structure
    mkdocs_config["nav"].append({"Source Code": nav_structure})

    # Write updated mkdocs.yml
    with open(MKDOCS_YML_PATH, "w") as f:
        yaml.dump(mkdocs_config, f)


if __name__ == "__main__":
    # Generate Markdown files and collect the navigation structure
    nav_structure = generate_markdown_files()

    # Update the mkdocs.yml file
    update_mkdocs_yml(nav_structure)

    print("Markdown files and navigation updated successfully.")
