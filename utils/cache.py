from django.core.cache import cache
from django.utils.encoding import force_str
from functools import wraps
import hashlib
import time

def generate_cache_key(prefix, *args, **kwargs):
    """
    Генерирует уникальный ключ кеша на основе префикса и аргументов
    """
    key_parts = [prefix]
    
    # Добавляем позиционные аргументы
    for arg in args:
        key_parts.append(force_str(arg))
    
    # Добавляем именованные аргументы, отсортированные по ключу
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{force_str(v)}")
    
    # Создаем хеш для длинных ключей
    key = "_".join(key_parts)
    if len(key) > 200:  # Если ключ слишком длинный
        hash_obj = hashlib.md5(key.encode('utf-8'))
        key = f"{prefix}_{hash_obj.hexdigest()}"
    
    return key

def cache_result(timeout=300, prefix='view'):
    """
    Декоратор для кеширования результатов функции
    
    Пример использования:
    @cache_result(timeout=3600, prefix='my_view')
    def my_view(request, user_id):
        ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кеша
            cache_key = generate_cache_key(prefix, func.__name__, *args, **kwargs)
            
            # Пытаемся получить результат из кеша
            result = cache.get(cache_key)
            
            # Если результат не найден в кеше, вызываем функцию
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """
    Инвалидирует все ключи кеша, соответствующие шаблону
    """
    keys = cache.keys(pattern)
    if keys:
        cache.delete_many(keys)

def cache_page_data(key, timeout=300):
    """
    Декоратор для кеширования данных страницы
    
    Пример использования:
    @cache_page_data('home_page_data', 3600)
    def get_home_page_data():
        ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Пытаемся получить данные из кеша
            data = cache.get(key)
            
            # Если данные не найдены в кеше, вызываем функцию
            if data is None:
                data = func(*args, **kwargs)
                cache.set(key, data, timeout)
            
            return data
        return wrapper
    return decorator

class QuerySetCacheMixin:
    """
    Миксин для кеширования результатов QuerySet
    
    Пример использования:
    class MyModel(QuerySetCacheMixin, models.Model):
        ...
    """
    @classmethod
    def cached_objects(cls, timeout=300):
        """
        Возвращает все объекты модели из кеша или из базы данных
        """
        cache_key = f"all_{cls.__name__.lower()}"
        objects = cache.get(cache_key)
        
        if objects is None:
            objects = list(cls.objects.all())
            cache.set(cache_key, objects, timeout)
        
        return objects
