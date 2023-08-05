from django.shortcuts import render, redirect
from .models import Post, NotificationSubscribe, Notification, Badge, BadgeType
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, PostForm, UserProfileForm, BadgeAddForm
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
import datetime
from .messages import *

User = get_user_model()


def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = "Activation Email"
    context = {"user": user,
               "domain": current_site,
               'uid': urlsafe_base64_encode(force_bytes(user.pk)),
               'token': generate_token.make_token(user)
               }
    email_body = render_to_string('email/activate.html', context)

    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_HOST_USER, to=[user.email])

    email.send()


def home(request):
    user = request.user
    topics = Topic.objects.filter(front_sticky__isnull=False)
    try:
        user_badge_types = user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
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

# ---- Requests --- #
pag_amount = settings.PAG_AMOUNT


# TODO Make it so all these checkers take badges instead of user so badges get called only once (EDIT MAY NOT BE NEEDED)


def post(request, pk):
    user = request.user

    try:
        post = Post.objects.get(id=pk)
    except:
        messages.info(request, ERR_POSTEXIST_NULL % pk)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    try:
        user_badge_types = user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    if not backendActionAuth(request, 'can-user-see-post', post) or post.profile_id:
        messages.error(request, ERR_POSTVIEW_NOPERM % user.name)
        return redirect('home')

    context = ContextGenerator(locals(), comments_check=True, comment_reaction_check=True,
                               post_reaction_check=True, post_badge_check=True, comment_badge_check=True,
                               pag_comments_check=True, make_comment_check=True, comment_history_check=True,
                               edit_comments_check=True, delete_comments_check=True, edit_post_check=True,
                               lock_post_check=True, unlock_posts_check=True, post_history_check=True,
                               delete_post_check=True, move_threads_check=True, pin_posts_check=True,
                               unpin_posts_check=True)

    context = context | {"post": post}
    return render(request, 'base/post.html', context)


@require_http_methods(['POST'])
def addComment(request, pk):
    try:
        post = Post.objects.get(id=pk)
    except:
        messages.info(request, ERR_POSTEXIST_NULL % pk)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    if backendActionAuth(request, 'make-comment', post):
        comment = Comment.objects.create(
            user=request.user, post=post, content=request.POST.get('content')
        )
        message = comment.content[:30]
        for notification in NotificationSubscribe.objects.filter(object_id=pk,
                                                                 content_type=ContentType.objects.get_for_model(
                                                                         post).id).exclude(user=request.user):
            try:
                Notification.objects.create(user=notification.user, content_object=comment,
                                            action_type="comment_on_subscribed_post", message=message,
                                            subscribed_object=post)
            except:
                pass

        try:
            NotificationSubscribe.objects.create(user=request.user, content_object=post)
        except:
            pass
        try:
            NotificationSubscribe.objects.create(user=request.user, content_object=comment, )
        except:
            pass

        messages.success(request, SUC_COMADD_ACCEPT % post.name)
    else:
        messages.error(request, ERR_COMADD_NOPERM % post.name)

    # TODO Make is so it redirect to the comment made not just the post
    # TODO ^ is already done somwhere else in the code
    return redirect("post", pk)


@require_http_methods(['POST'])
def editContent(request, pk, sk):
    if sk == "comment":
        try:
            item = Comment.objects.get(pk=pk)
        except:
            messages.info(request, ERR_COMEXIST_NULL % pk)
            response = HttpResponse()
            response['HX-Redirect'] = ""

            return response

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
                user_badge_types = user.badge_set.values_list('badge_type')
                badges = BadgeType.objects.filter(pk__in=user_badge_types)
            except:
                badges = None

            comments = CommentListGenerator(user, Comment.objects.filter(post=item.post.id), badges)
            item_nr = list(comments).index(item2)
            index = math.ceil((item_nr + 1) / pag_amount)
            id = item.post.id

            messages.success(request, SUC_COMEDIT_ACCEPT)
            return redirect('/post/' + str(id) + "/?index=" + str(index) + "#" + str(item2.id))
        else:
            messages.error(request, ERR_COMEDIT_NOPERM % item.content[:15])
            return redirect('/post/' + str(item.post.id) + "/")

    elif sk == "post":

        try:
            item = Post.objects.get(id=pk)
        except:
            messages.info(request, ERR_POSTEXIST_NULL % pk)
            response = HttpResponse()
            response['HX-Redirect'] = ""

            return response

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

            messages.success(request, SUC_POSTEDIT_ACCEPT)
        else:
            messages.error(request, ERR_POSTEDIT_NOPERM % item.name)

        return redirect("post", pk)


