from abc import ABC
from collections import namedtuple, OrderedDict
from datetime import datetime
from statistics import mean, stdev

from dateutil import tz

from .config import TwitterConfig

Score = namedtuple('Score', ('id', 'score'))


class PostQueue(OrderedDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rating_methods = list()
        self.filter_methods = list()

        # Add rating methods
        if TwitterConfig.get().search.sort.by_keywords.enabled:
            self.rating_methods.append(RateByKeywords())

        if TwitterConfig.get().search.sort.by_age.enabled:
            self.rating_methods.append(RateByAge())

        if TwitterConfig.get().search.sort.by_retweets_count.enabled:
            self.rating_methods.append(RateByRetweetsCount())

        # Add filter methods

        if TwitterConfig.get().search.filter.min_retweets.enabled:
            self.filter_methods.append(FilterMinRetweets())

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

    def get_rates(self, queue):
        raise NotImplementedError('get_scores must be implemented')

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


# ----------------------------------------------------------------------------------------------------------------------


class FilterABC(ABC):
    """
    Superclass of filtering methods for filtering the queue
    """

    def filter(self, queue):
        raise NotImplementedError('Subclasses must implement filter')


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
