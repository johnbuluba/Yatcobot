import os.path

import confuse
import pkg_resources
import yaml


class Config:
    template = {
        'twitter': {
            'consumer_key': confuse.String(),
            'consumer_secret': confuse.String(),
            'access_token_key': confuse.String(),
            'access_token_secret': confuse.String(),
            'min_ratelimit_percent': confuse.Integer(),

            'search': {
                'queries': confuse.TypeTemplate(list),
                'max_queue': confuse.Integer(),
                'max_quote_depth': confuse.Integer(),
                'min_quote_similarity': confuse.Number(),
                'filter': {
                    'min_retweets': {
                        'enabled': confuse.TypeTemplate(bool),
                        'number': confuse.Integer()
                    }
                },
                'sort': {
                    'by_keywords': {
                        'enabled': confuse.TypeTemplate(bool),
                        'keywords': confuse.StrSeq()
                    },
                    'by_age': {
                        'enabled': confuse.TypeTemplate(bool),
                    },
                    'by_retweets_count': {
                        'enabled': confuse.TypeTemplate(bool),
                    }
                }
            },

            'actions': {
                'follow': {
                    'enabled': confuse.TypeTemplate(bool),
                    'keywords': confuse.StrSeq(),
                    'max_following': confuse.Integer(),
                },
                'favorite': {
                    'enabled': confuse.TypeTemplate(bool),
                    'keywords': confuse.StrSeq()
                },
            },

            'scheduler': {
                'search_interval': confuse.Integer(),
                'retweet_interval': confuse.Integer(),
                'retweet_random_margin': confuse.Integer(),
                'blocked_users_update_interval': confuse.Integer(),
                'clear_queue_interval': confuse.Integer(),
                'rate_limit_update_interval': confuse.Integer(),
                'check_mentions_interval': confuse.Integer(),
            },
        },
        'notifiers': {
            'pushbullet': {
                'enabled': confuse.TypeTemplate(bool),
                'token': confuse.String()
            }
        }
    }

    _valid = None

    @staticmethod
    def get():
        """
        Gets the static config object
        :return:
        """
        if Config._valid is None:
            raise ValueError("Configuration not loaded")
        return Config._valid

    @staticmethod
    def load(filename=None):
        """
        Loads a file and imports the settings
        :param filename: the file to import
        """
        config = confuse.LazyConfig('Yatcobot', __name__)

        # Add default config (using this way because egg is breaking the default way)
        default_config_text = pkg_resources.resource_string("yatcobot", "config_default.yaml")
        config.add(yaml.load(default_config_text, Loader=confuse.Loader))

        if filename is not None and os.path.isfile(filename):
            config.set_file(filename)
        Config._valid = config.get(Config.template)


class TwitterConfig(Config):

    @staticmethod
    def get():
        return super(TwitterConfig, TwitterConfig).get().twitter


class NotifiersConfig(Config):

    @staticmethod
    def get():
        return super(NotifiersConfig, NotifiersConfig).get().notifiers
