from .models import Establecimiento
from rest_framework import serializers
from .models import Like, Rating, Comment, UserProfile, Comment, CommentReply, CommentLike
from django.db.models import Avg
from phonenumbers import parse as parse_phone_number, PhoneNumberFormat
from phonenumber_field.modelfields import PhoneNumberField

from djoser.serializers import UserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.contrib.auth.models import User
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.validators import UniqueValidator


class EstablecimientoSerializer(serializers.HyperlinkedModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    is_favorited_by_user = serializers.SerializerMethodField()
    rated_by_user = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='pk')
    class Meta:
        model = Establecimiento
        fields = '__all__'
        
    def get_likes_count(self, obj):
        likes_count = Like.objects.filter(establecimiento=obj).count()
        return likes_count

    def get_comments_count(self, obj):
        comments_count = Comment.objects.filter(establecimiento=obj).count()
        return comments_count
    def get_rating_count(self, obj):
        rating_count = Rating.objects.filter(establecimiento=obj).count()
        return rating_count
    
    def get_rated_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            rating = Rating.objects.filter(establecimiento=obj, user=user).first()
            return rating.rating if rating else 0.0
        else:
            return 0.0
    
    def get_is_favorited_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, establecimiento=obj).exists()
        return False  # Not authenticated or favorite not found
    
    def get_average_rating(self, obj):
        # Query for ratings and calculate the average using aggregate
        ratings = Rating.objects.filter(establecimiento=obj)
        if ratings.exists():
            average = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
            return average
        # Return 0 if no ratings
        return 0

class NombreSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='pk')
    nombre = serializers.CharField()


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('user', 'establecimiento', 'created_at')

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('user', 'establecimiento', 'rating', 'created_at')

class RatingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('rating',)  # Only allow modifying the rating field


"""
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content' , 'created_at')
"""
class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(blank=True, region="EC")
    class Meta:
        model = UserProfile
        #fields = ['phone_number', 'first_name', 'last_name', 'address', 'pic']
        #fields = '__all__'
        exclude = ['user']


"""class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    #pic = UserProfileSerializer(source='user.userprofile', read_only=True)
    pic = serializers.SerializerMethodField()  # Use SerializerMethodField

    def get_pic(self, obj):
        # Access the related UserProfile object
        user_profile = obj.user.userprofile
        if user_profile:
            return user_profile.pic  # Return the image URL
        return None  # Return None if no profile picture
    
    class Meta:
        model = Comment
        fields = ('username', 'content', 'created_at', 'pic')
"""
class CommentReplySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = CommentReply
        fields = ['id', 'comment', 'user', 'user_name', 'user_avatar', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def get_user_name(self, obj):
        # Try to get from UserProfile first, then fallback to username
        try:
            profile = obj.user.userprofile
            return f"{profile.first_name} {profile.last_name}" if profile.first_name else obj.user.username
        except:
            return obj.user.username
    
    def get_user_avatar(self, obj):
        try:
            profile = obj.user.userprofile
            if profile.avatar:
                return profile.avatar.url
        except:
            pass
        return f"https://ui-avatars.com/api/?name={obj.user.username}"


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    replies = CommentReplySerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'establecimiento', 'user', 'user_name', 'user_avatar', 
                  'content', 'created_at', 'replies', 'likes_count', 'is_liked_by_user']
        read_only_fields = ['user', 'created_at']
    
    def get_user_name(self, obj):
        try:
            profile = obj.user.userprofile
            return f"{profile.first_name} {profile.last_name}" if profile.first_name else obj.user.username
        except:
            return obj.user.username
    
    def get_user_avatar(self, obj):
        try:
            profile = obj.user.userprofile
            if profile.avatar:
                return profile.avatar.url
        except:
            pass
        return f"https://ui-avatars.com/api/?name={obj.user.username}"
    
    def get_likes_count(self, obj):
        return obj.likes.count() if hasattr(obj, 'likes') else 0
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists() if hasattr(obj, 'likes') else False
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']


class CommentReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ['content']



class EstablecimientoCommentsSerializer(serializers.ModelSerializer):
  comments = CommentSerializer(many=True, read_only=True)  # Nested serializer for comments
  class Meta:
    model = Establecimiento
    fields = ['id', 'nombre', 'comments']  # Include only relevant fields




class UserCommentSerializer(serializers.Serializer):
  username = serializers.CharField(source='user.username')
  pic = UserProfileSerializer(source='userprofile.pic')  # Nested serializer for profile picture (optional)
  comments = CommentSerializer(many=True)

  def get_queryset(self):
    user = self.context.get('user')  # Access user from context
    est = self.context.get('id')  # Access post_id from context
    queryset = Comment.objects.none()
    if user and est:
      queryset = Comment.objects.filter(user=user, establecimiento=est)
    return queryset


"""
class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "password", "re_password")
        # if you're not using username in your frontend, we auto-generate one below

    def validate(self, attrs):
        # re_password was added by setting USER_CREATE_PASSWORD_RETYPE = True, but validate again:
        re_password = attrs.pop("re_password", None)
        if not re_password or attrs.get("password") != re_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # ensure username exists (Djoser requires username by default). If frontend doesn't provide one,
        # generate a short unique username from email.
        if not validated_data.get("username"):
            base = validated_data.get("email", "").split("@")[0]
            validated_data["username"] = f"{base}_{str(uuid.uuid4())[:8]}"

        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")

        # super().create will create the User and set the password correctly
        user = super().create(validated_data)

        # Make sure user is inactive until activation (Djoser activation flow expects this).
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = False
        user.save()

        # Create UserProfile (avoid duplicating if signal also creates it)
        UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name)

        return user
"""
class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Ya existe una cuenta registrada con este email."
            )
        ]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "re_password",
        )

    # ✅ EMAIL UNIQUENESS VALIDATION
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        re_password = attrs.pop("re_password", None)
        if not re_password or attrs.get("password") != re_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Auto-generate username if missing
        if not validated_data.get("username"):
            base = validated_data.get("email", "").split("@")[0]
            validated_data["username"] = f"{base}_{str(uuid.uuid4())[:8]}"

        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")

        user = super().create(validated_data)

        user.first_name = first_name
        user.last_name = last_name
        user.is_active = False
        user.save()

        # Create profile
        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
        )

        return user


class CustomUserSerializer(DjoserUserSerializer):
    # expose some profile info when returning user
    profile = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + ("first_name", "last_name", "profile")

    def get_profile(self, obj):
        try:
            p = obj.userprofile
            return {
                "phone_number": str(p.phone_number) if p.phone_number else "",
                "address": p.address,
                "pic": p.pic,
            }
        except UserProfile.DoesNotExist:
            return {}