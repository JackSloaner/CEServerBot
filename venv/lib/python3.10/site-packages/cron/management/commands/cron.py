from django.core.management.base import BaseCommand
from logging import getLogger
from ...helpers import autodiscover, get_scheduler


class Command(BaseCommand):
    help = 'Run scheduled jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            help='Name of queue to check for scheduled tasks',
            default='default'
        )

    def handle(self, *args, **options):
        logger = getLogger('podiant.cron')
        scheduler = get_scheduler(
            queue_name=options['queue']
        )

        cleared = 0

        for job in scheduler.get_jobs():
            cleared += 1
            job.delete()

        if cleared:
            logger.debug(
                'Cleared %d job(s) from scheduler' % cleared
            )

        autodiscover(
            schedule=True,
            queue_name=options['queue']
        )

        logger.debug('Running cron worker')
        scheduler.run()
