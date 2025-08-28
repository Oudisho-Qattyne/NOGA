# utils/recommendation_utils.py
from collections import defaultdict
from django.db.models import Q
from mobile.models import Like, Save, Review , Client_Profile
from sales.models import Purchase , Purchased_Products , Customer

class RecommendationEngine:
    # Weight different interaction types
    INTERACTION_WEIGHTS = {
        'purchase': 1.0,
        'rating': 0.9,  # Will be multiplied by normalized rating
        'like': 0.7,
        'save': 0.6,
    }
    
    @staticmethod
    def get_user_interaction_matrix():
        """Create a user-item interaction matrix with weighted scores from separate models"""
        user_item_matrix = defaultdict(dict)
        
        # Process likes
        for like in Like.objects.all().select_related('user_id', 'product_id'):
            user_item_matrix[like.user_id.id][like.product_id.id] = user_item_matrix[
                like.user_id.id
            ].get(like.product_id, 0) + RecommendationEngine.INTERACTION_WEIGHTS['like']
        
        # Process saves
        for save in Save.objects.all().select_related('user', 'product'):
            user_item_matrix[save.user.id][save.product.id] = user_item_matrix[
                save.user.id
            ].get(save.product.id, 0) + RecommendationEngine.INTERACTION_WEIGHTS['save']
        
        # Process ratings
        for rating in Review.objects.all().select_related('user', 'product'):
            normalized_rating = rating.rating / 5.0
            user_item_matrix[rating.user.id][rating.product.id] = user_item_matrix[
                rating.user.id
            ].get(rating.product.id, 0) + (normalized_rating * RecommendationEngine.INTERACTION_WEIGHTS['rating'])
        
        # Process purchases
        for purchase in Purchase.objects.all():
            user = Client_Profile.objects.filter(national_number=purchase.customer.national_number)
            print(user)
            if len(user) > 0:
                user = user.first().user
                for purchased_product in purchase.purchased_products:
                    user_item_matrix[user.id][purchased_product.product.product.id] = user_item_matrix[
                        user.id
                    ].get(purchased_product.product.product.id, 0) + (RecommendationEngine.INTERACTION_WEIGHTS['purchase'] * purchased_product.quantity)
        print(user_item_matrix)
        return user_item_matrix
    
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        common_items = set(vec1.keys()) & set(vec2.keys())
        
        if not common_items:
            return 0
            
        dot_product = sum(vec1[item] * vec2[item] for item in common_items)
        magnitude1 = sum(score ** 2 for score in vec1.values()) ** 0.5
        magnitude2 = sum(score ** 2 for score in vec2.values()) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
            
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    def get_users_who_interacted_with_item(item_id):
        """Get all users who interacted with an item through any interaction type"""
        user_ids = set()
        
        # Get users from each interaction type
        user_ids.update(Like.objects.filter(product_id=item_id).values_list('user_id', flat=True))
        user_ids.update(Save.objects.filter(product=item_id).values_list('user_id', flat=True))
        user_ids.update(Review.objects.filter(product=item_id).values_list('user_id', flat=True))
        customers_id = Purchased_Products.objects.filter(product__product=item_id).values_list('purchase__customer', flat=True)
        users = []
        for customer_id in customers_id:
            customer = Customer.objects.get(id=customer_id)
            user = Client_Profile.objects.filter(national_number=customer.national_number)
            if len(user) > 0:
                users.append(user.first().user)
        user_ids.update(users)
        
        return user_ids