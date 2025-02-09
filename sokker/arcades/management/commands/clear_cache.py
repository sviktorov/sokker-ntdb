from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.core.cache import caches

__all__ = ['Command']

class Command(BaseCommand):
    help = 'Clears Django cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cache-name',
            help='Name of the cache to clear (default: all)',
            required=False
        )
        parser.add_argument(
            '--key',
            help='Specific cache key to clear',
            required=False
        )

    def handle(self, *args, **options):
        cache_name = options.get('cache-name')
        key = options.get('key')

        if key:
            if cache_name:
                caches[cache_name].delete(key)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully cleared key "{key}" from cache "{cache_name}"')
                )
            else:
                cache.delete(key)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully cleared key "{key}" from default cache')
                )
        elif cache_name:
            caches[cache_name].clear()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cleared cache "{cache_name}"')
            )
        else:
            for cache_name in caches.all():
                cache_name.clear()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared all caches')
            ) 