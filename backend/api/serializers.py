from rest_framework import serializers
from .models import User, Image, Annotation, Payment

# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'status', 'balance_wallet']

# Image serializer
class ImageSerializer(serializers.ModelSerializer):
    options_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = '__all__'
    
    def get_options_list(self, obj):
        # convert "Cat,Dog,Bird" to ["Cat", "Dog", "Bird"]
        return [x.strip() for x in obj.category_options.split(',')]

# Annotation serializer
class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = '__all__'