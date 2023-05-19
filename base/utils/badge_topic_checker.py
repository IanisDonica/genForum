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