@require_http_methods(['POST'])
def addReaction(request, pk, sk, tk):
    user = request.user
    reaction_types = reaction_types_gen()
    if sk == "post":
        try:
            post = Post.objects.get(id=pk)
        except:
            messages.info(request, ERR_POSTEXIST_NULL % pk)
            response = HttpResponse()
            response['HX-Redirect'] = ""

            return response

        if backendActionAuth(request, 'add-reaction-post', post):

            reaction_type = ReactionTypes.objects.get(id=tk)

            reaction = Reaction.objects.create(
                user=user, post=post, reaction_type=reaction_type
            )
            for notification in NotificationSubscribe.objects.filter(object_id=pk,
                                                                     content_type=ContentType.objects.get_for_model(
                                                                             post).id).exclude(user=request.user):
                try:
                    Notification.objects.create(user=notification.user, content_object=reaction,
                                                action_type="reaction_on_subscribed_post", subscribed_object=post)
                except:
                    pass

            messages.success(request, SUC_REACTADDPOST_ACCEPT)
            canUserReactPost = "reaction_in_place"

        else:
            # User cannot react, no need to redirect them to another page,
            # just remove their reaction check and notify them about the error
            messages.error(request, ERR_REACTADDPOST_NOPERM)
            canUserReactPost = False

        reactions_post_dict = reactionsPostGenerator(post)
        context = {"reactions_post_dict": reactions_post_dict,
                   "reaction_types": reaction_types, "item": "post", "post": post,
                   "canUserReactPost": canUserReactPost}

        return render(request, 'base/reactions_changable.html', context)

    if sk == "comment":
        try:
            comment = Comment.objects.get(pk=pk)
        except:
            messages.info(request, ERR_COMEXIST_NULL % pk)
            response = HttpResponse()
            response['HX-Redirect'] = ""

            return response

        if backendActionAuth(request, 'add-reaction-comment', comment):
            reaction_type = ReactionTypes.objects.get(id=tk)

            reaction = Reaction.objects.create(
                user=user, comment=comment, reaction_type=reaction_type
            )

            for notification in NotificationSubscribe.objects.filter(object_id=pk,
                                                                     content_type=ContentType.objects.get_for_model(
                                                                             comment).id).exclude(user=request.user):
                try:
                    Notification.objects.create(user=notification.user, content_object=reaction,
                                                action_type="reaction_on_subscribed_comment", subscribed_object=comment)
                except:
                    pass

            messages.success(request, SUC_REACTADDCOM_ACCEPT)
        else:
            messages.success(request, ERR_REACTADDCOM_NOPERM % comment.content[:15])

        reactions_single_comment = singleReactionCommentGenerator(comment)
        canUserReactComment = canUserReactSingleCommentFunction(user, comment)

        context = {"reactions_single_comment": reactions_single_comment, "canUserReactComment": canUserReactComment,
                   "reaction_types": reaction_types, "item": "comment", "comment": comment}

        return render(request, 'base/reactions_changable.html', context)


@require_http_methods(['POST'])
def removeReaction(request, id, type):
    user = request.user

    reaction_types = reaction_types_gen()
    if type == 'post':
        try:
            post = Post.objects.get(id=id)
        except:
            messages.info(request, ERR_POSTEXIST_NULL % id)
            response = HttpResponse()
            response['HX-Redirect'] = ""

            return response

        try:
            reaction = Reaction.objects.get(post=post, user=user)
        except:
            return HttpResponse("")

        if backendActionAuth(request, 'remove-reaction-post', reaction):
            for notification in Notification.objects.filter(object_id=reaction.id,
                                                            content_type=ContentType.objects.get_for_model(reaction).id,
                                                            seen=False, action_type="reaction_on_subscribed_post"):
                notification.delete()

            reaction.delete()
            messages.success(request, SUC_REACTDELPOST_ACCEPT)
        else:
            messages.success(request, ERR_REACTDELPOST_NOPERM % post.name)

        reactions_post_dict = reactionsPostGenerator(post)
        canUserReactPost = canUserReactPostFunction(request, user, post)

        context = {"canUserReactPost": canUserReactPost, "reactions_post_dict": reactions_post_dict,
                   "reaction_types": reaction_types, "item": "post", "post": post}

        return render(request, 'base/reactions_changable.html', context)

    if type == 'comment':
        comment = Comment.objects.get(id=id)

        try:
            reaction = Reaction.objects.get(comment=comment, user=user)
        except:
            return HttpResponse("")

        if backendActionAuth(request, 'remove-reaction-comment', reaction):
            for notification in Notification.objects.filter(object_id=reaction.id,
                                                            content_type=ContentType.objects.get_for_model(reaction).id,
                                                            seen=False, action_type="reaction_on_subscribed_comment"):
                notification.delete()
            reaction.delete()
            messages.success(request, SUC_REACTDELCOM_ACCEPT)
        else:
            messages.error(request, ERR_REACTDELCOM_NOPERM % comment.content[:15])

        reactions_single_comment = singleReactionCommentGenerator(comment)
        canUserReactComment = canUserReactSingleCommentFunction(user, comment)

        context = {"reactions_single_comment": reactions_single_comment, "canUserReactComment": canUserReactComment,
                   "reaction_types": reaction_types, "item": "comment", "comment": comment}
        return render(request, 'base/reactions_changable.html', context)


