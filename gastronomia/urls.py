from django.urls import include, path

from . import views
#from django.views.generic import TemplateView
from gastronomia import views


urlpatterns = [
    path('', views.index, name='index'),
    path("parroquias", views.parroquias, name="parroquias"),
    
    #path('api/nombres/', views.NombresFilterView.as_view(
    #    {'get': 'list'})),
    #path('accounts/activate/<uid>/<token>', views.CustomActivationView.as_view(), name='activation'),
    
    path('api/likes/<int:pk>', views.LikeViewSet.as_view(
        {'get': 'list', 'post': 'create', 'delete': 'destroy'})),
    
    path('api/ratings/<int:pk>', views.RatingViewSet.as_view(
        {'get': 'list', 'post': 'create', 'patch': 'update', 'delete': 'destroy'})),
    
    path('api/establecimientos/<int:pk>/comments/', views.CommentViewSet.as_view(
        {'get': 'list', 'post': 'create', 'delete': 'destroy'})),
    
    path('api/user-profiles/', views.UserProfileViewSet.as_view(
        {'get': 'list', 'post': 'create', 'patch': 'update',})),
    
    path('api/establecimientos/<int:est_id>/comments/', views.EstablecimientoCommentsView.as_view()),

    # Comment endpoints
    path('comments/<int:pk>/', views.CommentViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='comment-list-create'),
    
    path('comments/<int:pk>/<int:comment_pk>/', views.CommentViewSet.as_view({
        'delete': 'destroy',
    })),
    
    # Comment reply endpoints
    path('comments/<int:comment_pk>/replies/', views.CommentReplyViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='comment-reply-list-create'),
    
    path('comments/<int:comment_pk>/replies/<int:pk>/', views.CommentReplyViewSet.as_view({
        'delete': 'destroy',
    }), name='comment-reply-delete'),
    
    # Comment like endpoints
    path('comments/<int:comment_pk>/like/', views.CommentLikeViewSet.as_view({
        'get': 'retrieve',
        'post': 'create',
        'delete': 'destroy',
    }), name='comment-like'),

    
]