from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
import qrcode
from PIL import Image , ImageDraw

class Paginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 40

def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB in bytes

# Validate the size of uploaded images
def validate_image_size(value):
    if value.size > MAX_IMAGE_SIZE:
        raise serializers.ValidationError("Image file size is too large (max 2MB)")


def genereate(image_url , product):
    A4 = Image.open(f'mediafiles/productqr/A4.jpg')
    img = Image.open(image_url)
    new_image = Image.new('RGB',(A4.width,A4.height), (250,250,250))
    number_of_rows = A4.height//img.height
    number_of_cols = A4.width//img.width

    for j in range(0 , number_of_rows): 
        for i in range(0,number_of_cols):
            draw = ImageDraw.Draw(img)
            new_image.paste(img , (img.width*i,img.height*j))
    draw = ImageDraw.Draw(new_image)
    draw.text((10, A4.height-20), "NOGA project 2025" , fill='Black' )
    draw.text((300, A4.height-20), product , fill='Black' )
    return new_image
 

def generateQR(request , id , file_nameP , folder_name):
    file_name = f"{file_nameP}-{id}.png"
    download_file_name = f"{file_nameP}-{id}-download.jpg"
    path = f'mediafiles/productqr'
    file_path = f"{path}/{file_name}"
    download_file_path = f"{path}/{download_file_name}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5, border=3)
    qr.add_data(f"product-{id}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(file_path, 'PNG')
    download_image = genereate(file_path , f"{file_name}")
    download_image.save(download_file_path)
    qr_code = f"{request.build_absolute_uri('/')}media/productqr/{file_name}"
    qr_codes_download = f"{request.build_absolute_uri('/')}media/productqr/{download_file_name}"
    return qr_code , qr_codes_download