@require_http_methods(['GET'])
def moreComments(request, nr, postid):
    user = request.user

    try:
        user_badge_types = user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    try:
        post = Post.objects.get(id=postid)
    except:
        messages.info(request, ERR_POSTEXIST_NULL % postid)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    if backendActionAuth(request, 'can-user-see-post', post):
        context = ContextGenerator(locals(), comments_check=True, comment_reaction_check=True,
                                   comment_badge_check=True, pag_comments_check=True,
                                   make_comment_check=True, comment_history_check=True,
                                   edit_comments_check=True, delete_comments_check=True,
                                   )

        context = context | {"post": post}

        return render(request, 'base/comments.html', context)
    else:
        # This shouldn't happen
        messages.error(request, ERR_MORECOMVIEW_NOPERM)
        return HttpResponse("")


@require_http_methods(['POST'])
def deleteComment(request, commentid):
    try:
        comment = Comment.objects.get(pk=commentid)
    except:
        messages.info(request, ERR_COMEXIST_NULL % commentid)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    if backendActionAuth(request, 'can-user-delete-comment', comment):
        comment.is_deleted = True
        comment.deleted_by = request.user
        comment.save()

        messages.success(request, SUC_COMDEL_ACCEPT)

        response = HttpResponse()
        response['HX-Redirect'] = "/post/" + str(comment.post.id) + "/"
        return response
    else:
        messages.info(request, ERR_COMDEL_NOPERM % comment.content[:15])
        response = HttpResponse()
        response['HX-Redirect'] = "/post/" + str(comment.post.id) + "/"
        return response


def deletePost(request, postid):
    try:
        post = Post.objects.get(id=postid)
    except:
        messages.info(request, ERR_POSTEXIST_NULL % postid)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    if backendActionAuth(request, 'can-user-delete-post', post):
        post.is_deleted = True
        post.deleted_by = request.user
        post.save()

        messages.success(request, SUC_POSTDEL_ACCEPT % post.name)
    else:
        messages.error(request, ERR_POSTDEL_NOPERM % post.name)

    response = HttpResponse()
    response['HX-Redirect'] = "/post/" + str(post.id) + "/"

    return response


@require_http_methods(['POST'])
def lockPost(request, postid):
    try:
        post = Post.objects.get(id=postid)
    except:
        messages.info(request, ERR_POSTEXIST_NULL % postid)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    if backendActionAuth(request, "can-user-lock-posts", post):
        post.is_locked = True
        post.save()

        messages.success(request, SUC_POSTLOCK_ACCEPT)

        response = HttpResponse()
        response['HX-Redirect'] = "/post/" + str(postid) + '/'
        return response
    else:
        messages.error(request, ERR_POSTLOCK_NOPERM)


