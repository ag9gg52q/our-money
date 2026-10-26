from django.apps import AppConfig


class HouseholdsConfig(AppConfig):
    name = 'households'

    def ready(self):
        from . import signals  # noqa: F401
