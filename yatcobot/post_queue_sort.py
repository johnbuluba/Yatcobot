from statistics import mean, stdev
from collections import namedtuple, OrderedDict

from .config import Config

Score = namedtuple('Score', ('id', 'score'))


def post_queue_sort(queue):
    """
    Gets a queue of posts and sort it based on various scores
    :param queue: OrderedDict a dict of posts
    :return:OrderedDict the sorted queue
    """
    keywords_score = get_keywords_score(queue)
    retweets_score = get_retweets_score(queue)

    combined_scores = combine_scores(keywords_score, retweets_score)

    sorted_scores = sorted((x for x in combined_scores.items()), key=lambda x: x[1], reverse=True)

    #add a score value to every post
    for post in sorted_scores:
        queue[post[0]]['score'] = post[1]

    return OrderedDict((x[0], queue[x[0]]) for x in sorted_scores)


def combine_scores(*scores):
    """
    Sorts queue based on their score
    :param scores:
    :return:Returns an ordered dict sorted by the scores
    """
    combined_scores = {}
    for score_list in scores:
        for key, score in score_list.items():
            current_score = combined_scores.get(key, 0)
            current_score += score
            combined_scores[key] = current_score

    return combined_scores


def get_keywords_score(queue):
    """
    Gets a queue and returns the scores based on the keywords in text
    :return:A dict of {postid:Score}
    """
    scores = []

    # Find how many times each keyword appears in the text
    for post in queue.values():
        score = 0
        text = post['text'].lower()

        for keyword in Config.priority_keywords:
            keyword = keyword.lower()
            score += text.count(keyword)

        scores.append(Score(post['id'], score))

    norm_scores = normalize_scores(scores)

    return norm_scores


def get_retweets_score(queue):
    """
    Gets a queue and returns the scores based on number of retweets
    :return:A dict of {postid:Score}
    """
    scores = [Score(id,post['retweet_count']) for id, post in queue.items()]

    norm_scores = normalize_scores(scores)

    return norm_scores


def normalize_scores(scores):
    """
    Computes the standardized score for a collection of posts and scores
    :param value: The post score
    :param mean_value: The mean value of all scores
    :param standard_deviation: Standard deviation of all scores
    :return:Standardized score
    """
    m = mean(x.score for x in scores)
    s = stdev(x.score for x in scores)

    normalized_scores = {}

    # if standard deviation is 0 return 0 scores
    if s == 0:
        return {x.id: 0 for x in scores}

    for x in scores:
        normalized_scores[x.id] = (x.score - m)/s

    return normalized_scores




