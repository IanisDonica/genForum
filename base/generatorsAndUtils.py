#TODO Make generator for if a user can delete a commennt
def badge_checker(badges, check_type):
    if not badges:
        return False

    def search_tree(current_dir):
        permision = None
        for badge in current_dir:
            if getattr(badge, check_type ,None) is not None:
                return getattr(badge, check_type ,None)

        current_dir2 = []
        for badge in current_dir:
            if badge.inheritance != None:
                current_dir2.append(badge.inheritance)

        if len(current_dir2) == 0:
            return None
        else: 
            return search_tree(current_dir2)

    return search_tree(badges)

#TODO Find a better name for this and all of the function 

def BadgeTopicAndPostChecker(user_badges, topic):
    def compare_badges(badges):
        if user_badges == None and badges == None:
            return True
        elif user_badges == None and badges:
            return False

        for badge in badges:
            for user_badge in user_badges:
                if user_badge == badge:
                    return True
            
        return False

    def search_badges(topic):
        if topic.parrent_topic is None and not len(topic.view_permisions.all()):
            return True
        elif topic.parrent_topic and not len(topic.view_permisions.all()):
            return search_badges(topic.parrent_topic)
        elif len(topic.view_permisions.all()):
            return compare_badges(topic.view_permisions.all())
        
    return search_badges(topic)

from .sanitationChecks import *
from .models import User, Reaction, Comment, Topic

def history_checker(item):
    item_div = []

    def loopback(item):
        if item.previous:
            item_div.append(item.previous)
            item = item.previous

            return loopback(item)
        
        return item_div
    
    return loopback(item)


def canUserDeleteComments(request, comments):
    canUserDeleteCommentsDict = {}
    for comment in comments:
        if backendActionAuth(request, 'can-user-delete-comment', comment):
            canUserDeleteCommentsDict[comment.id] = True
        else: 
            canUserDeleteCommentsDict[comment.id] = False

    return canUserDeleteCommentsDict


def badgeDictGenerator(comments, post):
    badge_dict = {"post": {}, "comments": {}}
    badge_dict["post"] = User.objects.get(id=post.user.id).badges.all()
    for comment in comments:
        try:
            badges = User.objects.get(id=comment.user.id).badges.all()
        except:
            badges = None
        badge_dict["comments"][comment.id] = badges
    return badge_dict

def reactionsCommentGenerator(comments):
    reactions_comment_dict = {}
    for comment in comments:
        reactions_comment = Reaction.objects.filter(comment=comment)
        reactions_comment_dict[comment] = {}

        for reaction in reactions_comment:
            if reaction.reaction_type in reactions_comment_dict[comment]:
                reactions_comment_dict[comment][reaction.reaction_type].append(reaction)
            else: 
                reactions_comment_dict[comment][reaction.reaction_type] = [reaction]

    return reactions_comment_dict

def reactionsPostGenerator(post):
    reactions_post_dict = {}
    reactions_post = Reaction.objects.filter(post=post)
    for reaction in reactions_post:
        if reaction.reaction_type in reactions_post_dict:
            reactions_post_dict[reaction.reaction_type].append(reaction)
        else: 
            reactions_post_dict[reaction.reaction_type] = [reaction]

    return reactions_post_dict

def canUserReactCommentsGenerator(request, comments):
    canUserReactComment = {}
    for comment in comments:
        if backendActionAuth(request, 'add-reaction-comment', comment):
            canUserReactComment[comment.id] = True
        else:
            try:
                Reaction.objects.get(comment=comment, user=request.user)
                canUserReactComment[comment.id] = "reaction_in_place"
            except:
                canUserReactComment[comment.id] = False
            
    return canUserReactComment

def canUserReactPostFunction(request, user, post):
    if not backendActionAuth(request, 'add-reaction-post', post):
        try:
            Reaction.objects.get(post=post, user=user)
            return "reaction_in_place"
        except:
            return False
    else:
        return True

def singleReactionCommentGenerator(comment):
    reactions_single_comment = {}
    reactions_comment = Reaction.objects.filter(comment=comment)
    for reaction in reactions_comment:
        if reaction.reaction_type in reactions_single_comment:
            reactions_single_comment[reaction.reaction_type].append(reaction)
        else: 
            reactions_single_comment[reaction.reaction_type] = [reaction]

    return reactions_single_comment

