from django.db import models


class EEUser(models.Model):
    class UserType(models.TextChoices):
        supervisor = 'supervisor', 'Руководитель'
        worker = 'worker', 'Рабочий'

    fullname = models.CharField(max_length=255, verbose_name='ФИО')
    user_type = models.CharField(max_length=255, verbose_name='Тип пользователя', choices=UserType.choices)
    phone = models.CharField(verbose_name='Телефон', max_length=20)
    tg_id = models.BigIntegerField(verbose_name='Телеграм айди', default=0)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Task(models.Model):
    class Status(models.TextChoices):
        created = 'created', 'Создано'
        progress = 'progress', 'В процессе'
        completed = 'completed', 'Выполнено'

    class FileType(models.TextChoices):
        photo = 'photo', 'Фото'
        document = 'document', 'Документ'
        video = 'video', 'Видео'
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    file_id = models.CharField(verbose_name='Файл айди', max_length=255, null=True)
    file_type = models.CharField(max_length=255, verbose_name='Тип файла', choices=FileType.choices, null=True)
    result = models.CharField(max_length=255, verbose_name='Результат', null=True)
    result_file_id = models.CharField(verbose_name='Файл результата айди', max_length=255, null=True)
    creator = models.ForeignKey('bot.EEUser', on_delete=models.CASCADE, verbose_name='Создатель',
                                related_name='tasks')
    message_id = models.BigIntegerField(verbose_name='Айди сообщения', default=0)
    executor = models.ForeignKey('bot.EEUser', on_delete=models.CASCADE, verbose_name='Исполнитель', null=True)
    created = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    finish_date = models.DateField(verbose_name='Дата окончания', null=True)
    status = models.CharField(max_length=255, verbose_name='Статус', choices=Status.choices, default=Status.created)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Поручение'
        verbose_name_plural = 'Поручения'
