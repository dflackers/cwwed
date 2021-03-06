from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from revproxy.views import ProxyView, QUOTE_SAFE
from audit.models import ThreddsRequestLog


class ThreddsProxy(ProxyView):

    @method_decorator(login_required)
    def dispatch(self, request, path):
        if self._should_log():
            ThreddsRequestLog(
                user=request.user,
                path=request.get_full_path(),
            ).save()
        return super().dispatch(request, path)

    def get_proxy_request_headers(self, request):
        # overridden to spoof the port to this web application
        headers = super().get_proxy_request_headers(request)
        headers['HOST'] = request.get_host()
        return headers

    def get_quoted_path(self, path):
        # overridden to use quote vs quote_plus because THREDDS chokes on the plus characters
        return quote(path.encode('utf8'), QUOTE_SAFE)

    def _should_log(self) -> bool:
        exclusions = (
            '/',
            '.gif',
            '.html',
            '.css',
        )
        return not any([self.request.path.endswith(p) for p in exclusions])
