def badge_checker(badges, check_type):
    if not badges:
        return None

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