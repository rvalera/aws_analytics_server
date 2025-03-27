import pymupdf
from pdf2image import convert_from_path
import os

import numpy as np
import PIL
from PIL import Image
from dotenv import load_dotenv
from .files import get_base64_from_files

import math

class PDFProcessor:
    def __init__(self, file_name: str):
        self.file_name = file_name
        load_dotenv()        

        self.extracted_text = self.__extract_text()

        self.base_path = os.getenv('TEMPDIR')
        self.preprocessing_path = os.path.join(self.base_path, 'preprocessing')        


    def __extract_text(self) -> str:
        doc = pymupdf.open(self.file_name)
        texts = []
        for page in doc:
            text = page.get_text().encode("utf8")
            new_text = text.decode("utf-8")
            if new_text and len(new_text.strip()):
                texts.append(new_text)
        return texts

    def contains_text(self) -> bool:
        texts = self.__extract_text()
        return len(texts) > 0

    def get_content_to_analyze(self) -> (str,list):
        source_path, file_name = os.path.split(self.file_name)
        fname, extension = os.path.splitext(file_name)
        
        content_list = []     
        content_type = ''   
        if not self.contains_text():
            to_analysis = []            
            pages = convert_from_path(self.file_name, 500)
            for count, page in enumerate(pages):
                filename_tosave = os.path.join(self.preprocessing_path, f'{fname}-{count}.png')
                page.save(filename_tosave, 'PNG')
                
                img_exp = Image.open(filename_tosave)
                width, height = img_exp.size
                
                factor = 0.4
                new_width = int(width * factor)
                new_height = int(height * factor)
                
                MAX_SIZE = (new_width, new_height)
                img_exp.thumbnail(MAX_SIZE)
                img_exp.save(filename_tosave, optimize=True)
                
                to_analysis.append(filename_tosave)
            
            content_list = get_base64_from_files(to_analysis)  
            content_type = 'image'
        else:
            content_list.append(self.extracted_text)
            content_type = 'text'
            
        return (content_type,content_list)
