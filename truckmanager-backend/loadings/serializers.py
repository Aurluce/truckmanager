from rest_framework import serializers
from .models import Loading
class LoadingSerializer(serializers.ModelSerializer):
    truck_id=serializers.CharField(source='trip.truck.truck_id',read_only=True)
    validated_by_name=serializers.SerializerMethodField()
    photo_url=serializers.SerializerMethodField()
    class Meta:
        model=Loading
        fields=['id','trip','truck_id','product_name','product_type','weight_kg','weight_verified','photo','photo_url','photo_taken_at','is_validated','validated_by','validated_by_name','validated_at','created_at','updated_at']
        read_only_fields=['id','created_at','updated_at']
    def get_validated_by_name(self,obj): return obj.validated_by.get_full_name() if obj.validated_by else None
    def get_photo_url(self,obj):
        if not obj.photo: return None
        req=self.context.get('request')
        return req.build_absolute_uri(obj.photo.url) if req else obj.photo.url
class LoadingListSerializer(serializers.ModelSerializer):
    truck_id=serializers.CharField(source='trip.truck.truck_id',read_only=True)
    photo_url=serializers.SerializerMethodField()
    class Meta:
        model=Loading
        fields=['id','truck_id','trip','product_name','weight_kg','photo_url','is_validated','created_at']
    def get_photo_url(self,obj):
        if not obj.photo:return None
        req=self.context.get('request'); return req.build_absolute_uri(obj.photo.url) if req else obj.photo.url