def postPining(request, type, postid):
    try:
        post = Post.objects.get(id=postid)
    except:
        messages.info(request, ERR_POSTEXIST_NULL % postid)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    if type == "pin":
        if backendActionAuth(request, "can-user-pin-posts", post):
            post.is_pinned = True
            post.save()

            messages.success(request, SUC_POSTPIN_ACCEPT)

            response = HttpResponse()
            response['HX-Redirect'] = "/post/" + str(postid) + '/'
            return response
        else:
            messages.error(request, ERR_POSTPIN_NOPERM)

    elif type == "unpin":
        if backendActionAuth(request, "can-user-unpin-posts", post):
            post.is_pinned = False
            post.save()

            messages.success(request, SUC_POSTUPIN_ACCEPT)

            response = HttpResponse()
            response['HX-Redirect'] = "/post/" + str(postid) + '/'
            return response
        else:
            messages.error(request, ERR_POSTUPIN_NOPERM)

    else:
        messages.error(request, ERR_INVALIDREQ % 1)

    response = HttpResponse()
    response['HX-Redirect'] = "/post/" + str(postid) + '/'

    return response


@require_http_methods(['POST'])
def unlockPost(request, postid):
    try:
        post = Post.objects.get(id=postid)
    except:
        messages.info(request, ERR_POSTEXIST_NULL % postid)
        response = HttpResponse()
        response['HX-Redirect'] = ""

        return response

    if backendActionAuth(request, "can-user-unlock-posts", post):
        post.is_locked = False
        post.save()

        messages.success(request, SUC_POSTULOCK_ACCEPT)

        response = HttpResponse()
        response['HX-Redirect'] = "/post/" + str(postid) + '/'
        return response
    else:
        messages.error(request, ERR_POSTULOCK_NOPERM)


def editHistory(request, id, type):
    user = request.user

    if type == "comment":
        if backendActionAuth(request, 'can-user-see-comment-history', user):
            item_history = history_checker(Comment.objects.get(id=id))

            context = {"item_history": item_history}

            return render(request, 'base/comment_history.html', context)
        else:
            messages.error(request, ERR_COMHIST_NOPERM)

    if type == "post":
        if backendActionAuth(request, 'can-user-see-post-history', user):
            item_history = history_checker(Post.objects.get(id=id))

            context = {"item_history": item_history}

            return render(request, 'base/comment_history.html', context)
        else:
            messages.error(request, ERR_POSTHIST_NOPERM)


# ------------------------- #
# -- End of /post/ stuff -- #
# ------------------------- #

def browse(request, tk):
    topic = Topic.objects.get(pk=tk)
    try:
        user_badge_types = request.user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    if tk == None or not BadgeTopicAndPostChecker(badges, topic):
        messages.info(request, ERR_BROWSE_NOPERM)
        return redirect('home')

    posts = Post.objects.filter(parrent_topic=tk, is_pinned=False)
    topics = Topic.objects.filter(parrent_topic=tk)
    topics = TopicsGenerator(topics, badges)
    posts = RemoveDeletedIfNoPermisions(TopicsGenerator(posts, badges), badges)
    pinned_posts = RemoveDeletedIfNoPermisions(
        TopicsGenerator(Post.objects.filter(parrent_topic=tk, is_pinned=True), badges), badges)

    index = int(request.GET.get("index")) if request.GET.get('index') != None else 1

    paginated_posts = Paginator(posts, settings.POST_PAG_AMOUNT)
    page_count = range(paginated_posts.num_pages)

    try:
        posts = paginated_posts.page(index)
    except:
        posts = paginated_posts.page(page_count[-1])

    pag_next = posts.has_next()
    pag_previous = posts.has_previous()

    front_range = range(settings.NAV_BAR_AMOUNT)

    if index - settings.NAV_BAR_AMOUNT_2 - 1 < 1:
        m1 = settings.NAV_BAR_AMOUNT_2  # to make it odd
    else:
        m1 = index - settings.NAV_BAR_AMOUNT_2 - 1

    if index + settings.NAV_BAR_AMOUNT_2 > paginated_posts.num_pages:
        m2 = paginated_posts.num_pages
    else:
        m2 = index + settings.NAV_BAR_AMOUNT_2

    middle_range = range(m1, m2)
    back_range = range(paginated_posts.num_pages - settings.NAV_BAR_AMOUNT, paginated_posts.num_pages)

    indentation_range = chainNoOverlap(front_range, middle_range, back_range)
    canPost = backendActionAuth(request, "can-user-make-post", topic)

    context = {"topics": topics, "canPost": canPost, 't': tk,
               "pinned_posts": pinned_posts, "indentation_range": indentation_range,
               "pag_previous": pag_previous, "pag_next": pag_next,
               "page_count": page_count, "posts": posts, "curent_page": index}

    return render(request, 'base/browse.html', context)


