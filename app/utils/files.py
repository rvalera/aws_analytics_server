import base64

def get_base64_from_files(file_list):
    base64_files = []
    
    for file_name in file_list:
        with open(file_name, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            base64_files.append(base64_image)

    return base64_files