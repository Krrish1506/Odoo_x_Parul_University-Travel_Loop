import urllib.request
import os
import sys

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        if hasattr(pip, 'main'):
            pip.main(['install', package])
        else:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    finally:
        globals()[package] = importlib.import_module(package)

try:
    install_and_import('pypdf')
    from pypdf import PdfReader
    
    reader = PdfReader("Traveloop.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
        
    with open("pdf_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully extracted text to pdf_text.txt")
except Exception as e:
    print(f"Error: {e}")