def morePosts(request, nr, topicid):
    try:
        user_badge_types = request.user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    posts = Post.objects.filter(parrent_topic=topicid, is_pinned=False)

    posts = RemoveDeletedIfNoPermisions(TopicsGenerator(posts, badges), badges)

    paginated_posts = Paginator(posts, settings.POST_PAG_AMOUNT)
    page_count = range(paginated_posts.num_pages)

    # nr is the page index, if it's over the max it defaults to the max as a fail safe
    try:
        posts = paginated_posts.page(nr)
    except:
        posts = paginated_posts.page(page_count[-1])
        messages.warning(request, WAR_MPOST_INDEXOF)

    pag_next = posts.has_next()
    pag_previous = posts.has_previous()

    front_range = range(settings.NAV_BAR_AMOUNT)

    if nr - settings.NAV_BAR_AMOUNT_2 - 1 < 1:
        m1 = settings.NAV_BAR_AMOUNT_2  # to make it odd
    else:
        m1 = nr - settings.NAV_BAR_AMOUNT_2 - 1

    if nr + settings.NAV_BAR_AMOUNT_2 > paginated_posts.num_pages:
        m2 = paginated_posts.num_pages
    else:
        m2 = nr + settings.NAV_BAR_AMOUNT_2

    middle_range = range(m1, m2)
    back_range = range(paginated_posts.num_pages - settings.NAV_BAR_AMOUNT, paginated_posts.num_pages)

    indentation_range = chainNoOverlap(front_range, middle_range, back_range)

    context = {"indentation_range": indentation_range, "pag_previous": pag_previous, "pag_next": pag_next,
               "posts": posts, "curent_page": nr, "page_count": page_count, 't': topicid}

    return render(request, 'base/browse_posts.html', context)


def register_user(request):
    page = "register"
    form = CustomUserCreationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            # The reason for the try>except block is due to the fact that
            # the email activation may be not sent due to external factors outside of the code

            try:
                send_activation_email(user, request)
                messages.info(request, SUC_EMAIlSEND_ACCEPT)
            except:
                messages.error(request, ERR_EMAILSEND_EMAILERROR)
        else:
            messages.error(request, ERR_EMAILSEND_INVFORM)

        return redirect('home')

    context = {"form": form, "page": page}

    return render(request, 'base/register_login.html', context)


def login_user(request):
    page = "login"

    if request.user.is_authenticated:
        messages.error(request, INFO_LOGIN_ALREADYLOGEDIN)
        return redirect('home')

    if request.method == "POST":
        email = BaseUserManager.normalize_email(request.POST.get('email'))
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            messages.info(request, SUC_LOGIN_ACCEPT)
            return redirect('home')

        messages.error(request, ERR_LOGINCRED_INVCREDENTIALS)

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
        messages.error(request, ERR_ACTUSER_INVUUID)
        return redirect('home')

    if generate_token.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, SUC_ACTUSER_ACCEPT)
    else:
        messages.error(request, ERR_ACTUSER_INVTOKEN)

    return redirect('home')


