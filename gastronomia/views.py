from tokenize import String
from django.shortcuts import render
from .models import Establecimiento, Like, Rating, Comment, UserProfile, CommentLike, CommentReply
from .serializers import EstablecimientoSerializer, NombreSerializer, LikeSerializer, RatingSerializer, RatingCreateUpdateSerializer, CommentSerializer, CommentCreateSerializer, UserProfileSerializer, UserCommentSerializer, EstablecimientoCommentsSerializer, CommentReplyCreateSerializer, CommentCreateSerializer, CommentReplySerializer
from rest_framework import viewsets
#from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator



class MyCustomPagination(PageNumberPagination):
    page_size = 15
    page_query_param = 'page'



# Create your views here.
#from django.http import HttpResponse

PARROQUIAS = {"Taquil": "Taquil",
            "Chantaco": "Chantaco",
            "Chuquiribamba": "Chuquiribamba",
            "El_Cisne": "El_Cisne",
            "Gualel": "Gualel" }


def index(request):
    template='gastronomia/index.html'
    lista = Establecimiento.objects.all()
    return render(request,template, {
        "lista": lista
    })


def parroquias(request):
    context = {
        "parroquias": PARROQUIAS
    }
    return render(request, "gastronomia/parroquias.html", {
        "context": context
    })

class EstablecimientoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows establecimientos to be viewed or edited.
    """
    #queryset = Establecimiento.objects.all().order_by('-precio_promedio')

    permission_classes = [IsAuthenticatedOrReadOnly]
    
    serializer_class = EstablecimientoSerializer
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `nombte`, `parroquia` or `precio` query parameter in the URL.
        """
        queryset = Establecimiento.objects.all().order_by('-precio_promedio')
        nombre = self.request.query_params.get('nombre')
        
        id = self.request.query_params.get('id')
        
        parroquia = self.request.query_params.get('parroquia')
        precio = self.request.query_params.get('precio')
        
        if id is not None:
            queryset = Establecimiento.objects.all()
            queryset = queryset.filter(pk=id)
        
        if nombre is not None:
            queryset = Establecimiento.objects.all()
            queryset = queryset.filter(nombre=nombre)
        if parroquia is not None:
            parroquia_values = parroquia.split(",")
            queryset = queryset.filter(parroquia__in=parroquia_values)
        if precio is not None:
            queryset = queryset.filter(precio_promedio__lte=precio)
        return queryset

    # def get_permissions(self):
    #     permission_classes = []
    #     if self.request.method != 'GET':
    #         permission_classes = [IsAuthenticated]

    #     return [permission() for permission in permission_classes]
    


class NombresFilterView(viewsets.ModelViewSet):
    """
    API endpoint that allows establecimientos nombres to be viewed or edited.
    """
    queryset = Establecimiento.objects.all()
    serializer_class = NombreSerializer
    filter_backends = [SearchFilter]
    search_fields = ['nombre']  # Specify fields to search within

    # def list(self, request):
    #     name = request.query_params.get('nombre', None)  # Get the query parameter
    #     if name:
    #         self.queryset = self.queryset.filter(nombre__icontains=name)  # Filter using case-insensitive contains
    #     serialized_data = self.serializer_class(self.queryset, many=True)
    #     return Response(serialized_data.data)
    def get_queryset(self):
        queryset = Establecimiento.objects.all()
        nombre = self.request.query_params.get('nombre')
        if nombre is not None:
            queryset = Establecimiento.objects.all()
            queryset = queryset.filter(nombre__icontains=nombre)
        return queryset
    
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    


