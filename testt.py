import pandas as pd

from sales.models import Purchase,Purchased_Products

def extract_transaction_data():
    purchases=Purchase.objects.filter(status='completed').only('id')
    transactions=[]
    purchase_count=0
    product_count=0

    for purchase in purchases:
        product_ids=[]
        for product in Purchased_Products.product.all():
            print(product)
            # product_ids.append(str())