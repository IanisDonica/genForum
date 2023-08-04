from ..models import User, Reaction
from .badge_topic_checker import BadgeTopicAndPostChecker
from .badge_checker import badge_checker

def backendActionAuth(request, action, id):
    #True +  Null = True
    #False + Null = False
    #True + False = False
    #Null = False
    user = request.user

    #Anonymous user does not have these properties, so we gotta make sure they have them :)
    try:
        user.is_verified
        user.is_superuser
    except:
        user.is_verified = False
        user.is_superuser = False

    from ..models import BadgeType

    try:
        user_badge_types = user.badge_set.values_list('badge_type')
        badges = BadgeType.objects.filter(pk__in=user_badge_types)
    except:
        badges = None

    match action:
        case 'can-user-make-post':
            if ( badge_checker(badges, "make_posts_perm") != False or id.banned_users_allowed ) and BadgeTopicAndPostChecker(badges, id) and user.is_verified:
                return True
            return False

        case 'edit-comment':
            if user == id.user or badge_checker(badges, "edit_comments_perm") and ( badge_checker(badges, "edit_comments_perm") != False or id.post.parrent_topic.banned_users_allowed ) and user.is_verified:
                return True
            return False

        case 'edit-post':
            if ( user == id.user and badge_checker(badges, "edit_posts_perm") != False ) or badge_checker(badges, "edit_posts_perm") or ( user == id.user and id.parrent_topic.banned_users_allowed ) and user.is_verified:
                return True
            return False

        case 'add-reaction-comment':
            if user.is_verified and ( badge_checker(badges, "make_reactions_comments") != False or ( id.post.parrent_topic.banned_users_allowed and id.post.user == user )):
                try:
                    Reaction.objects.get(comment=id, user=user)
                    return False
                except:
                    return True
            else:
                return False

        case 'add-reaction-post':
            if user.is_verified and ( badge_checker(badges, "make_reactions_post") != False or ( id.parrent_topic.banned_users_allowed and id.user == user )):
                try:
                    Reaction.objects.get(post=id, user=user)
                    return False
                except:
                    return True
            else:
                return False

        case 'remove-reaction-post':
            if user.is_verified and ( badge_checker(badges, "make_reactions_post") != False or ( id.post.parrent_topic.banned_users_allowed and id.post.user == user )):
                try:
                    Reaction.objects.get(id=id.id)
                    return True
                except:
                    return False
            else:
                return False

        case 'remove-reaction-comment':
            if user.is_verified and ( badge_checker(badges, "make_reactions_comments") != False or ( id.comment.post.parrent_topic.banned_users_allowed and id.comment.post.user == user )):
                try:
                    Reaction.objects.get(id=id.id)
                    return True
                except:
                    return False
            else:
                return False

        case 'make-comment':
            if user.is_verified and (id.is_locked == False or badge_checker(badges, "make_comments_on_locked_perm")) and BadgeTopicAndPostChecker(badges, id) and ( badge_checker(badges, "make_comments") != False or ( id.parrent_topic.banned_users_allowed and id.user == user)):
                return True
            return False

        case 'make-profile-post':
            if user.is_verified and badge_checker(badges, "make_profile_posts") != False:
                return True
            return False
        
        case 'user-settings-save':
            if user.is_authenticated:
                return True
            return False
        
        case 'can-user-delete-comment':
            if (user == id.user or badge_checker(badges, "delete_comments_perm")) and ( badge_checker(badges, "delete_comments_perm") != False or (id.post.parrent_topic.banned_users_allowed and id.user == user )) and not id.is_deleted and BadgeTopicAndPostChecker(badges, id.post):
                return True
            return False


        case 'can-user-delete-post':
            if (user == id.user or badge_checker(badges, "delete_post_perm")) and ( badge_checker(badges, "delete_post_perm") != False or (id.parrent_topic.banned_users_allowed and id.user == user )) and not id.is_deleted and BadgeTopicAndPostChecker(badges, id):
                return True
            return False

        case 'can-user-lock-posts':
            if badge_checker(badges, 'lock_post_perm') and not id.is_locked:
                return True
            return False
        
        case 'can-user-unlock-posts':
            if badge_checker(badges, "unlock_post_perm") and id.is_locked:
                return True
            return False
        
        case 'can-user-see-notifications':
            if user == id.user:
                return True
            return False

        case 'can-user-move-thread':
            if badge_checker(badges, 'move_threads_perm'):
                return True
            return False 

        case 'can-user-see-post':
            if BadgeTopicAndPostChecker(badges, id) and not id.is_deleted or badge_checker(badges, "see_deleted_post_perm") and not id.has_new_version:
                return True
            return False

        case 'can-user-see-comment-history': 
            if badge_checker(badges, "see_comment_history"):
                return True
            return False

        case 'can-user-see-post-history':
            if badge_checker(badges, "see_post_history"):
                return True
            return False

        case 'delete-profile-posts':
            if ( badge_checker(badges, "delete_profile_posts") or id.user == user or id.profile == user ) and not id.is_deleted:
                return True
            return False

        case 'can-user-pin-posts':
            if badge_checker(badges, "pin_posts_perm") and not id.is_pinned:
                return True
            return False

        case 'can-user-unpin-posts':
            if badge_checker(badges, "unpin_posts_perm") and id.is_pinned:
                return True
            return False

        case 'can-user-add-badge':
            if badge_checker(badges, "add_badges_perm") or user.is_superuser:
                return True
            return False

        case 'can-user-modify-badge':
            if badge_checker(badges, "modify_badges_perm") or user.is_superuser:
                return True
            return False

        case 'can-user-revoke-badge':
            if badge_checker(badges, "revoke_badges_perm") or user.is_superuser:
                return True
            return False

