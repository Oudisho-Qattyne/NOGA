from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination


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
