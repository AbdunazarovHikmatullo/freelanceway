from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.core.cache import cache
from .cache import generate_cache_key

class CachedPaginator(Paginator):
    """
    Расширенный класс пагинатора с кешированием
    """
    def __init__(self, object_list, per_page, cache_key_prefix=None, cache_timeout=300, orphans=0, allow_empty_first_page=True):
        self.cache_key_prefix = cache_key_prefix
        self.cache_timeout = cache_timeout
        super().__init__(object_list, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)
    
    def _get_count(self):
        """
        Кешированная версия получения общего количества объектов
        """
        if self.cache_key_prefix:
            cache_key = f"{self.cache_key_prefix}_count"
            count = cache.get(cache_key)
            if count is None:
                count = super()._get_count()
                cache.set(cache_key, count, self.cache_timeout)
            return count
        return super()._get_count()
    
    def page(self, number):
        """
        Кешированная версия получения страницы
        """
        if self.cache_key_prefix:
            cache_key = f"{self.cache_key_prefix}_page_{number}"
            page_obj = cache.get(cache_key)
            if page_obj is None:
                page_obj = super().page(number)
                cache.set(cache_key, page_obj, self.cache_timeout)
            return page_obj
        return super().page(number)

def paginate_queryset(request, queryset, per_page=None, cache_key_prefix=None, cache_timeout=300):
    """
    Функция для пагинации QuerySet с кешированием
    
    Аргументы:
        request: объект запроса Django
        queryset: QuerySet для пагинации
        per_page: количество элементов на странице (по умолчанию из настроек)
        cache_key_prefix: префикс ключа кеша (если None, кеширование не используется)
        cache_timeout: время жизни кеша в секундах
    
    Возвращает:
        page_obj: объект страницы
    """
    if per_page is None:
        per_page = getattr(settings, 'PAGINATION_PAGE_SIZE', 12)
    
    orphans = getattr(settings, 'PAGINATION_ORPHANS', 3)
    
    if cache_key_prefix:
        # Генерируем уникальный ключ кеша на основе запроса
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        
        cache_key = generate_cache_key(
            cache_key_prefix,
            str(query_params.urlencode())
        )
    else:
        cache_key = None
    
    paginator = CachedPaginator(
        queryset, 
        per_page, 
        cache_key_prefix=cache_key,
        cache_timeout=cache_timeout,
        orphans=orphans
    )
    
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу
        page_obj = paginator.page(1)
    except EmptyPage:
        # Если страница вне диапазона, возвращаем последнюю страницу
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj
