from django.shortcuts import render, redirect
from .models import Post, ReactionTypes, NotificationSubscribe, Notification, Topic
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, PostForm, UserProfileForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .utils.utils import generate_token, password_reset_token
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.conf import settings 
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from itertools import chain
from django.contrib import messages
import math
from .utils.generatorsAndUtils import *
from .utils.context_generators import ContextGenerator
from django.contrib.contenttypes.models import ContentType


User = get_user_model()

def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = "Activation Email"
    context = {"user": user, 
                "domain": current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), 
                'token': generate_token.make_token(user)
                }
    email_body = render_to_string('email/activate.html',context)

    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_HOST_USER, to=[user.email])

    email.send()


def home(request):
    user = request.user
    topics = Topic.objects.filter(front_sticky__isnull=False)
    try: 
        badges = user.badges.all()
    except:
        badges = None

    posts = Post.objects.exclude(front_sticky__isnull=True)

    topics = TopicsGenerator(topics, badges)
    posts = RemoveDeletedIfNoPermisions(TopicsGenerator(posts, badges), badges)

    front_page_items = list(chain(topics, posts))

    front_page_dict = {}
    for front_page_item in front_page_items:
        if front_page_item.front_sticky in front_page_dict:
            front_page_dict[front_page_item.front_sticky].append(front_page_item)
        else: 
            front_page_dict[front_page_item.front_sticky] = [front_page_item]

    context = {"front_page_dict": front_page_dict}

    return render(request, 'base/home.html', context)

# ------------------ #
# -- /post/ stuff -- #
# ------------------ #

# ---- Functions --- #
            

# ---- Requests --- #
pag_amount = settings.PAG_AMOUNT
navbar_ammount = settings.NAV_BAR_AMOUNT
navbar_ammount_2 = settings.NAV_BAR_AMOUNT_2

#TODO Make it so all these checkers take badges instead of user so badges get called only once (EDIT MAY NOT BE NEEDED)


def post(request, pk):
    user = request.user
    post = Post.objects.get(id=pk)

    try:
        badges = user.badges.all()
    except:
        badges = None

    if not backendActionAuth(request, 'can-user-see-post', post):
        messages.info(request, 'You cant access this page')
        return redirect('home')

    context = ContextGenerator(locals(), comments_check=True, comment_reaction_check=True,
                               post_reaction_check=True, post_badge_check=True, comment_badge_check=True,
                               pag_comments_check=True, make_comment_check=True, comment_history_check=True,
                               edit_comments_check=True, delete_comments_check=True, edit_post_check=True,
                               lock_post_check=True, unlock_posts_check=True, post_history_check=True,
                               delete_post_check=True, move_threads_check=True)

    context = context | {"post": post}
    return render(request, 'base/post.html', context)

@ require_http_methods(['POST'])
def addComment(request, pk):
    post = Post.objects.get(id=pk)

    if backendActionAuth(request, 'make-comment', post):
        comment = Comment.objects.create(
            user=request.user, post=post, content=request.POST.get('content')
        )
        message = comment.content[:30]
        for notification in NotificationSubscribe.objects.filter(object_id=pk,content_type=ContentType.objects.get_for_model(post).id).exclude(user=request.user):
            try:
                Notification.objects.create(user=notification.user, content_object=comment, action_type="comment_on_subscribed_post", message=message, subscribed_object=post)
            except:
                pass

        try:
            NotificationSubscribe.objects.create(user=request.user, content_object=post)
        except:
            pass
        try:
            NotificationSubscribe.objects.create(
                user=request.user, content_object=comment,
            )
        except: 
            pass


    else:
        messages.info(request, "You are not allowed to add this comment")

    return redirect("post", pk)


@require_http_methods(['POST'])
def editContent(request, pk, sk):
    if sk == "comment":
        item = Comment.objects.get(id=pk)
        if backendActionAuth(request, 'edit-comment', item):
            user = request.user

            item2 = Comment.objects.get(id=pk)
            item2.pk = None

            item.has_new_version = True
            item.edited_by = request.user
            item.save()

            reactions = Reaction.objects.filter(comment=item)

            item2.previous = item
            item2.created = item.created
            item2.content = request.POST.get('editcontent')
            item2.save()

            for reaction in reactions:
                reaction.comment = item2
                reaction.save()

            try:
                badges = user.badges.all()
            except:
                badges = None

            comments = CommentListGenerator(user, Comment.objects.filter(post=item.post.id), badges)
            item_nr = list(comments).index(item2)
            index = math.ceil((item_nr + 1 )/pag_amount)
            id = item.post.id

            return redirect('/post/' + str(id) + "/?index=" + str(index) + "#" + str(item2.id))

    elif sk == "post":
        item = Post.objects.get(id=pk)
        if backendActionAuth(request, 'edit-post', item):

            item2 = Post.objects.get(id=pk)
            item.pk = None

            item.has_new_version = True
            item.edited_by = request.user
            item.save()

            reactions = Reaction.objects.filter(post=item)

            item2.previous = item
            item2.created = item.created
            item2.content = request.POST.get('editcontent')
            item2.save()

            for reaction in reactions:
                reaction.post = item2
                reaction.save()

            id = pk

        return redirect("post", id)

@require_http_methods(['POST'])
def addReaction(request, pk, sk, tk):
    user = request.user
    reaction_types = ReactionTypes.reaction_types_gen()
    if sk == "post":    
        post = Post.objects.get(id=pk)
        print(backendActionAuth(request, 'add-reaction-post', post))
        if backendActionAuth(request, 'add-reaction-post', post):

            reaction_type = ReactionTypes.objects.get(id=tk)
                
            reaction = Reaction.objects.create(
                user=user, post=post, reaction_type=reaction_type
            ) 
            for notification in NotificationSubscribe.objects.filter(object_id=pk,content_type=ContentType.objects.get_for_model(post).id).exclude(user=request.user):
                try:
                    Notification.objects.create(user=notification.user, content_object=reaction, action_type="reaction_on_subscribed_post", subscribed_object=post)
                except:
                    pass

        reactions_post_dict = reactionsPostGenerator(post)
        canUserReactPost = "reaction_in_place"


        context = {"reactions_post_dict": reactions_post_dict,"canUserReactPost": canUserReactPost, "reaction_types":reaction_types, "item": "post", "post": post, "canUserReactPost": canUserReactPost}
        return render(request, 'base/reactions_changable.html', context)   
    
    if sk == "comment":
        comment = Comment.objects.get(id=pk)
        if backendActionAuth(request, 'add-reaction-comment', comment):
            reaction_type = ReactionTypes.objects.get(id=tk)
                
            reaction = Reaction.objects.create(
                user=user, comment=comment, reaction_type=reaction_type
            )

            for notification in NotificationSubscribe.objects.filter(object_id=pk,content_type=ContentType.objects.get_for_model(comment).id).exclude(user=request.user):
                try:
                    Notification.objects.create(user=notification.user, content_object=reaction, action_type="reaction_on_subscribed_comment", subscribed_object=comment)
                except:
                    pass

            
        reactions_single_comment = singleReactionCommentGenerator(comment)
        canUserReactComment = False

        context = {"reactions_single_comment": reactions_single_comment, "canUserReactComment": canUserReactComment, "reaction_types":reaction_types, "item": "comment", "comment":comment}
        return render(request, 'base/reactions_changable.html', context)

@require_http_methods(['POST'])
def removeReaction(request, id, type):
    user = request.user
    
    reaction_types = ReactionTypes.reaction_types_gen()    
    if type == 'post':
        post = Post.objects.get(id=id)

        try: 
            reaction = Reaction.objects.get(post=post, user=user)
        except:
            return HttpResponse("")

        if backendActionAuth(request, 'remove-reaction', reaction):
            for notification in Notification.objects.filter(object_id=reaction.id, content_type=ContentType.objects.get_for_model(reaction).id, seen=False, action_type="reaction_on_subscribed_post"):
                notification.delete()

            reaction.delete()       

        
        reactions_post_dict = reactionsPostGenerator(post)
        canUserReactPost = canUserReactPostFunction(request, user, post)

        context = {"canUserReactPost": canUserReactPost, "reactions_post_dict": reactions_post_dict, "reaction_types": reaction_types, "item": "post", "post": post}

        return render(request, 'base/reactions_changable.html', context)
    
    if type == 'comment':
        comment = Comment.objects.get(id=id)

        try: 
            reaction = Reaction.objects.get(comment=comment, user=user)
        except:
            return HttpResponse("")

        if backendActionAuth(request, 'remove-reaction', reaction):
            for notification in Notification.objects.filter(object_id=reaction.id, content_type=ContentType.objects.get_for_model(reaction).id, seen=False, action_type="reaction_on_subscribed_comment"):
                notification.delete()

            reaction.delete()    

        reactions_single_comment = singleReactionCommentGenerator(comment)
        canUserReactComment = canUserReactSingleCommentFunction(user, comment)

        context = {"reactions_single_comment": reactions_single_comment, "canUserReactComment": canUserReactComment, "reaction_types":reaction_types, "item": "comment", "comment":comment}
        return render(request, 'base/reactions_changable.html', context)  

