from rest_framework import serializers
from network.models import User,Post, Followed, Liked
from django.core.exceptions import ObjectDoesNotExist


# creating a serializer for post model
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields=('id',
                'creator',
                'creation_date',
                'text_content',
                'edited',
                'like_count',
                'editing_allowed',
                'liked_by_user')
    
    creator = serializers.SlugRelatedField(many=False, queryset = User.objects.all(), slug_field='username')
    creation_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M") 
    like_count = serializers.SerializerMethodField(method_name='get_like_counts')
    editing_allowed = serializers.SerializerMethodField(method_name = 'check_editing_permission')
    liked_by_user = serializers.SerializerMethodField(method_name = 'check_if_liked')

    #get like counts
    def get_like_counts(self, obj):
        try:
            return obj.liked_by.count()
        except AttributeError:
            #if a post is new
            return 0

    #this method checks if requesting user is the creator of this post
    def check_editing_permission(self,obj):
        requesting_user_username = self.context.get("requesting_user")
        if(requesting_user_username):
            try:
                return requesting_user_username == obj.creator.username
            except AttributeError:
                #if a post is new
                return True
        return False
    
    #this method returns true if user likes the post
    def check_if_liked(self,obj):
        try:
            requesting_user = User.objects.get(username = self.context.get("requesting_user"))
            Liked.objects.get(user=requesting_user, target_post = Post.objects.get(id=obj.id))
        except (ObjectDoesNotExist, AttributeError):
            return False
        return True
        

#serializer for Followed model
class FollowedSerializer(serializers.ModelSerializer):
    class Meta:
        model=Followed
        fields=('id', 'following', 'followers', 'deleted')
    
    following = serializers.SlugRelatedField(many=False, queryset = User.objects.all(), slug_field='username')
    followers = serializers.SlugRelatedField(many=False, queryset = User.objects.all(), slug_field='username')


#serializer for Liked model
class LikedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liked
        fields=('user', 'target_post')
    
    user = serializers.SlugRelatedField(many=False, queryset = User.objects.all(), slug_field='id')
    target_post = serializers.SlugRelatedField(many=False, queryset = Post.objects.all(), slug_field='id')


#creating a serializer for User profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','following','followers','is_following')

    following = serializers.SerializerMethodField(method_name='get_following_count')
    followers = serializers.SerializerMethodField(method_name='get_followers_count')
    is_following = serializers.SerializerMethodField(method_name='check_if_following')

    def get_following_count(self,obj):
        return obj.following.filter(deleted='False').count()

    def get_followers_count(self,obj):
        return obj.followers.filter(deleted='False').count()
    
    def check_if_following(self,obj):
        #checking if requesting user is following displayed user
        requesting_user_username = self.context.get("requesting_user_username")
        if(requesting_user_username):
            try:
                requesting_user = User.objects.get(username = requesting_user_username)
                result = bool(Followed.objects.get(following=requesting_user, followers=obj, deleted=False))
            except ObjectDoesNotExist:
                return False
            return result
        return False


    

