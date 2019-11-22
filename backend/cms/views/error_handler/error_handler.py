from django.shortcuts import render
from django.utils.translation import ugettext as _


# pylint: disable=unused-argument
def handler400(request, exception):
    ctx = {'code': 400, 'title': _('Bad request'),
           'message': _('There was an error in your request.')}
    response = render(request, 'error_handler/http_error.html', ctx)
    response.status_code = 400
    return response

    # pylint: disable=unused-argument
def handler403(request, exception):
    ctx = {'code': 403, 'title': _('Forbidden'),
           'message': _("You don't have the permission to access this page.")}
    response = render(request, 'error_handler/http_error.html', ctx)
    response.status_code = 403
    return response

    # pylint: disable=unused-argument
def handler404(request, exception):
    ctx = {'code': 404, 'title': _('Page not found'),
           'message': _('The page you requested could not be found.')}
    response = render(request, 'error_handler/http_error.html', ctx)
    response.status_code = 404
    return response

    # pylint: disable=unused-argument
def handler500(request):
    ctx = {'code': 500, 'title': _('Internal Server Error'),
           'message': _('An unexpected error has occurred.')}
    response = render(request, 'error_handler/http_error.html', ctx)
    response.status_code = 500
    return response

    # pylint: disable=unused-argument
def csrf_failure(request, reason):
    return render(request, 'error_handler/csrf_failure.html')