@login_required(login_url='login')
def createPost(request, tk):
    form = PostForm()
    user = request.user

    try:
        user_badge_types = user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    t = tk

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid() and backendActionAuth(request, 'can-user-make-post', Topic.objects.get(id=tk)):
            post = form.save(commit=False)
            post.user = user
            post.parrent_topic = Topic.objects.get(id=t)
            post.save()
            NotificationSubscribe.objects.create(user=user, content_object=post)
            messages.success(request, SUC_POSTADD_ACCEPT)
            return redirect('post', post.id)
        else:
            messages.error(request, ERR_POSTADD_NOPERM)

    context = {'form': form}
    return render(request, 'base/create_post.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)

    try:
        user_badge_types = user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    # This is temporary make a special case for this, and make it paginated
    profile_posts = RemoveDeletedIfNoPermisions(Post.objects.filter(profile=user).order_by('-created'), badges)

    if request.method == "POST":
        if 'make-profile-post' in request.POST:
            if backendActionAuth(request, 'make-profile-post', user):
                comment = Post.objects.create(
                    user=request.user, profile=user, content=request.POST.get('content'), name="Profile post"
                )
                if user != request.user:
                    try:
                        Notification.objects.create(user=user, content_object=comment,
                                                    action_type="comment_on_profile_post", subscribed_object=user)
                    except:
                        pass

                messages.success(request, SUC_PRFADD_ACCEPT)
            else:
                messages.error(request, ERR_PRFADD_NOPERM)

            return redirect('user-profile', pk)

    canUserMakeProfilePost = backendActionAuth(request, "make-profile-post", None)
    canUserDeleteProfilePosts = canUserDeleteProfilePostsGenerator(request, profile_posts)
    canUserAddBadge = backendActionAuth(request, "can-user-add-badge", None)
    canUserModifyBadge = backendActionAuth(request, "can-user-modify-badge", None) and badges
    canUserRevokeBadge = backendActionAuth(request, "can-user-revoke-badge", None) and badges

    badge_dict = {}
    for badge in Badge.objects.filter(user=user):
        badge_dict[badge.id] = badge.badge_type

    context = {"user": user,
               "canUserMakeProfilePost": canUserMakeProfilePost, "profile_posts": profile_posts,
               "canUserDeleteProfilePosts": canUserDeleteProfilePosts, "canUserRevokeBadge": canUserRevokeBadge,
               "canUserModifyBadge": canUserModifyBadge, "canUserAddBadge": canUserAddBadge, "badge_dict": badge_dict
               }

    return render(request, 'base/profile.html', context)


def profileComments(request, userid, pagamount):
    comments = Comment.objects.filter(user=userid).order_by('-created')
    paginated_comments = Paginator(comments, 4)

    try:
        comments = paginated_comments.page(pagamount)
        last = not paginated_comments.has_next()
    except:
        last = True
        comments = None

    comments_pag_value = pagamount + 1

    context = {"comments": comments, "comments_pag_value": comments_pag_value, "last": last}

    return render(request, 'base/profile_comments.html', context)


def profilePosts(request, userid, pagamount):
    posts = Post.objects.filter(user=userid).order_by('-created')
    paginated_posts = Paginator(posts, 4)
    try:
        posts = paginated_posts.page(pagamount)
        last = not paginated_posts.has_next()
    except:
        last = True
        posts = None

    posts_pag_value = pagamount + 1

    context = {"posts": posts, "posts_pag_value": posts_pag_value, "last": last}

    return render(request, 'base/profile_posts.html', context)


def profileActivity(request, userid, pagamount):
    posts_n_comments = sorted(chain(Post.objects.filter(user=userid), Comment.objects.filter(user=userid)),
                              key=lambda item: item.created, reverse=True)
    paginated_posts_posts_n_comments = Paginator(posts_n_comments, 4)

    try:
        posts_n_comments = paginated_posts_posts_n_comments.page(pagamount)
        last = paginated_posts_posts_n_comments.has_next()
    except:
        last = True
        posts_n_comments = None

    activity_pag_value = pagamount + 1

    context = {"posts_n_comments": posts_n_comments, "activity_pag_value": activity_pag_value, "last": last}

    return render(request, 'base/profile_activity.html', context)


def userSettings(request):
    form = UserProfileForm(instance=request.user)

    if request.method == 'POST':
        if 'user-settings-save' in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid() and backendActionAuth(request, 'user-settings-save', form):
                form.save()
                messages.success(request, SUC_USERSET_ACCEPT)
            else:
                messages.error(request, ERR_USERSET_NOPERMORINVFORM)

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

    context = {"notifications": notifications, "notifications_unseen": notifications_unseen, "index": index}

    return render(request, 'base/notification_inner.html', context)


def notificationSeen(request, notificationid):
    user = request.user
    try:
        notification = Notification.objects.get(id=notificationid)
    except:
        notification = None

    if backendActionAuth(request, "can-user-see-notifications", notification):
        notification.seen = True
        notification.save()

    action_type = notification.action_type

    if action_type == "comment_on_subscribed_post" or action_type == "reaction_on_subscribed_post":
        url = reverse("post", args=[notification.content_object.post.id])
    elif action_type == "reaction_on_subscribed_comment":
        url = reverse('post', args=[notification.content_object.comment.post.id])
    elif action_type == "comment_on_profile_post":
        url = reverse("user-profile", args=[notification.content_object.profile.id])
    else:
        url = ""
        messages.error(request, ERR_NOTSEEN_INVACTION)

    response = HttpResponse()
    response['HX-Redirect'] = url

    return response


def sendResetPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, ERR_PASSRES_NOEMAIl % email)
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

        messages.info(request, SUC_EMAIlSEND_ACCEPT)
        return redirect('home')

    if request.method == "GET":
        return render(request, 'base/register_login.html', {'page': 'reset_pre_mail'})


