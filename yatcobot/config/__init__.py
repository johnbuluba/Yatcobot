import logging
import os.path

import confuse
import pkg_resources
import yaml

logger = logging.getLogger(__name__)


class Config:
    base_template = {
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
                'skip_retweeted': confuse.TypeTemplate(bool),
                # Is updated on runtime
                'filter': {},
                # Is updated on runtime
                'sort': {},
            },
            # Is updated on runtime
            'actions': {},
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
        # Is updated on runtime
        'notifiers': {}
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

        # Add default config when in egg (using this way because egg is breaking the default way)
        if len(config.sources) == 0:
            default_config_text = pkg_resources.resource_string("yatcobot.config", "config_default.yaml")
            default_config = confuse.ConfigSource(yaml.load(default_config_text, Loader=confuse.Loader),
                                                  'pkg/config/config_default.yaml',
                                                  True)
            config.add(default_config)

        # Add user specified config
        if filename is not None and os.path.isfile(filename):
            config.set_file(filename)

        logger.info('Loading config files (From highest priority to lowest):')
        config.resolve()
        for i, config_source in enumerate(config.sources):
            logger.info('{}: Path: {}'.format(i, config_source.filename))

        # Update template from plugins
        template = Config.get_template()
        Config._valid = config.get(template)

    @staticmethod
    def get_template():
        """
        Updates the config template dynamically from plugins
        :return: config template
        """
        template = Config.base_template

        # Merge filters templates
        from yatcobot.plugins.filters import FilterABC
        template['twitter']['search']['filter'].update(FilterABC.get_config_template())

        # Merge ratings templates
        from yatcobot.plugins.ratings import RatingABC
        template['twitter']['search']['sort'].update(RatingABC.get_config_template())

        # Merge actions templates
        from yatcobot.plugins.actions import ActionABC
        template['twitter']['actions'].update(ActionABC.get_config_template())

        # Merge notifiers templates
        from yatcobot.plugins.notifiers import NotifierABC
        template['notifiers'].update(NotifierABC.get_config_template())

        return template


class TwitterConfig(Config):

    @staticmethod
    def get():
        return super(TwitterConfig, TwitterConfig).get().twitter


class NotifiersConfig(Config):

    @staticmethod
    def get():
        return super(NotifiersConfig, NotifiersConfig).get().notifiers
