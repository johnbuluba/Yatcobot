from collections import OrderedDict

from yatcobot.plugins.filters import FilterABC
from yatcobot.plugins.ratings import RatingABC


class PostQueue(OrderedDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rating_methods = RatingABC.get_enabled()
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

        combined_rates = self.combine_rates(*(method.get_rating(self) for method in self.rating_methods))

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
