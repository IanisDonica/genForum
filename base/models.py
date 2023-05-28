from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.db.models import UniqueConstraint
from .utils.formatChecker import ContentTypeRestrictedFileField
from PIL import Image as im
from forum.settings import BASE_DIR
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone


class CustomUserManager(UserManager):
    def _create_user(self, email, password, name, **extra_fields):
        if not email or not name:
            raise ValueError("no email or name")
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()

        return user
    
    def create_user(self, email=None, password=None, name=None, **extra_fields):
        return self._create_user(email, password, name, **extra_fields)

    def create_superuser(self, email=None, password=None, name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self._create_user(email, password, name, **extra_fields)

class BadgeType(models.Model):
    name = models.CharField(max_length=200, null=True, default=None)
    html = models.TextField(max_length=9999, unique=True)

    inheritance = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    make_comments = models.BooleanField(default=None, null=True)
    make_posts_perm = models.BooleanField(default=None, null=True)
    edit_comments_perm = models.BooleanField(default=None, null=True)
    edit_posts_perm = models.BooleanField(default=None, null=True)
    delete_comments_perm = models.BooleanField(default=None, null=True)
    delete_post_perm = models.BooleanField(default=None, null=True)
    see_deleted_comments_perm = models.BooleanField(default=None, null=True)
    make_comments_on_locked_perm = models.BooleanField(default=None, null=True)
    lock_post_perm = models.BooleanField(default=None, null=True)
    unlock_post_perm = models.BooleanField(default=None, null=True)
    see_comment_history = models.BooleanField(default=None, null=True)
    see_post_history = models.BooleanField(default=None, null=True)
    see_deleted_post_perm = models.BooleanField(default=None, null=True)
    move_threads_perm = models.BooleanField(default=None, null=True)
    make_reactions_comments = models.BooleanField(default=None, null=True)
    make_reactions_post = models.BooleanField(default=None, null=True)
    make_profile_posts = models.BooleanField(default=None, null=True)
    delete_profile_posts = models.BooleanField(default=None, null=True)
    pin_posts_perm = models.BooleanField(default=None, null=True)
    unpin_posts_perm = models.BooleanField(default=None, null=True)
    add_badges_perm = models.BooleanField(default=None, null=True)
    modify_badges_perm = models.BooleanField(default=None, null=True)
    revoke_badges_perm = models.BooleanField(default=None, null=True)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, default='', unique=True)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=255, default='', unique=True)

    avatar = ContentTypeRestrictedFileField(content_types=['image/jpeg', 'image/png', 'image/gif'], max_upload_size=5242880, default='default.png', upload_to ='uploads/')
    background = ContentTypeRestrictedFileField(content_types=['image/jpeg', 'image/png', 'image/gif'] ,max_upload_size=5242880, default='default.png', upload_to ='uploads/')

    score = models.IntegerField(default=1)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    register = models.CharField(max_length=255, default='', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

        if self.avatar:
            file_path = str(BASE_DIR) + '/base/' + self.avatar.url
            avatar = im.open(file_path)
            avatar.thumbnail((300,300)) #avatar size 
            avatar.save(file_path)

        if self.background:
            file_path = str(BASE_DIR) + '/base/' + self.background.url
            background = im.open(file_path)
            background.thumbnail((300,300)) #background size
            background.save(file_path)


    def __str__(self):
        return self.name

class Badge(models.Model):
    badge_type = models.ForeignKey(BadgeType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_applied = models.DateTimeField(auto_now=True)
    badge_duration = models.DurationField(default=None, null=True) #0 for infinite duration

    class Meta:
        unique_together = ['badge_type', 'user']


class FrontStickyType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
class Topic(models.Model):
    name = models.CharField(max_length=200)
    parrent_topic = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    view_permisions = models.ManyToManyField(BadgeType, blank=True)
    banned_users_allowed = models.BooleanField(default=False)
    front_sticky = models.ForeignKey('FrontStickyType', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name

    def model_name(self):
        return self._meta.model_name

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    parrent_topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    content = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)

    view_permisions = models.ManyToManyField(BadgeType, blank=True)

    profile = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="profile")

    is_locked = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    front_sticky = models.ForeignKey('FrontStickyType', on_delete=models.SET_NULL, null=True, blank=True)

    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="deleted_by_post", null=True, default=None, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    previous = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None)
    has_new_version = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="edited_by", null=True, blank=True, default=None)


    def model_name(self):   
        return self._meta.model_name

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    content = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)

    previous = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None)
    has_new_version = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="edited_by_comment", null=True, blank=True, default=None)

    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="deleted_by", null=True, default=None, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:100]
    
    def model_name(self):   
        return self._meta.model_name

    class Meta:
        ordering = ['created']

class ReactionTypes(models.Model):
    image = models.ImageField(default='default.png', upload_to ='reaction_images/')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def reaction_types_gen():
        reaction_types = []
        reactions = ReactionTypes.objects.all()
        for reaction in reactions:
            reaction_types.append(reaction)

        return reaction_types

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)   

    reaction_type = models.ForeignKey(ReactionTypes, on_delete=models.CASCADE)

    def __str__(self):
        try:
            post = Post.objects.get(id=self.post.id)
            return post.name + " | " + ReactionTypes.objects.get(id=self.reaction_type.id).name + " reaction"
        except: 
            return Comment.objects.get(id=self.comment.id).content + " | " + ReactionTypes.objects.get(id=self.reaction_type.id).name + " reaction"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    seen = models.BooleanField(default=False)
    message = models.CharField(max_length=99999, null=True, blank=True)

    action_type = models.CharField(max_length=200)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    subscribed_object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="subscribed_object_type")
    subscribed_object_id = models.PositiveIntegerField()
    subscribed_object = GenericForeignKey('subscribed_object_type', 'subscribed_object_id')

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

        constraints = [
            UniqueConstraint(fields=['user', 'subscribed_object_type', 'subscribed_object_id', 'action_type'], condition=Q(seen=False), name='unique_field_a_field_b_validated')
        ]

class NotificationSubscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id' )
