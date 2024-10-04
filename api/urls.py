from django.urls import path

from . import views

urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("user", views.user_view, name="user"),
    path("user_reviews", views.user_reviews, name="user_reviews"),
    path("user_favorites", views.user_favorites, name="user_favorites"),
    path("businessP", views.business_post_view, name="business"),
    path("review/<int:id>", views.business_reviews, name="review"),
    path("businesses", views.businesses_view, name="businesses"),
    path("visit", views.visit, name="visit"),

]
