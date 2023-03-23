from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

import datetime

#importing models
from .models import User, Post, Followed, Liked

#imports from django-rest
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from network.serializers import LikedSerializer, PostSerializer,FollowedSerializer,UserSerializer


def index(request):
    """
        sends authenticated users to the index page,
        redirect to Register page if not authenticated
    """
    if request.user.is_authenticated:
        return render(request, "network/index.html")
    #send user to the registration page
    return HttpResponseRedirect(reverse("register"))


@login_required
def profile_page(request, name):
    """
        loads user`s profile page
    """ 
    try:
        user = User.objects.get(username=name)
    except ObjectDoesNotExist:
        raise Http404
    return render (request, "network/profile_page.html", {"user":user})


@login_required
def following_page(request):
    return render(request, "network/following_page.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password !"
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match !"
            })
        #if passwords match validate it
        try:
            #try validating password
            validate_password(password,request.user)
        except ValidationError as val_err:
            #if validation fails Validation error is raised and messages are sent to client
            return render(request, "network/register.html", {
                "message": "Your password is weak !"
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken !"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


#API views
@login_required
@api_view(['GET'])
def all_posts_view(request):
    """ 
        returns every post object to display on the index page
    """ 
    paginator = PageNumberPagination()
    paginator.page_size = 10
    posts = Post.objects.all()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True, context={"requesting_user":request.user.username})
    return paginator.get_paginated_response(serializer.data)


@login_required
@api_view(['GET'])
def profile_posts_view(request,profile_username):
    """
        returns posts for a specific user
    """
    try:
        profile_user = User.objects.get(username = profile_username)
        posts = Post.objects.filter(creator = profile_user)
    except (KeyError, ObjectDoesNotExist):
        return Response(status = status.HTTP_404_NOT_FOUND)
    #paginate the result
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True, context={"requesting_user":request.user.username})
    #return paginated response
    return paginator.get_paginated_response(serializer.data)


@login_required
@api_view(['GET'])
def following_posts_view(request):
    """
        returns posts for a user`s following page
    """
    try:
        user = User.objects.get(id = request.user.id)
    except ObjectDoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)
    #get user Following list
    following_list = list(obj.followers for obj in user.following.all() if not obj.deleted)
    posts = Post.objects.filter(creator__in = following_list)
    #paginate the result
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True, context={"requesting_user":request.user.username})
    #return paginated response
    return paginator.get_paginated_response(serializer.data)


@login_required
@api_view(['PUT'])
def post_edit_view(request,pk):
    """
        API view for changing the text content of the post
    """
    data = {
        "text_content":request.data["updated_text_content"],
        "edited":True
    }
    try:
        target_post = Post.objects.get(id = pk)
    except ObjectDoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)
    if request.user != target_post.creator:
        return Response(status = status.HTTP_400_BAD_REQUEST)
    #update text content and return updated post
    serializer = PostSerializer(target_post, data=data, partial=True, context={"requesting_user":request.user.username})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

@login_required
@api_view(['GET'])
def post_detail_view(request, pk):
    """
    API view for post details
    """
    try:
        post = Post.objects.get(id = pk)
        serializer = PostSerializer(post, many = False, context={"requesting_user":request.user.username})
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)


@login_required
@api_view(['POST'])
def create_post_view(request):
    """ 
        API view for creating a post
    """
    data = {
        "creator" : request.user,
        "text_content" : request.data["text_content"],
        "creation_date":datetime.datetime.now()
    }
    #post = Post(creator = request.user, text_content = request.data["text_content"], creation_date = datetime.datetime.now())
    serializer = PostSerializer(data = data,many = False, context={"requesting_user":request.user.username})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED) 
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['POST', 'DELETE'])
def like_unlike_post_view(request):
    """
        API view for liking and unliking posts
    """
    user_id = request.user.id
    post_id = request.data["post_id"]
    if request.method == 'POST':
        data = {
            "user" : user_id,
            "target_post" : post_id
        }
        #create a new object in the liked table
        serializer = LikedSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            updated_post = Post.objects.get(pk = post_id) 
            #returning updated information for post to update the like count
            updated_post_serializer = PostSerializer(updated_post, many = False, context={"requesting_user":request.user.username})
            return Response(updated_post_serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            liked_obj = Liked.objects.get(user = user_id, target_post = post_id)
        except ObjectDoesNotExist:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        #if the post exists, delete the like
        liked_obj.delete()
        updated_post = Post.objects.get(pk = post_id) 
        #returning updated information for post to update the like count
        updated_post_serializer = PostSerializer(updated_post, many = False, context={"requesting_user":request.user.username})
        return Response(updated_post_serializer.data)


@login_required
@api_view(['GET'])
def user_profile_info_view(request, username):
    """"
        Returns user data to display on the profile page.
    """
    try:
        user=User.objects.get(username = username)
        serializer = UserSerializer(user,many=False, context={"requesting_user_username":request.user.username})
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)


@login_required
@api_view(['POST'])
def create_following_view(request):
    """
        Lets a user follow another user.
    """
    try:
        #user which is being followed
        user_followed = User.objects.get(username = request.data["followers"])
    except ObjectDoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)
        
    data = {
        "following":request.user,
        "followers":user_followed,
        "deleted":False
    }
    if request.user == user_followed:
        #self following is forbidden
        return Response(status = status.HTTP_403_FORBIDDEN)

    serializer = FollowedSerializer(data=data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            #updating a deleted status on old Following model object
            target = Followed.objects.get(following=request.user, followers=User.objects.get(username=request.data["followers"]), deleted=True)
            serializer = FollowedSerializer(instance=target, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['PUT'])
def delete_following_view(request):
    """
        Lets a user unfollow another user.
    """
    data={
        "deleted":True
    }

    try:
        target = Followed.objects.get(following=request.user, followers=User.objects.get(username=request.data["followers"]), deleted=False)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    #setting deleted status of an object as True
    serializer = FollowedSerializer(target, data = data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    