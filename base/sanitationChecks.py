from .models import User, Reaction
from .generatorsAndUtils import badge_checker, BadgeTopicAndPostChecker

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
            if request.user == id.user or badge_checker(badges, "edit_comments_perm"):
                return True
            return False

        case 'edit-post':
            if user == id.user or badge_checker(badges, "edit_posts_perm"):
                return True
            return False

        case 'add-reaction-comment':
            if not user.is_authenticated:
                return False

            if len(Reaction.objects.filter(comment=id, user=user)):
                return False
            else:
                return True

        case 'add-reaction-post':
            if not user.is_authenticated:
                return False
            
            try:
                Reaction.objects.get(post=id, user=user)
                return False
            except:
                return True

        case 'remove-reaction':
            if user == id.user:
                return True
            return False

        case 'make-comment':
            if user.is_authenticated and (id.is_locked == False or badge_checker(badges, "make_comments_on_locked_perm")) and BadgeTopicAndPostChecker(badges, id):
                return True
            return False

        case 'make-profile-post':
            if user.is_authenticated:
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
            print("badge_checker: ", badge_checker(badges, "delete_post_perm"))
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