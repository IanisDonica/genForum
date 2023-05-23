from ..models import User, Reaction
from .badge_topic_checker import BadgeTopicAndPostChecker
from .badge_checker import badge_checker

def backendActionAuth(request, action, id):
    #True +  Null = True
    #False + Null = False
    #True + False = False
    #Null = False
    user = request.user
    try:
        badges = User.objects.get(id=request.user.id).badges.all()
    except:
        badges = None

    match action: 
        case 'edit-comment':
            if user == id.user or badge_checker(badges, "edit_comments_perm") and badge_checker(badges, "edit_comments_perm") != False and user.is_verified:
                return True
            return False

        case 'edit-post':
            if user == id.user or badge_checker(badges, "edit_posts_perm") and badge_checker(badges, "edit_posts_perm") != False and user.is_verified:
                return True
            return False

        case 'add-reaction-comment':
            if not user.is_verified or badge_checker(badges, "make_reactions_comments") == False:
                return False

            if len(Reaction.objects.filter(comment=id, user=user)):
                return False
            else:
                return True

        case 'add-reaction-post':
            if not user.is_verified or badge_checker(badges, "make_reactions_post") == False:
                return False
            
            try:
                Reaction.objects.get(post=id, user=user)
                return False
            except:
                return True

        case 'remove-reaction':
            if user == id.user and badge_checker(badges, "make_reactions_post") != False:
                return True
            return False

        case 'make-comment':
            if user.is_authenticated and (id.is_locked == False or badge_checker(badges, "make_comments_on_locked_perm")) and BadgeTopicAndPostChecker(badges, id) and badge_checker(badges, "make_comments") != False:
                return True
            return False

        case 'make-profile-post':
            if user.is_authenticated and badge_checker(badges, "make_profile_posts") != False:
                return True
            return False
        
        case 'user-settings-save':
            if user.is_authenticated:
                return True
            return False
        
        case 'can-user-delete-comment':
            if user == id.user or badge_checker(badges, "delete_comments_perm") and not id.is_deleted and BadgeTopicAndPostChecker(badges, id.post):
                return True
            return False
        
        case 'can-user-delete-post':
            if user == id.user or badge_checker(badges, "delete_post_perm") and not id.is_deleted and BadgeTopicAndPostChecker(badges, id):
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
