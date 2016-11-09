import logging
from project.external_services import log_to_mixpanel
from urllib.parse import urlparse
import uuid


logger = logging.getLogger(__name__)


class PersistReferrerMiddleware:

    def process_request(self, request):
        referrer = request.META.get('HTTP_REFERER')
        if referrer:
            referrer_host = urlparse(referrer).netloc
            # make sure this is not an internal referrer
            if referrer_host != request.get_host():
                request.session['referrer'] = referrer
        return None


class GetCleanIpAddressMiddleware:

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def process_request(self, request):
        request.ip_address = self._get_client_ip(request)
        return None


class TrackPageViewsMiddleware:

    def process_request(self, request):
        applicant_id = request.session.get(
            'applicant_id', 'anon_%s' % uuid.uuid4())
        log_to_mixpanel(applicant_id, "page_view", {
            'applicant_id': applicant_id,
            'path': request.path
        })
