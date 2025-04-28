import os
import xml.etree.ElementTree as ET
import subprocess

def scan_assets(directory: str):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, start=directory)
            files.append(relative_path.replace("\\", "/"))
    return files

def generate_qrc(resource_dir: str, qrc_output_path: str):
    if not os.path.exists(resource_dir):
        print(f"[!] Error: Resource directory {resource_dir} does not exist.")
        return

    qresource = ET.Element("qresource", prefix="/")
    for file in scan_assets(resource_dir):
        file_with_assets = "assets/" + file.lstrip("/")
        ET.SubElement(qresource, "file").text = file_with_assets

    rcc = ET.Element("RCC")
    rcc.append(qresource)

    os.makedirs(os.path.dirname(qrc_output_path), exist_ok=True)
    tree = ET.ElementTree(rcc)
    tree.write(qrc_output_path, encoding="utf-8", xml_declaration=True)

    if os.path.exists(qrc_output_path):
        print(f"[+] Generated {qrc_output_path}")
    else:
        print(f"[!] Error: {qrc_output_path} was not created.")

def compile_qrc(qrc_path: str, py_output_path: str):
    try:
        subprocess.run(["pyside6-rcc", qrc_path, "-o", py_output_path], check=True)
        print(f"[+] Compiled {qrc_path} -> {py_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error compiling resource file: {e}")
    except FileNotFoundError:
        print("[!] Error: pyside6-rcc not found. Ensure it's installed and in your PATH.")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

def build_resources(resource_dir: str, qrc_path: str, py_output_path: str) -> str:
    """
    Build resources for a PySide6 application.

    :param resource_dir: Path to the assets directory.
    :param qrc_path: Path to write the .qrc file.
    :param py_output_path: Path to write the .py file compiled from the .qrc.
    :return: The importable module name.
    """
    print("[+] Building resources...")
    generate_qrc(resource_dir, qrc_path)
    compile_qrc(qrc_path, py_output_path)

    # Convert file path to module import path
    base_dir = os.getcwd()  # Root of the project
    module_rel_path = os.path.relpath(py_output_path, base_dir)
    module_name = module_rel_path.replace(".py", "").replace(os.sep, ".")

    return module_name
