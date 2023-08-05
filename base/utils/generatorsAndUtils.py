#TODO Make generator for if a user can delete a commennt

#TODO Find a better name for this and all of the function

from .sanitationChecks import *
from ..models import User, Reaction, Comment, Topic, ReactionTypes 

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
    from ..models import BadgeType
    badge_dict = {}
    for comment in comments:
        try:
            user_badge_types = comment.user.badge_set.values_list('badge_type')
            badges = BadgeType.objects.filter(pk__in=user_badge_types)
        except:
            badges = None
        badge_dict[comment.id] = badges

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
            reaction = Reaction.objects.get(post=post, user=user)
            return reaction
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

#TODO Fix this so its usable and uses sanitation checks
def canUserReactSingleCommentFunction(request, user, comment):
    if not backendActionAuth(request, 'add-reaction-comment', comment):
        try:
            reaction = Reaction.objects.get(comment=comment, user=user)
            return reaction
        except:
            return False
    else:
        return True

def canUserEditCommentsGenerator(request, commnents):
    can_user_edit = {}

    for comment in commnents:
        if backendActionAuth(request, "edit-comment", comment):
            can_user_edit[comment.id] = True

    return can_user_edit


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

def canUserDeleteProfilePostsGenerator(request, posts):
    canUserDeleteProfilePostsDict = {}
    for post in posts:
        canUserDeleteProfilePostsDict[post.id] = backendActionAuth(request, "delete-profile-posts", post)

    return canUserDeleteProfilePostsDict


def reaction_types_gen():
    reaction_types = []
    reactions = ReactionTypes.objects.all()
    for reaction in reactions:
        reaction_types.append(reaction)

    return reaction_types
def reaction_types_gen(self):
    reaction_types = []
    reactions = ReactionTypes.objects.all()
    for reaction in reactions:
        reaction_types.append(reaction)

    return reaction_types