def canUserReactSingleCommentFunction(user, comment):
    if not user.is_authenticated:
        return False
    else:
        try:
            reaction = Reaction.objects.get(comment=comment, user=user)
            return reaction
        except:
            return True

def canUserEditCommentsGenerator(request, commnents):
    can_user_edit = {}

    for comment in commnents:
        if backendActionAuth(request, "edit-comment", comment):
            can_user_edit[comment.id] = True

    return can_user_edit

def canUserEditPostGenerator(user, post):
    try:
        badges = user.badges.all()
    except:
        badges = None
    
    if badge_checker(badges, "edit_posts_perm") or post.user == user:
        return True
    else: 
        return False

def CommentListGenerator(user, comments, badges):
    permision = badge_checker(badges, "see_deleted_comments_perm")
    comments_dict = []

    for comment in comments:
        if not comment.is_deleted and not comment.has_new_version:
            comments_dict.append(comment)
        else:
            if permision and not comment.has_new_version:
                comments_dict.append(comment)

    comments_dict = sorted(comments_dict, key=lambda x: x.created)
    return comments_dict


#TODO Find a better name since it works for generating posts aswel

def TopicsGenerator(topics, badges): 
    exclude_topics = []
    for topic in topics:
        try: 
            has_new_version = topic.has_new_version
        except:
            has_new_version = False

        if not BadgeTopicAndPostChecker(badges, topic) or has_new_version:
            exclude_topics.append(topic.id)
    
    return topics.exclude(pk__in=exclude_topics)

def chainNoOverlap(*argv):
    chained_list= []
    for arg in argv:
        for i in arg:
            if not i in chained_list:
                chained_list.append(i)

    chained_list.sort()

    chained_list_post = chained_list.copy()
    prev = chained_list[0]
    n = 0
    z = 0
    for i in chained_list:
        if i - prev > 1:
            chained_list_post.insert(n + z, "...")
            z += 1
        prev = i 
        n += 1

    return chained_list_post

def topicDictGenerator(base_topics):
    base_dict = {}
    for topic in base_topics:
        child_topics = Topic.objects.filter(parrent_topic=topic)
        if not child_topics:
            base_dict[topic] = None
        else: 
            base_dict[topic] = topicDictGenerator(child_topics)

    return base_dict

def RemoveDeletedIfNoPermisions(posts, badges):
    posts_exclude = []
    if not badge_checker(badges, "see_deleted_post_perm"):
        for post in posts:
            if post.is_deleted:
                posts_exclude.append(post.id)

    return posts.exclude(pk__in=posts_exclude) 

