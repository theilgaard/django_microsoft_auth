import logging

from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from .client import MicrosoftClient
from .conf import LOGIN_TYPE_XBL, config

logger = logging.getLogger('django')


def microsoft(request):
    """ Adds global template variables for microsoft_auth """
    login_type = None
    if config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
        login_type = _('Xbox Live')
    else:
        login_type = _('Microsoft')

    if config.DEBUG:
        expected_domain = Site.objects.get_current().domain
        current_domain = request.get_host()
        if expected_domain != current_domain:
            logger.warning(
                '\n\nWARNING:\nThe domain configured for the sites framework '
                'does not match the domain you are accessing Django with. '
                'Microsoft authentication may not work.\n\n'
            )

        if request.scheme == 'http' and \
                not current_domain.startswith('localhost'):
            logger.warning(
                '\n\nWARNING:\nYou are not using HTTPS. Microsoft '
                'authentication only works over HTTPS unless the hostname for '
                'your `redirect_uri` is `localhost`\n\n'
            )

    # initialize Microsoft client using CSRF token as state variable
    microsoft = MicrosoftClient(state=get_token(request))
    auth_url = microsoft.authorization_url()[0]
    return {
        'microsoft_login_enabled': config.MICROSOFT_AUTH_LOGIN_ENABLED,
        'microsoft_authorization_url': mark_safe(auth_url),
        'microsoft_login_type_text': login_type}
