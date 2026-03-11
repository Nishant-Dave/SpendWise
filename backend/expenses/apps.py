from django.apps import AppConfig


class ExpensesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.expenses'
    label = 'expenses'

    def ready(self):
        import backend.expenses.signals  # noqa: F401
