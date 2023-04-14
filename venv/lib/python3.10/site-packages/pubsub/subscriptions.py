from .exceptions import AlreadyRegisteredError
import logging
import re
import warnings


class SubscriptionList(object):
    def __init__(self):
        self._subs = []
        self._logger = logging.getLogger('pubsub')

    def register(self, channel, tags, func, once=None):
        if once is not None:  # pragma: no cover
            warnings.warn(
                '\'once\' argument is deprecated',
                DeprecationWarning
            )

        key = '^' + channel.replace(
            '.', '\\.'
        ).replace('*', '([a-z0-9]+)') + '$'
        ex = re.compile(key)

        for (e, t, f, o) in self._subs:
            if f == func and e == ex:
                raise AlreadyRegisteredError(
                    '%s is already registered.' % (func.__name__)
                )

        self._subs.append(
            (
                ex,
                tags,
                func,
                once
            )
        )

    def publish(self, message):
        self._logger.debug(
            'Publishing on channel \'%s\'' % message.channel
        )

        for ex, listening_tags, func, once in self._subs:
            if ex.match(message.channel) is None:
                continue

            if any(listening_tags):
                if not message.tags.filter(*listening_tags).exists():
                    continue

            self._logger.debug('Sending to %s' % func.__name__)

            try:
                message.call(func)
            except AssertionError:
                raise
            except Exception:
                self._logger.error(
                    'Error running action hook',
                    extra={
                        'channel_name': message.channel,
                        'msg_name': message.name,
                        'msg_data': message.data,
                        'msg_func': func.__name__
                    },
                    exc_info=True
                )
