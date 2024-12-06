import os
import gradio as gr
from urllib.request import url2pathname
from translate import Translator
from PyPDF2 import PdfReader
import warnings

# Ignore user warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Function to save translated text to a file and return the file path
def save_text_to_file(text, file_path, page_num, lang_code, file_name):
    pages_folder = os.path.join(os.path.dirname(file_path), "Pages")
    os.makedirs(pages_folder, exist_ok=True)
    output_file_name = f"{os.path.splitext(os.path.basename(file_name))[0]}_page_{page_num}_{lang_code}.txt"
    output_file_path = os.path.join(pages_folder, output_file_name)
    with open(output_file_path, "w", encoding='utf-8') as output_file:
        output_file.write(text)
    return output_file_path

# Function to translate text using the translate library
def translate_text(text, target_lang):
    if not text.strip():
        return "Error: Input text is empty or cannot be extracted."
    
    translator = Translator(to_lang=target_lang)
    try:
        return translator.translate(text)
    except Exception as e:
        return f"Error: {str(e)}"

# Function to extract and translate text from a PDF or TXT file or a sentence
def extract_and_translate_text(text_or_file_path, start_page=0, end_page=0, target_lang='english', download=False, file_name=""):
    if not text_or_file_path:
        return "Error: Please provide a text sentence or a file path."
    
    if os.path.isfile(text_or_file_path):
        file_path = url2pathname(text_or_file_path.strip('\"')) if text_or_file_path.startswith('file://') else text_or_file_path
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                translated_text = ""

                for page_num in range(start_page, end_page + 1):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        translated_page_text = translate_text(text, target_lang)
                    except IndexError:
                        return f"Error: Page {page_num} does not exist in the PDF."
                    except Exception as e:
                        return f"Error: {str(e)}"

                    if download:
                        save_text_to_file(translated_page_text, file_path, page_num, target_lang, file_name)

                    translated_text += f"Page {page_num}:\n\n{translated_page_text}\n\n---\n\n"

        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
                translated_text = translate_text(text, target_lang)
                if download:
                    save_text_to_file(translated_text, file_path, 0, target_lang, file_name)
        else:
            return "Error: Unsupported file type. Please provide a PDF or TXT file."
    else:
        text = text_or_file_path
        translated_text = translate_text(text, target_lang)

    return translated_text

# Get a list of all available languages for the user interface dropdown
language_choices = [
    'english', 'french', 'german', 'spanish', 'italian', 'chinese', 'japanese', 'hindi', 'arabic'
]

# Create a Gradio interface
iface = gr.Interface(
    fn=extract_and_translate_text,
    inputs=[
        gr.Textbox(label='Enter a PDF or TXT file path or paste a sentence'),
        gr.Slider(label='Start page (PDF only)', minimum=0, maximum=100, step=1, value=0),
        gr.Slider(label='End page (PDF only)', minimum=0, maximum=100, step=1, value=0),
        gr.Dropdown(label='Choose translation language:', choices=language_choices, value='english'),
        gr.Checkbox(label="Download translation?", value=False),
        gr.Textbox(label='Add a prefix to the file(s)', value="")
    ],
    outputs=[gr.Textbox(label='Translated Text')],
    title='💥 Universal PDF/Text Translator 💥',
    description='Extract and translate text from PDF or TXT files as well as pasted sentences.',
    allow_flagging='never',
    examples=[
        ['example.pdf', 1, 1, 'french', False, '']
    ],
)

if __name__ == '__main__':
    iface.launch()