@require_http_methods(['GET'])
def moreComments(request, nr, post_id):
    user = request.user

    try:
        badges = user.badges.all()
    except:
        badges = None

    post = Post.objects.get(id=post_id)

    if not backendActionAuth(request, 'can-user-see-post', post):
        messages.info(request, 'You cant access this page')
        return redirect('home')

    context = ContextGenerator(locals(), comments_check=True, comment_reaction_check=True,
                               comment_badge_check=True, pag_comments_check=True,
                               make_comment_check=True, comment_history_check=True,
                               edit_comments_check=True, delete_comments_check=True,
                               )

    context = context | {"post": post}

    return render(request, 'base/comments.html', context)

@require_http_methods(['POST'])
def deleteComment(request, commentid):
    
    comment = Comment.objects.get(pk=commentid)

    if backendActionAuth(request, 'can-user-delete-comment', comment):
        comment.is_deleted = True
        comment.deleted_by = request.user
        comment.save()
        response = HttpResponse()
        response['HX-Redirect'] = "/post/" + str(comment.post.id) + "/"
        return response
    else:
        messages.info(request, 'You cant delete this comment')
        response = HttpResponse()
        response['HX-Redirect'] = ""
        return response

def deletePost(request, postid):
    post = Post.objects.get(pk=postid)

    if backendActionAuth(request, 'can-user-delete-post', post):
        post.is_deleted = True
        post.deleted_by = request.user
        post.save()
    else:
        messages.info(request, 'You cant delete this post')

    response = HttpResponse()
    response['HX-Redirect'] = ""

    return response
    

@require_http_methods(['POST'])
def lockPost(request, postid):
    
    try:
        post = Post.objects.get(id=postid)
    except:
        messages.info(request, "Post with the id of " + str(postid) + " does not exist")
        response = HttpResponse()
        response['HX-Redirect'] = ""
        
        return response
    
    if backendActionAuth(request, "can-user-lock-posts" ,post):
        post.is_locked = True
        post.save()

        response = HttpResponse()
        response['HX-Redirect'] = "/post/" + str(postid) + '/'
        return response
    else:
        messages.info(request, "You do not have permision to lock this post")


@require_http_methods(['POST'])
def unlockPost(request, postid):
    
    try:
        post = Post.objects.get(id=postid)
    except:
        messages.info(request, "Post with the id of " + str(postid) + " does not exist")
        response = HttpResponse()
        response['HX-Redirect'] = ""
        
        return response
    
    if backendActionAuth(request, "can-user-lock-posts" ,post):
        post.is_locked = False
        post.save()

        response = HttpResponse()
        response['HX-Redirect'] = "/post/" + str(postid) + '/'
        return response
    else:
        messages.info(request, "You do not have permision to unlock this post")

def editHistory(request, id, type):
    user = request.user

    try:
        badges = request.user.badges.all()
    except:
        badges = None

    if type == "comment":
        if backendActionAuth(request, 'can-user-see-comment-history', user):
            item_history = history_checker(Comment.objects.get(id=id))

            context = {"item_history": item_history}

            return render(request, 'base/comment_history.html', context)
        else:
            messages.error(request, "You do not have permisions to see the comment history")

    if type == "post":
        if backendActionAuth(request, 'can-user-see-post-history', user):
            item_history = history_checker(Post.objects.get(id=id))

            context = {"item_history": item_history}

            return render(request, 'base/comment_history.html', context)
        else:
            messages.error(request, "You do not have permisions to see the post history")


# ------------------------- #
# -- End of /post/ stuff -- #
# ------------------------- #

