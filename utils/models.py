from django.db import models
from django.core.cache import cache

class CounterCacheManager(models.Manager):
    """
    Менеджер для моделей с кешированными счетчиками
    """
    def increment(self, name, amount=1):
        """
        Увеличивает счетчик с указанным именем
        """
        counter, created = self.get_or_create(name=name)
        counter.value += amount
        counter.save()
        
        # Обновляем кеш
        cache_key = f"counter_{name}"
        cache.set(cache_key, counter.value)
        
        return counter.value
    
    def get_value(self, name, default=0):
        """
        Возвращает значение счетчика с указанным именем
        """
        # Пытаемся получить значение из кеша
        cache_key = f"counter_{name}"
        value = cache.get(cache_key)
        
        if value is None:
            try:
                counter = self.get(name=name)
                value = counter.value
                # Обновляем кеш
                cache.set(cache_key, value)
            except self.model.DoesNotExist:
                value = default
        
        return value

class Counter(models.Model):
    """
    Модель для хранения счетчиков
    """
    name = models.CharField(max_length=100, unique=True)
    value = models.IntegerField(default=0)
    
    objects = CounterCacheManager()
    
    def __str__(self):
        return f"{self.name}: {self.value}"
