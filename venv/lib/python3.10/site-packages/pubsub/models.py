from . import subscriptions


class TagList(list):
    def filter(self, *tags):
        filtered = []

        for tag in tags:
            if tag in self:
                filtered.append(tag)

        return TagList(filtered)

    def exists(self):
        return any(self)


class Message(object):
    def __init__(self, **kwargs):
        self.channel = kwargs.pop('channel')
        self.name = kwargs.pop('name')
        self.data = kwargs.pop('data', {})
        self.tags = TagList(
            sorted(
                set(
                    kwargs.pop('tags', [])
                )
            )
        )

        for key in kwargs.keys():  # pragma: no cover
            raise TypeError(
                '__init__() got an unexpected keyword argument \'%s\'' % (
                    key
                )
            )

    def publish(self):
        subscriptions.publish(self)

    def call(self, func):
        return func(
            self.channel,
            self.name,
            *self.tags,
            **self.data
        )
