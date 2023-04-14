from .models import Message
from . import subscriptions
import warnings


def subscription(*channels, tags=(), once=None):
    if once is not None:  # pragma: no cover
        warnings.warn(
            '\'once\' argument is deprecated',
            DeprecationWarning
        )

    def wrapper(f):
        for channel in channels:
            subscriptions.register(channel, tags, f, once)

        return f

    return wrapper


def publish(channel, name, *tags, **data):
    message = Message(
        channel=channel,
        name=name,
        data=data,
        tags=tags
    )

    message.publish()
