from django.dispatch import receiver
from django.utils import timezone
from .tasks import write_login_log_async
from .signals import post_auth_success, post_auth_failed
from .utils import get_request_ip
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def generate_data(username, request):
    logger.info(request)

    login_ip = get_request_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    login_type = 'W'

    data = {
        'username': username,
        'ip': login_ip,
        'type': login_type,
        'user_agent': user_agent,
        'datetime': timezone.now()
    }
    return data

@receiver(post_auth_success)
def on_user_auth_success(sender, user, request, **kwargs):
    logger.info('on_user_auth_success')
    data = generate_data(user.username, request)
    data.update({'status': True})
    if settings.ENV_MODE == 'DEMO':
        write_login_log_async(**data)
    else:
        write_login_log_async.delay(**data)


@receiver(post_auth_failed)
def on_user_auth_failed(sender, username, request, reason, **kwargs):
    logger.info('on_user_auth_failed')
    data = generate_data(username, request)
    data.update({'reason': reason, 'status': False})
    if settings.ENV_MODE == 'DEMO':
        write_login_log_async(**data)
    else:
        write_login_log_async.delay(**data)
