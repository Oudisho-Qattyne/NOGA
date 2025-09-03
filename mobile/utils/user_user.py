import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from django.db.models import Count, Q
import joblib  # لحفظ النموذج
from mobile.models import Like,Save,Review
from products.models import Product
class UserUserRecommendationEngine:
    def init(self):
        self.user_similarity = None
        self.user_ids = None
        self.product_ids = None
        self.user_product_matrix = None
    
    def build_model(self):
        """بناء نموذج User-User التعاوني"""
        
        
        # تجميع تفاعلات جميع المستخدمين
        user_interactions = defaultdict(dict)
        
        # وزن التفاعلات المختلفة
        interaction_weights = {
            'like': 3,
            'save': 4,
            'review': 2  # الأساسي، سيضرب في قيمة التقييم
        }
        
        # جمع الإعجابات
        for like in Like.objects.select_related('user_id', 'product_id').all():
            user_interactions[like.user_id][like.product_id] = \
                user_interactions[like.user_id].get(like.product_id, 0) + interaction_weights['like']
        
        # جمع عمليات الحفظ
        for save in Save.objects.select_related('user', 'product').all():
            user_interactions[save.user_id][save.product_id] = \
                user_interactions[save.user_id].get(save.product_id, 0) + interaction_weights['save']
        
        # جمع التقييمات (نضرب وزن التقييم في قيمة التقييم)
        for review in Review.objects.select_related('user', 'product').all():
            user_interactions[review.user_id][review.product_id] = \
                user_interactions[review.user_id].get(review.product_id, 0) + (interaction_weights['review'] * review.rating)
        
        # إنشاء مصفوفة المستخدم-المنتج
        users = list(user_interactions.keys())
        products = list(set(pid for interactions in user_interactions.values() for pid in interactions.keys()))
        
        user_product_matrix = np.zeros((len(users), len(products)))
        for i, user_id in enumerate(users):
            for j, product_id in enumerate(products):
                user_product_matrix[i, j] = user_interactions[user_id].get(product_id, 0)

        user_similarity = cosine_similarity(user_product_matrix)
        print("users : " , users )
        print("products : "  , products)
        print(user_product_matrix)
        print(user_similarity)
        
        # حفظ حالة النموذج
        self.user_similarity = user_similarity
        self.user_ids = users
        self.product_ids = products
        self.user_product_matrix = user_product_matrix
        
        return self
    
    def get_recommendations(self, user_id, num_recommendations=10):

        if self.user_similarity is None:
            raise ValueError("يجب بناء النموذج أولاً باستخدام build_model()")
        
        try:
            # البحث عن index المستخدم في المصفوفة
            user_idx = self.user_ids.index(user_id)
            
            # الحصول على أوجه التشابه مع جميع المستخدمين الآخرين
            user_similarities = self.user_similarity[user_idx]
            
            # إيجاد أكثر المستخدمين تشابهًا (لا تشمل المستخدم نفسه)
            similar_users_idx = np.argsort(user_similarities)[::-1][1:6]  # 
            
        
                # تجميع المنتجات التي تفاعل معها المستخدمون المشابهون
            recommended_products = defaultdict(float)
        
            for similar_user_idx in similar_users_idx:
                    similarity_score = user_similarities[similar_user_idx]
            
            # المنتجات التي تفاعل معها المستخدم المشابه ولكن المستخدم الحالي لم يتفاعل معها
            for j, product_id in enumerate(self.product_ids):
                interaction_score = self.user_product_matrix[similar_user_idx, j]
                current_user_score = self.user_product_matrix[user_idx, j]
                
                # إذا تفاعل المستخدم المشابه مع المنتج ولكن المستخدم الحالي لم يتفاعل
                if interaction_score > 0 and current_user_score == 0:
                    recommended_products[product_id] += interaction_score * similarity_score
        
                # ترتيب المنتجات حسب مجموع الأوزان
            sorted_products = sorted(recommended_products.items(), key=lambda x: x[1], reverse=True)
            
            # إرجاع أفضل التوصيات
            return [product_id.id for product_id, score in sorted_products[:num_recommendations]]
        
        except ValueError:
                # إذا لم يكن المستخدم موجودًا في النموذج (مستخدم جديد)
            return self.get_popular_products(num_recommendations)

    def get_popular_products(self, num_recommendations=10):
        """المنتجات الشائعة كبديل للمستخدمين الجدد"""

        
        popular_products = Product.objects.annotate(
            popularity=Count('like') + Count('save') * 2 + Count('reviews') * 1.5
        ).order_by('-popularity')[:num_recommendations]
        
        return [p.id for p in popular_products]
    
    def save_model(self, filepath):
        """حفظ النموذج للاستخدام لاحقًا"""
        model_data = {
            'user_similarity': self.user_similarity,
            'user_ids': self.user_ids,
            'product_ids': self.product_ids,
            'user_product_matrix': self.user_product_matrix
        }
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath):
        """تحميل نموذج محفوظ"""
        model_data = joblib.load(filepath)
        self.user_similarity = model_data['user_similarity']
        self.user_ids = model_data['user_ids']
        self.product_ids = model_data['product_ids']
        self.user_product_matrix = model_data['user_product_matrix']
        return self