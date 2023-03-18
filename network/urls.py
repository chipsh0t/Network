from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/user=<str:name>", views.profile_page, name="profile_page"),
    path("following_page", views.following_page, name="following_page"),
    #api routes
    path("all_posts", views.all_posts_view, name="all_posts"),
    path("profile_posts/<str:profile_username>", views.profile_posts_view, name="profile_posts"),
    path("following_posts", views.following_posts_view, name="following_posts"),
    path("create_post", views.create_post_view, name="create_post"),
    path("edit_post/<int:pk>", views.post_edit_view, name="edit_post"),
    path("like_unlike_post", views.like_unlike_post_view, name="like_unlike_post"),
    path("post_detail/<int:pk>", views.post_detail_view, name="post"),
    path("follow", views.create_following_view, name="follow"),
    path("unfollow", views.delete_following_view, name="unfollow"),
    path("user_profile_info/<str:username>", views.user_profile_info_view, name="user_info")
]
