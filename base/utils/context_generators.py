from .generatorsAndUtils import *
def ContextGenerator(var, comments_check=False, comment_reaction_check=False,
                     post_reaction_check=False, post_badge_check=False, comment_badge_check=False,
                     pag_comments_check=False, make_comment_check=False, comment_history_check=False,
                     edit_comments_check=False, delete_comments_check=False, edit_post_check=False,
                     lock_post_check=False, unlock_posts_check=False, post_history_check=False,
                     delete_post_check=False, move_threads_check=False):
    from django.conf import settings

    context = {}

    if comments_check:
        comments_pre = CommentListGenerator(var["user"], Comment.objects.filter(post=var["post"]), var["badges"])

        if pag_comments_check:
            from django.core.paginator import Paginator

            try:
                index = var["nr"]
            except:
                try:
                    index = var["nr"]
                except:
                    index = int(var["request"].GET.get("index")) if var["request"].GET.get('index') != None else 1

            paginated_comments = Paginator(comments_pre, settings.PAG_AMOUNT)
            page_count = range(paginated_comments.num_pages)

            comments = paginated_comments.page(index)

            pag_next = comments.has_next()
            pag_previous = comments.has_previous()

            front_range = range(settings.NAV_BAR_AMOUNT)

            if index - settings.NAV_BAR_AMOUNT_2 - 1 < 1:
                m1 = settings.NAV_BAR_AMOUNT_2  # to make it odd
            else:
                m1 = index - settings.NAV_BAR_AMOUNT_2 - 1

            if index + settings.NAV_BAR_AMOUNT_2 > paginated_comments.num_pages:
                m2 = paginated_comments.num_pages
            else:
                m2 = index + settings.NAV_BAR_AMOUNT_2

            middle_range = range(m1, m2)
            back_range = range(paginated_comments.num_pages - settings.NAV_BAR_AMOUNT, paginated_comments.num_pages)

            indentation_range = chainNoOverlap(front_range, middle_range, back_range)

            context_tmp = {
                "comments": comments, "page_count": page_count, "pag_next": pag_next, "curent_page": index,
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
            badgeDict = badgeDictGenerator(comments, var["post"])

            context_tmp = {
                "badgeDict": badgeDict
            }

            context = context | context_tmp

    if comment_reaction_check or post_reaction_check:
        from ..models import ReactionTypes
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
        # Done so incase there will ever be a thing as a badge type for something like adding nadges
        # without thw django admin panne;
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