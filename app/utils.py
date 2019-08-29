from app.celery import app as celery_app


def send_to_zagreus(transaction: dict, provider: str, location: str = '') -> None:
    transaction['provider'] = provider
    transaction['location'] = location
    celery_app.send_task('auth-transactions.save', args=[transaction, ])
