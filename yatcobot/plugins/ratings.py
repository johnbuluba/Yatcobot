from abc import abstractmethod
from collections import namedtuple
from datetime import datetime
from statistics import mean, stdev

from dateutil import tz

from yatcobot.config import TwitterConfig
from yatcobot.plugins import PluginABC

Score = namedtuple('Score', ('id', 'score'))


class RatingABC(PluginABC):
    """
    Superclass of rating methods that are used for sorting the queue
    """

    config_name = ''

    @abstractmethod
    def get_rating(self, queue):
        """Must be implemented by RateABC classes"""

    def normalize_scores(self, scores):
        """
        Computes the standardized score for a collection of scores
        :param scores: A list of scores [Score]
        :return:Standardized score
        """
        m = mean(x.score for x in scores)
        s = stdev(x.score for x in scores)

        normalized_scores = []

        # if standard deviation is 0 return 0 scores
        if s == 0:
            return [Score(x.id, 0) for x in scores]

        for x in scores:
            normalized_scores.append(Score(x.id, (x.score - m) / s))

        return normalized_scores

    @staticmethod
    @abstractmethod
    def is_enabled():
        """Action must implement is_enabled"""

    @staticmethod
    def get_enabled():
        """Retuns a list of instances of actions that are enabled"""
        enabled = list()
        for cls in RatingABC.__subclasses__():
            if cls.is_enabled():
                enabled.append(cls())
        return enabled


class RatingByKeywords(RatingABC):
    config_name = 'by_keywords'

    def get_rating(self, queue):
        """
        Gets a queue and returns the scores based on the keywords in text
        :param queue: The queue to score
        :return:A list of scores [Score]
        """
        rates = []

        # Find how many times each keyword appears in the text
        for post in queue.values():
            rate = 0
            text = post['full_text'].lower()

            for keyword in TwitterConfig.get().search.sort.by_keywords.keywords:
                keyword = keyword.lower()
                rate += text.count(keyword)

            rates.append(Score(post['id'], rate))

        norm_scores = self.normalize_scores(rates)

        return norm_scores

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().search.sort.by_keywords.enabled


class RatingByRetweetsCount(RatingABC):
    config_name = 'by_retweets_count'

    def get_rating(self, queue):
        """
        Gets a queue and returns the scores based on the retweets of the post
        :param queue: The queue to score
        :return:A list of scores [Score]
        """
        rates = [Score(post_id, post['retweet_count']) for post_id, post in queue.items()]

        norm_rates = self.normalize_scores(rates)

        return norm_rates

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().search.sort.by_retweets_count.enabled


class RatingByAge(RatingABC):
    config_name = 'by_age'

    def get_rating(self, queue):
        rates = []

        now = datetime.now(tz.tzutc())

        for post in queue.values():
            post_date = datetime.strptime(post['created_at'], '%a %b %d %H:%S:%M %z %Y')
            seconds = (post_date - now).total_seconds()
            rates.append(Score(post['id'], seconds))

        return self.normalize_scores(rates)

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().search.sort.by_age.enabled
