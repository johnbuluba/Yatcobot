from abc import ABC, abstractmethod
from collections import namedtuple, OrderedDict
from datetime import datetime
from statistics import mean, stdev

from dateutil import tz

from .config import TwitterConfig

Score = namedtuple('Score', ('id', 'score'))


class PostQueue(OrderedDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rating_methods = RateABC.get_enabled()
        self.filter_methods = FilterABC.get_enabled()

    def filter(self):
        """
         Will filter the queue based on the options provided in config
        """
        for method in self.filter_methods:
            method.filter(self)

    def sort(self):
        """
        Will sort the queue based on the options provided in config

        """
        # If len < 2, StatisticsError('variance requires at least two data points')
        if len(self) < 2:
            # Set a predefined score
            for x in self.values():
                x['score'] = 1
            return

        combined_rates = self.combine_rates(*(method.get_rates(self) for method in self.rating_methods))

        sorted_rates = sorted((x for x in combined_rates.items()), key=lambda x: x[1], reverse=True)

        # add a score value to every post
        for post in sorted_rates:
            self[post[0]]['score'] = post[1]

        updated_queue = OrderedDict((x[0], self[x[0]]) for x in sorted_rates)
        self.clear()
        self.update(updated_queue)

    def combine_rates(self, *rates):
        """
        Combines the rates of multiple features to one final rate
        :param rates: a tuple of list of scores ( [Ascore1, Ascore2], [Bscore1,Bscore2])
        :return:Returns an a dict with final scores {id:Score}
        """
        combined_rates = {}
        for rates_list in rates:
            for rate in rates_list:
                current_score = combined_rates.get(rate.id, 0)
                current_score += rate.score
                combined_rates[rate.id] = current_score

        return combined_rates


# ----------------------------------------------------------------------------------------------------------------------

class RateABC(ABC):
    """
    Superclass of rating methods that are used for sorting the queue
    """

    config_name = ''

    @abstractmethod
    def get_rates(self, queue):
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
        for cls in RateABC.__subclasses__():
            if cls.is_enabled():
                enabled.append(cls())
        return enabled


class RateByKeywords(RateABC):
    config_name = 'by_keywords'

    def get_rates(self, queue):
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


class RateByRetweetsCount(RateABC):
    config_name = 'by_retweets_count'

    def get_rates(self, queue):
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


class RateByAge(RateABC):
    config_name = 'by_age'

    def get_rates(self, queue):
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


# ----------------------------------------------------------------------------------------------------------------------


class FilterABC(ABC):
    """
    Superclass of filtering methods for filtering the queue
    """

    @abstractmethod
    def filter(self, queue):
        raise NotImplementedError('Subclasses must implement filter')

    @staticmethod
    @abstractmethod
    def is_enabled():
        """Action must implement is_enabled"""

    @staticmethod
    def get_enabled():
        """Retuns a list of instances of actions that are enabled"""
        enabled = list()
        for cls in FilterABC.__subclasses__():
            if cls.is_enabled():
                enabled.append(cls())
        return enabled


class FilterMinRetweets(FilterABC):

    def filter(self, queue):
        """
        Removes all post that have less rewteets than min_retweets defined at config
        :param queue: Posts Queue
        """
        ids_to_remove = list()

        for post_id, post in queue.items():
            if post['retweet_count'] < TwitterConfig.get().search.filter.min_retweets.number:
                ids_to_remove.append(post_id)

        for post_id in ids_to_remove:
            del queue[post_id]

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().search.filter.min_retweets.enabled