def checkResetToken(request, uid64, token):
    if request.method == "POST":
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except:
            messages.error(request, ERR_RESTOK_INVALIDUID)
            return redirect("home")

        if password_reset_token.check_token(user, token):
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            if password1 == password2:
                login(request, user)
                user.set_password(password1)
                user.save()
                messages.success(request, SUC_RESTOK_ACCEPT)
                return redirect('home')
            else:
                messages.error(request, ERR_RESTOK_MISSMATCH)
                return redirect(reverse('reset-password', uid64, token))
        else:
            messages.error(request, ERR_RESTOK_DENY)
            return redirect('home')

    elif request.method == "GET":
        return render(request, "base/register_login.html", {'page': 'reset_post_mail', 'uid': uid64, 'token': token})


def moveThread(request, post, topic):
    if backendActionAuth(request, 'can-user-move-thread', None):
        post = Post.objects.get(id=post)
        topic = Topic.objects.get(id=topic)

        post.parrent_topic = topic
        post.save()
        messages.success(request, SUC_MVTREAD_ACCEPT)
    else:
        messages.error(request, ERR_MVTREAD_NOPERM)

    response = HttpResponse()
    response['HX-Redirect'] = "/post/" + str(post.id) + "/"
    return response


def getTopics(request, post):
    try:
        user_badge_types = request.user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    topics = TopicsGenerator(Topic.objects.filter(parrent_topic__isnull=True), badges)
    topics = topicDictGenerator(topics)

    context = {'topics': topics, 'post': post}

    return render(request, 'base/move_topics.html', context)


def deleteProfilePost(request, postid):
    # This is temporary make a special case for all of this, including pagnation
    post = Post.objects.get(id=postid)
    if backendActionAuth(request, "delete-profile-posts", post):
        post.is_deleted = True
        post.deleted_by = request.user
        post.save()
        messages.success(request, SUC_PRFDEL_ACCEPT)
    else:
        messages.error(request, ERR_PRFDEL_NOPERM)

    response = HttpResponse()
    response['HX-Redirect'] = "/profile/" + str(post.profile.id) + "/"
    return response


def addbadge(request, userid):
    user = User.objects.get(id=userid)
    form = BadgeAddForm(user, request.POST)
    if request.method == "POST":
        if backendActionAuth(request, "can-user-add-badge", None) and form.is_valid():
            import datetime
            cd = form.cleaned_data
            Badge.objects.create(
                user=user,
                badge_type=BadgeType.objects.get(id=cd["badge_type"]),
                badge_duration=datetime.timedelta(seconds=cd["badge_duration"]),
            )
            messages.info(request, SUC_BAGADD_ACCEPT)
        else:
            messages.error(request, ERR_BAGADD_NOPERMORINVFORM)

        return redirect('user-profile', userid)

    elif request.method == "GET":
        context = {"form": form, "page": "add"}
        return render(request, "base/badge_mod.html", context)


def revokebadge(request, userid, badgeid):
    if backendActionAuth(request, "can-user-revoke-badge", None):
        badge = Badge.objects.get(id=badgeid)
        badge.delete()
        messages.info(request, SUC_BAGDEL_ACCEPT)
        return HttpResponse("")
    else:
        messages.error(request, ERR_BAGDEL_NOPERM)
        response = HttpResponse()
        response['HX-Redirect'] = "/profile/" + userid + "/"
        return response


def modifybadge(request, badgeid):
    badge = Badge.objects.get(id=badgeid)
    user = badge.user.id
    if request.method == "POST":
        form = BadgeAddForm(user, request.POST)
        if backendActionAuth(request, "can-user-modify-badge", None) and form.is_valid():
            cd = form.cleaned_data
            badge.badge_type = BadgeType.objects.get(id=cd["badge_type"])
            badge.badge_duration = datetime.timedelta(cd["badge_duration"])
            badge.save()
            messages.info(request, SUC_BAGEDIT_ACCEPT)
        else:
            messages.error(request, ERR_BAGEDIT_NOPERMORINVFORM)

        return redirect('user-profile', badge.user.id)

    if request.method == "GET":
        form = BadgeAddForm(user, initial={'badge_type': badge.badge_type.id, 'badge_duration': badge.badge_duration})
        context = {"form": form, "badge": badge.id, "page": "modify"}

        return render(request, "base/badge_mod.html", context)
