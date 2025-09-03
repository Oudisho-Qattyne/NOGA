import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori,association_rules
from django.db import transaction
from ..models import AssociationRule
from sales.models import Purchase , Purchased_Products
def extract_transaction_data():
    purchases=Purchase.objects.filter(status='completed')
    transactions=[]
    purchase_count=0
    product_count=0
    for purchase in purchases:
        product_ids=[]
        for product in purchase.purchased_products.all():
            p_id=product.product.product.id
            product_ids.append(str(p_id))
        if product_ids:
            print(product_ids)
            transactions.append(product_ids)
            purchase_count+=1
            product_count+=len(product_ids)
        # print(transactions)
        print(f"processing {purchase_count} invoice has {product_count} product")
    return transactions
                
def prepar_data_for_analysis(transactions):
    if not transactions:
        print('there is not data to process')
        return pd.DataFrame()
    try:
        te=TransactionEncoder()
        te_ary=te.fit(transactions).transform(transactions)
        df=pd.DataFrame(te_ary,columns=te.columns_)
        print(f"preparing {len(transactions)} transaction contain {len(te.columns_)} unique product")
        return df
    except Exception as e:
        print(f"error in preparing data {e}")
        return pd.DataFrame()
    

def generate_association_rules_df(min_support=0.01,min_threshold=1.0):
    transactions=extract_transaction_data()
    if not transactions:
        return pd.DataFrame()
    df=prepar_data_for_analysis(transactions)
    if df.empty:
        return pd.DataFrame()
    try:
        frequent_itemsets=apriori(df,min_support=min_support,use_colnames=True)
        # print(frequent_itemsets)
        if frequent_itemsets.empty:
            print("frequent itemsets not found")
            return pd.DataFrame()
        rules=association_rules(frequent_itemsets,metric="lift",min_threshold=min_threshold)
        # print(rules)
        if rules.empty:
            print("association rules not found")
        rules=rules.sort_values(['lift','confidence'],ascending=[False,False])
        print(f"{len(rules)} association rule are generated")
        # print(rules)
        return rules
    except Exception as e:
        print(f"error in generating rule {e}")
        return pd.DataFrame()


@transaction.atomic
def save_association_rules(rules_df):
    if  rules_df.empty:
        print("no association rule to save")
        return 0
    try:
        deleted_count,_=AssociationRule.objects.all().delete()
        print("deleted old rule")

        saved_count=0
        unique_rules=set()
        for index,rule in rules_df.iterrows():
            try:
                antecedents=list(rule['antecedents'])
                consequents=list(rule['consequents'])
                rule_key=f"{str(antecedents)}->{str(consequents)}"
                if rule_key in unique_rules:
                    continue
                unique_rules.add(rule_key)
                AssociationRule.objects.create(
                    antecedents=antecedents,
                    consequents=consequents,
                    support=float(rule['support']),
                    confidence=float(rule['confidence']),
                    lift=float(rule['lift'])
                )
                saved_count+=1
            except Exception as e:
                print(f"error in rule {index}: {e}")
        return saved_count
    except Exception as e:
            print(f"error in save rule : {e}")
            raise
    
def update_association_rules(min_support=0.01,min_threshold=1.0):
    try:
        rules_df=generate_association_rules_df(min_support,min_threshold)
        if rules_df.empty:
            raise
        saved_count=save_association_rules(rules_df)
        print(saved_count)
        if saved_count>0:
            message=" succesfuly saved"
            return message
        else:
            message="not save any rule"
            return message
    except Exception as e:
        error_message=f"update faild"
        return error_message
        