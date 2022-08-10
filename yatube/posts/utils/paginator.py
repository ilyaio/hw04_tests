from django.conf import settings
from django.core.paginator import Paginator


def get_page_context(queryset, request):
    paginator = Paginator(queryset, settings.POST_PER_PAGE)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
