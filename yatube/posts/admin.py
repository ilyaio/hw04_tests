from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    # По поводу коммментов мы уже общались в Slack. Я помню, что в методически
    # просят удалять, но они нужны мне для того, чтобы быстро вспомнить, что
    # делает данный код
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group'
                    )
    # Это позволит изменять поле group в любом посте
    list_editable = ('group',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

# При регистрации модели Post источником конфигурации для неё назначаем
# класс PostAdmin


admin.site.register(Post, PostAdmin)

admin.site.register(Group)