def ContextGenerator(var, comments_check=False, comment_reaction_check=False,
                     post_reaction_check=False, post_badge_check=False, comment_badge_check=False,
                     pag_comments_check=False, make_comment_check=False, comment_history_check=False,
                     edit_comments_check=False, delete_comments_check=False,edit_post_check=False,
                    lock_post_check=False,unlock_posts_check=False, post_history_check=False,
                    delete_post_check=False, move_threads_check=False):

    from django.conf import settings

    context = {}

    if comments_check:
        comments_pre = CommentListGenerator(var["user"],Comment.objects.filter(post=var["post"]), var["badges"])

        if pag_comments_check:
            from django.core.paginator import Paginator

            try:
                index = var["nr"]
            except:
                index = int(var["request"].GET.get("index")) if var["request"].GET.get('index') != None else 1

            paginated_comments = Paginator(comments_pre, settings.PAG_AMOUNT)
            page_count = range(paginated_comments.num_pages)

            try:
                comments = paginated_comments.page(index)
            except:
                comments = paginated_comments.page(page_count)
                
            pag_next = comments.has_next()
            pag_previous = comments.has_previous()

            front_range = range(settings.NAV_BAR_AMOUNT)
            back_range = range(paginated_comments.num_pages - settings.NAV_BAR_AMOUNT ,paginated_comments.num_pages)

            if index - settings.NAV_BAR_AMOUNT_2 - 1 < 1:
                m1 = settings.NAV_BAR_AMOUNT_2  #to make it odd
            else:
                m1 = index-settings.NAV_BAR_AMOUNT_2  - 1

            if index+settings.NAV_BAR_AMOUNT_2 > paginated_comments.num_pages:
                m2 = paginated_comments.num_pages
            else: 
                m2 = index+settings.NAV_BAR_AMOUNT_2

            middle_range = range(m1, m2) 
            back_range = range(paginated_comments.num_pages - settings.NAV_BAR_AMOUNT,paginated_comments.num_pages)

            indentation_range = chainNoOverlap(front_range, middle_range, back_range)
        
            context_tmp = {
                "comments": comments,"page_count": page_count, "pag_next": pag_next, "curent_page": index,
                "pag_previous": pag_previous, "indentation_range": indentation_range
                }   

            context = context_tmp | context
       
        else:
           comments = comments_pre
           context["comments"] = comments

        if make_comment_check:
            canUserMakeComment = backendActionAuth(var["request"], "make-comment", var["post"])
            context["canUserMakeComment"] = canUserMakeComment 

        if comment_reaction_check:
            reactions_comment_dict = reactionsCommentGenerator(comments)
            canUserReactComment = canUserReactCommentsGenerator(var["request"], comments)
            
            context_tmp = {
            "reactions_comment_dict": reactions_comment_dict,
            "canUserReactComment": canUserReactComment, 
            }

            context = context | context_tmp

        if comment_history_check:
            canUserSeeEditHistoryComments = backendActionAuth(var["request"], "can-user-see-comment-history", None)
            context["canUserSeeEditHistoryComments"] = canUserSeeEditHistoryComments

        if edit_comments_check:
            canUserEditComments = canUserEditCommentsGenerator(var["request"], comments)
            context["canUserEditComments"] = canUserEditComments
        
        if delete_comments_check:
            canUserDeleteCommentsDict = canUserDeleteComments(var["request"], comments)
            context["canUserDeletCommentsDict"] = canUserDeleteCommentsDict

        if comment_badge_check: 
            badgeDict = badgeDictGenerator(comments,var["post"])

            context_tmp = {
                "badgeDict": badgeDict
            }

            context = context | context_tmp

    if comment_reaction_check or post_reaction_check:
        from .models import ReactionTypes 
        if post_reaction_check:

            reactions_post_dict = reactionsPostGenerator(var["post"])
            canUserReactPost = canUserReactPostFunction(var["request"], var["user"], var["post"])

            context_tmp = {
           "reactions_post_dict": reactions_post_dict,
            "canUserReactPost": canUserReactPost, 
            }
        
            context = context | context_tmp

        reaction_types = ReactionTypes.reaction_types_gen()

        context_tmp = {
            "reaction_types": reaction_types 
        }
        
        context = context | context_tmp


    if post_badge_check or comment_badge_check:
        #Done so incase there will ever be a thing as a badge type for something like adding nadges 
        #without thw django admin panne;
        if post_badge_check:
            post_badges = var["post"].user.badges.all()        
            
            context_tmp = {
                "post_badges": post_badges
            }

            context = context | context_tmp


    
    if edit_post_check: 
        canusereditpost = canUserEditPostGenerator(var["user"], var["post"])
        context["canusereditpost"] = canusereditpost

    if lock_post_check:
        canUserLockPost = backendActionAuth(var["request"], "can-user-lock-posts", var["post"])
        context["canUserLockPost"] = canUserLockPost

    if unlock_posts_check:
        canUserUnlockPost = backendActionAuth(var["request"], "can-user-unlock-posts", var["post"])
        context["canUserUnlockPost"] = canUserUnlockPost

    if post_history_check:
        canUserSeeEditHistoryPosts = backendActionAuth(var["request"], "can-user-see-post-history", None)
        context["canUserSeeEditHistoryPosts"] = canUserSeeEditHistoryPosts
    
    if delete_post_check:
        canUserDeletePost = backendActionAuth(var["request"], 'can-user-delete-post', var["post"])
        context["canUserDeletePost"] = canUserDeletePost

    if move_threads_check:
        canUserMoveThreads = badge_checker(var["badges"], "move_threads_perm")
        context["canUserMoveThreads"] = canUserMoveThreads


    return context 



            
