import os
import xml.etree.ElementTree as ET
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_DIR = os.path.join(BASE_DIR, 'assets')
OUTPUT_DIR = os.path.join(BASE_DIR)
QRC_FILE = 'resources.qrc'
PY_OUTPUT_FILE = 'resources_rc.py'

def scan_assets(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            # Convert to relative path from the base resource directory
            relative_path = os.path.relpath(full_path, start=directory)
            # Ensure paths use the correct format (forward slashes for compatibility)
            files.append(relative_path.replace("\\", "/"))
    return files

def generate_qrc(resource_dir=RESOURCE_DIR, output_dir=OUTPUT_DIR, qrc_file=QRC_FILE, py_output_file=PY_OUTPUT_FILE):
    output_dir = os.path.abspath(output_dir)
    output_file = os.path.join(output_dir, qrc_file)
    resource_dir = os.path.abspath(resource_dir)

    if not os.path.exists(resource_dir):
        print(f"[!] Error: Resource directory {resource_dir} does not exist.")
        return

    # Create the root element of the QRC file
    qresource = ET.Element("qresource", prefix="/")
    for file in scan_assets(resource_dir):
        # Prepend the "assets/" directory using forward slashes only
        file_with_assets = "assets/" + file.lstrip("/")
        ET.SubElement(qresource, "file").text = file_with_assets

    rcc = ET.Element("RCC")
    rcc.append(qresource)

    tree = ET.ElementTree(rcc)
    # Create the output directory if needed
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

    if not os.path.exists(output_file):
        print(f"[!] Error: {output_file} was not created.")
        return

    print(f"[+] Generated {output_file}")

def compile_qrc(output_dir=OUTPUT_DIR, qrc_file=QRC_FILE, py_output_file=PY_OUTPUT_FILE):
    try:
        output_file = os.path.join(output_dir, py_output_file)
        qrc_file = os.path.join(output_dir, qrc_file)
        # Call pyside6-rcc to compile the QRC into Python code
        subprocess.run(["pyside6-rcc", qrc_file, "-o", output_file], check=True)
        print(f"[+] Compiled {qrc_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error compiling resource file: {e}")
    except FileNotFoundError:
        print("[!] Error: pyside6-rcc command not found. Please ensure it is installed and available in your PATH.")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

def build_resources(resource_dir=RESOURCE_DIR, output_dir=OUTPUT_DIR, qrc_file=QRC_FILE, py_output_file=PY_OUTPUT_FILE) -> str:
    """
    Build the resources for the application and return the importable Python module path.
    :param resource_dir: Directory containing the resources to be compiled.
    :param output_dir: Directory where the compiled resources will be saved.
    :param qrc_file: Name of the QRC file to be generated.
    :param py_output_file: Name of the output Python file.
    :return: Python import path to the compiled resource module (e.g., 'resources_rc')
    """
    print("[+] Building resources...")
    generate_qrc(resource_dir, output_dir, qrc_file, py_output_file)
    compile_qrc(output_dir, qrc_file, py_output_file)

    # Derive importable module path from output_dir and py_output_file


    return 'resources_rc'