class UserProfileViewSet(viewsets.ViewSet):
    
    
    
    permission_classes = [IsAuthenticated]


    def list(self, request):
        # Get all ratings for a specific establecimiento
        print('ingresa en list')
        userProfile = UserProfile.objects.filter(user=request.user)
        if userProfile:
            serializer = UserProfileSerializer(userProfile, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'UserProfile not found'}, status=status.HTTP_404_NOT_FOUND)
        
            
    def create(self, request):
        user, created = User.objects.get_or_create(username = request.user)
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserProfileSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def destroy(self, request, pk=None):
        user = request.user
        try:
            # Deleting the user object triggers the CASCADE delete on UserProfile
            user.delete()
            return Response(
                {"message": "Cuenta eliminada correctamente"}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        


####### SOCIAL COMPONENT #########

class LikeViewSet(viewsets.ViewSet):
    #permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def list(self, request, pk=None):
        # Get all likes for the currently authenticated user (optional)
        #if request.user.is_authenticated:
        #likes = Like.objects.filter(user=request.user)
        try:
            est = Establecimiento.objects.get(pk=pk)
        except Establecimiento.DoesNotExist:
            return Response({'error': 'Establecimiento not found'}, status=status.HTTP_404_NOT_FOUND)
        likes = Like.objects.filter(establecimiento=est)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

        #return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, pk=None):
        if pk:
            # Check if post exists
            try:
                est = Establecimiento.objects.get(pk=pk)
            except Establecimiento.DoesNotExist:
                return Response({'error': 'Establecimiento not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if user already liked the establecimientos
            if Like.objects.filter(user=request.user, establecimiento=est).exists():
                return Response({'error': 'Already liked this startup'}, status=status.HTTP_400_BAD_REQUEST)

            # Create new like
            like = Like.objects.create(user=request.user, establecimiento=est)
            serializer = LikeSerializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        if pk:
            # Check if like exists
            try:
                est = Establecimiento.objects.get(pk=pk)
                like = Like.objects.get(establecimiento=est, user=request.user)
            except Like.DoesNotExist:
                return Response({'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if user owns the like
            if like.user != request.user:
                return Response({'error': 'You cannot delete other users\' likes'}, status=status.HTTP_403_FORBIDDEN)

            # Delete like
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class RatingViewSet(viewsets.ViewSet):
    #permission_classes = [IsAuthenticated]
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    

    def list(self, request, pk=None):
        # Get all ratings for a specific establecimiento
        if pk:
            try:
                establecimiento = Establecimiento.objects.get(pk=pk)
            except Establecimiento.DoesNotExist:
                return Response({'error': 'Establecimiento not found'}, status=status.HTTP_404_NOT_FOUND)
            ratings = Rating.objects.filter(establecimiento=establecimiento)
            serializer = RatingSerializer(ratings, many=True)
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, pk=None):
        if pk:
            try:
                establecimiento = Establecimiento.objects.get(pk=pk)
            except Establecimiento.DoesNotExist:
                return Response({'error': 'Establecimiento not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if user already rated the post
            if Rating.objects.filter(user=request.user, establecimiento=establecimiento).exists():
                return Response({'error': 'Already rated this establecimiento'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = RatingCreateUpdateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, establecimiento=establecimiento)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        # Update user's rating for a specific post
        if pk:
            rating = None
            try:
                establecimiento = Establecimiento.objects.get(pk=pk)
                rating = Rating.objects.get(user=request.user, establecimiento=establecimiento)
            except Rating.DoesNotExist:
                return Response({'error': 'Rating not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if rating.user != request.user:
                return Response({'error': 'You can only update your own ratings'}, status=status.HTTP_403_FORBIDDEN)
            serializer = RatingCreateUpdateSerializer(rating, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        if pk:
            # Check if rating exists
            try:
                rating = Rating.objects.get(pk=pk)
            except Rating.DoesNotExist:
                return Response({'error': 'Rating not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if user owns the rating
            if rating.user != request.user:
                return Response({'error': 'You cannot delete other users\' ratings'}, status=status.HTTP_403_FORBIDDEN)

            # Delete rating
            rating.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class CommentViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def list(self, request, pk=None):
        """Get all comments for a specific establecimiento"""
        if pk:
            try:
                establecimiento = Establecimiento.objects.get(pk=pk)
            except Establecimiento.DoesNotExist:
                return Response({'error': 'Establecimiento not found'}, status=status.HTTP_404_NOT_FOUND)
            
            comments = Comment.objects.filter(establecimiento=establecimiento).prefetch_related(
                'replies', 'replies__user', 'likes'
            ).order_by('-created_at')
            
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, pk=None):
        """Create a new comment"""
        if pk:
            try:
                establecimiento = Establecimiento.objects.get(pk=pk)
            except Establecimiento.DoesNotExist:
                return Response({'error': 'Establecimiento not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = CommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(user=request.user, establecimiento=establecimiento)
                response_serializer = CommentSerializer(comment, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None, comment_pk=None):
        """Delete a comment and all its replies"""
        if comment_pk:
            try:
                # Use 'establecimiento' instead of 'emprendimiento_id'
                comment = Comment.objects.get(pk=comment_pk, establecimiento_id=pk)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user owns the comment
            if comment.user != request.user:
                return Response(
                    {'error': 'You cannot delete other users\' comments'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete the comment (replies will be cascade deleted if properly configured)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

class CommentReplyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, comment_pk=None):
        """Get all replies for a comment"""
        if comment_pk:
            try:
                comment = Comment.objects.get(pk=comment_pk)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            replies = CommentReply.objects.filter(comment=comment).order_by('created_at')
            serializer = CommentReplySerializer(replies, many=True)
            return Response(serializer.data)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, comment_pk=None):
        """Create a reply to a comment"""
        if comment_pk:
            try:
                comment = Comment.objects.get(pk=comment_pk)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CommentReplyCreateSerializer(data=request.data)
            if serializer.is_valid():
                reply = serializer.save(user=request.user, comment=comment)
                response_serializer = CommentReplySerializer(reply)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, comment_pk=None, pk=None):
        """Delete a reply"""
        if pk:
            try:
                reply = CommentReply.objects.get(pk=pk, comment_id=comment_pk)
            except CommentReply.DoesNotExist:
                return Response({'error': 'Reply not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if reply.user != request.user:
                return Response(
                    {'error': 'You cannot delete other users\' replies'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            reply.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CommentLikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, comment_pk=None):
        """Check if user has liked a comment"""
        if comment_pk:
            try:
                comment = Comment.objects.get(pk=comment_pk)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            is_liked = CommentLike.objects.filter(comment=comment, user=request.user).exists()
            return Response({'is_liked': is_liked, 'comment_id': comment_pk})
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, comment_pk=None):
        """Like a comment"""
        if comment_pk:
            try:
                comment = Comment.objects.get(pk=comment_pk)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if already liked
            if CommentLike.objects.filter(comment=comment, user=request.user).exists():
                return Response({'error': 'Already liked this comment'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create like
            CommentLike.objects.create(comment=comment, user=request.user)
            return Response({'message': 'Comment liked successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, comment_pk=None):
        """Unlike a comment"""
        if comment_pk:
            try:
                comment = Comment.objects.get(pk=comment_pk)
                like = CommentLike.objects.get(comment=comment, user=request.user)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
            except CommentLike.DoesNotExist:
                return Response({'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
            
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

class UserCommentView(APIView):
  def get(self, request, id):
    try:
      user = User.objects.get(username=request.user)
      user_profile = UserProfile.objects.filter(user=request.user)  # Access profile through related object
      serializer = UserCommentSerializer(
          instance=None,  # No instance needed for filtering
          context={'user': user, 'id': id}  # Pass user and post_id in context
      )
      return Response(serializer.data)
    except User.DoesNotExist:
      return Response({'error': 'User not found'}, status=404)

class EstablecimientoCommentsView(APIView):
  def get(self, request, est_id):
    try:
      est = Establecimiento.objects.get(pk=est_id)
      serializer = EstablecimientoCommentsSerializer(est)
      return Response(serializer.data)
    except Establecimiento.DoesNotExist:
      return Response({'error': 'Establecimiento not found'}, status=404)

from django.views import View
from rest_framework.request import Request
import requests
class ActivateUserView(View):
    template_name = "gastronomia/activation_result.html"

    def get(self, request, uid, token):
        """
        Called when user clicks the email link.
        This view forwards uid/token to Djoser's activation endpoint and shows a result page.
        """
        # Build the URL of Djoser's activation endpoint (hardcoded)
        activation_url = request.build_absolute_uri("/auth/users/activation/")

        # Send POST to Djoser's activation endpoint
        response = requests.post(
            activation_url,
            json={"uid": uid, "token": token},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 204:
            context = {"status": "success"}
        else:
            context = {"status": "error", "detail": response.text}

        return render(request, self.template_name, context)


class PasswordResetConfirmView(APIView):
    """
    Custom view to handle password reset confirmation with HTML form
    """
    permission_classes = []
    
    def get(self, request, uid, token):
        """Display the password reset form"""
        try:
            # Verify the token is valid
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                return render(request, 'email/password_reset_confirm.html', {
                    'uid': uid,
                    'token': token,
                    'validlink': True,
                })
            else:
                return render(request, 'email/password_reset_confirm.html', {
                    'validlink': False,
                    'error': 'El enlace de restablecimiento es inválido o ha expirado.'
                })
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'email/password_reset_confirm.html', {
                'validlink': False,
                'error': 'El enlace de restablecimiento es inválido.'
            })
    
    def post(self, request, uid, token):
        """Handle password reset form submission"""
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
            
            if not default_token_generator.check_token(user, token):
                return JsonResponse({
                    'success': False, 
                    'error': 'El enlace de restablecimiento es inválido o ha expirado.'
                }, status=400)
            
            new_password = request.POST.get('new_password1')
            confirm_password = request.POST.get('new_password2')
            
            # Validate passwords match
            if new_password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'error': 'Las contraseñas no coinciden.'
                }, status=400)
            
            # Validate password strength (optional - add your own validation)
            if len(new_password) < 8:
                return JsonResponse({
                    'success': False,
                    'error': 'La contraseña debe tener al menos 8 caracteres.'
                }, status=400)
            
            # Set the new password
            user.set_password(new_password)
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Contraseña actualizada correctamente.'
            })
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return JsonResponse({
                'success': False,
                'error': 'Error al procesar la solicitud.'
            }, status=400)