def browse(request, tk):
    if request.user.is_authenticated:
        canPost = True
    else:
        canPost = False

    try:
        badges = request.user.badges.all()
    except:
        badges = None

    try: 
        badges = request.user.badges.all()
    except:
        badges = None

    if tk == None or not BadgeTopicAndPostChecker(badges, Topic.objects.get(pk=tk)):
        messages.info(request, 'You cant acces this page')
        return redirect('home')

    posts = Post.objects.filter(parrent_topic=tk, is_pinned=False)
    topics = Topic.objects.filter(parrent_topic=tk)
    topics = TopicsGenerator(topics, badges)
    posts = RemoveDeletedIfNoPermisions(TopicsGenerator(posts, badges), badges)
    pinned_posts = RemoveDeletedIfNoPermisions(TopicsGenerator(Post.objects.filter(parrent_topic=tk, is_pinned=True), badges), badges)

    context = {"topics": topics, "posts": posts, "canPost": canPost, 't': tk, "pinned_posts": pinned_posts}

    return render(request, 'base/browse.html', context)

def register_user(request):
    page = "register"
    form = CustomUserCreationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_activation_email(user, request)
        return redirect('home')

            
    context = {"form": form, "page": page}

    return render(request, 'base/register_login.html', context)

def login_user(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = BaseUserManager.normalize_email(request.POST.get('email'))
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect('home')

    context = {"page": page}

    return render(request, 'base/register_login.html', context)

def logout_user(request):
    logout(request)
    return redirect('home')

def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    
    except:
        user = None
    
    if user and generate_token.check_token(user, token):
        user.is_verified=True
        user.save()

    return redirect('home')


@login_required(login_url='login')
def createPost(request, tk):
    form = PostForm()
    user = request.user

    try: 
        badges = user.badges.all()
    except:
        badges = None

    t = tk 
    
    if request.method == "POST":
        form = PostForm(request.POST)  
        if form.is_valid() and BadgeTopicAndPostChecker(badges, Topic.objects.get(id=tk)):
            post = form.save(commit=False)
            post.user = user
            post.parrent_topic = Topic.objects.get(id=t)
            post.save()
            NotificationSubscribe.objects.create(user=user, content_object=post)
            return redirect('post', post.id)
        else: 
            messages.error(request, "You are not allowed to post there or the value provided is wrong")

    context = {'form': form}
    return render(request, 'base/create_post.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)

    profile_posts = Post.objects.filter(profile=user).order_by('-created')

    if request.method == "POST":
        if 'make-profile-post' in request.POST:
            if backendActionAuth(request, 'make-profile-post', user):
                comment = Post.objects.create(
                    user=request.user, profile=user, content=request.POST.get('content'), name="Profile post"
                )
                if user != request.user:
                    try:
                        Notification.objects.create(user=user, content_object=comment, action_type="comment_on_profile_post",subscribed_object=user)
                    except:
                        pass
                
                return redirect('user-profile', pk)
            
    canUserMakeProfilePost = True
    if not request.user.is_authenticated:
        canUserMakeProfilePost = False

    
    context = { "user": user, 
    "canUserMakeProfilePost": canUserMakeProfilePost, "profile_posts": profile_posts}

    return render(request, 'base/profile.html', context)

def profileComments(request, userid, pagamount):
    comments = Comment.objects.filter(user=userid).order_by('-created')
    paginated_comments = Paginator(comments, 4)

    try:
        comments = paginated_comments.page(pagamount)
        try:
            test = paginated_comments.page(pagamount + 1)
            last = False
        except:
            last = True
    except:
        comments = None

    comments_pag_value = pagamount+1

    context = {"comments": comments, "comments_pag_value": comments_pag_value, "last": last}

    return render(request, 'base/profile_comments.html', context)


def profilePosts(request, userid, pagamount):
    posts = Post.objects.filter(user=userid).order_by('-created')
    paginated_posts = Paginator(posts, 4)
    try:
        posts = paginated_posts.page(pagamount)
        try:
            test = paginated_posts.page(pagamount + 1)
            last = False
        except:
            last = True
    except:
        posts = None

    posts_pag_value = pagamount+1

    context = {"posts": posts, "posts_pag_value": posts_pag_value, "last": last}

    return render(request, 'base/profile_posts.html', context)

def profileActivity(request, userid, pagamount):
    posts_n_comments = sorted(chain(Post.objects.filter(user=userid), Comment.objects.filter(user=userid)), key=lambda item: item.created, reverse=True)
    paginated_posts_posts_n_commentes = Paginator(posts_n_comments, 4)

    try:
        posts_n_comments = paginated_posts_posts_n_commentes.page(pagamount)
        try:
            test = paginated_posts_posts_n_commentes.page(pagamount + 1)
            last = False
        except:
            last = True 
    except:
        posts_n_comments = None
    
    activity_pag_value = pagamount+1

    context = {"posts_n_comments": posts_n_comments, "activity_pag_value": activity_pag_value, "last": last}

    return render(request, 'base/profile_activity.html', context)

def userSettings(request):
    form = UserProfileForm(instance=request.user)

    if request.method == 'POST': 
        if 'user-settings-save' in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                if backendActionAuth(request, 'user-settings-save', form):
                    form.save()
                    return redirect('user-profile', request.user.id)



    context = {'form': form}

    return render(request, 'base/settings.html', context)

def checkHTMX(request, pk):
    if pk == 'name':
        try:
            User.objects.get(name=request.POST.get('name'))
            return HttpResponse("<p style='color: red;'>This username already exists</p>")
        except:
            return HttpResponse("This username is avalible")
    elif pk == 'email':
        try:
            User.objects.get(email=request.POST.get('email'))
            return HttpResponse("<p style='color: red'>This email already exists</p>")
        except:
            return HttpResponse("This email is avalible")

def notifications(request):
    user = request.user

    index = int(request.GET.get("index")) if request.GET.get('index') != None else 1

    try:
        notifications_pre = Notification.objects.filter(user=user)
        paginated_notifications = Paginator(notifications_pre, 4)
        notifications = paginated_notifications.page(index)
    except:
        notifications = None

    try:
        notifications_unseen = len(Notification.objects.filter(user=user, seen=False))
    except:
        notifications_unseen = None

    context = {"notifications":notifications, "notifications_unseen": notifications_unseen, "index": index}

    return render(request, 'base/notification_inner.html', context)

def notificationSeen(request, notificationid):
    user = request.user
    try:
        notification = Notification.objects.get(id=notificationid)
    except:
        notification = None
    
    if backendActionAuth(request, "can-user-see-notifications",notification):
        notification.seen = True
        notification.save()

    action_type = notification.action_type

    if action_type == "comment_on_subscribed_post" or action_type == "reaction_on_subscribed_post":
        url = reverse("post", args=[notification.content_object.post.id])
    elif action_type == "reaction_on_subscribed_comment":
        url = reverse('post', args=[notification.content_object.comment.post.id])
    elif action_type == "comment_on_profile_post":
        url = reverse("user-profile", args=[notification.content_object.profile.id])


    response = HttpResponse()
    response['HX-Redirect'] = url

    return response

def sendResetPassword(request):
    if request.method=="POST":
        email = request.POST['email']
        try: 
            user = User.objects.get(email=email)
        except: 
            messages.error(request, "this email does not exist")
            return redirect('send-reset-password')

        current_site = get_current_site(request)
        email_subject = "Password recovery"
        context = {
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": password_reset_token.make_token(user),
        }

        email_body = render_to_string('email/reset_password.html', context)

        email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_HOST_USER, to=[email])
    
        email.send()

        messages.info(request, "You have been sent a reset password in the mail, please check it and click the link")
        return redirect('home')

    if request.method=="GET":
        return render(request, 'base/register_login.html', {'page': 'reset_pre_mail'})

def checkResetToken(request, uid64, token):
    if request.method=="POST":
        try: 
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)

        except: 
            messages.error(request, "No such user with the UID that was provided, if you get this erorr report it to a administrator")
            redirect("home")
        
        if password_reset_token.check_token(user, token):
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            if password1 == password2:
                login(request, user)
                user.set_password(password1)
                user.save()
                messages.info(request, "Password succesfully reset")
                return redirect('home')
            else:
                messages.error("Passwords dont match")
                return redirect(reverse('reset-password', uid64, token))
        else: 
            messages.error(request, "Token check failed (most likely due to expired token)")
            return redirect('home')
            
    elif request.method=="GET":
        return render(request, "base/register_login.html", {'page':'reset_post_mail', 'uid': uid64, 'token':token})

def moveThread(request,post,topic):
    if request.method == "POST":
        if backendActionAuth(request, 'can-user-move-thread', None):
           post = Post.objects.get(id=post)
           topic = Topic.objects.get(id=topic)
           
           post.parrent_topic = topic 
           post.save()

        else:
           messages.error(request, "You are not allowed to move threads")

        return HttpResponse('')

def getTopics(request, post):

    try: 
        badges = request.user.badges.all()
    except:
        badges = None

    topics = TopicsGenerator(Topic.objects.filter(parrent_topic__isnull=True), badges)
    topics = topicDictGenerator(topics)
    
    context = {'topics': topics, 'post': post}

    return render(request, 'base/move_topics.html', context)