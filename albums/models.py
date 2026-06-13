import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_member = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    cover_photo = models.ForeignKey(
        'EventPhoto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_for_event',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
    )                                                  # 建立活動的老師
    created_at = models.DateTimeField(auto_now_add=True)  # 建立時間

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class EventPhoto(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='photos'
    )                                                  # 這張照片屬於哪個活動
    image = models.ImageField(upload_to='events/%Y/%m/')  # 照片
    caption = models.CharField(max_length=300, blank=True)  # 照片說明
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )                                                  # 上傳照片的老師
    uploaded_at = models.DateTimeField(auto_now_add=True)   # 上傳時間

    def __str__(self):
        return f'{self.event.title} - {self.uploaded_at}'


class EventDocument(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    title = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def ext(self):
        return os.path.splitext(self.file.name)[1].lower().lstrip('.')

    def __str__(self):
        return f'{self.event.title} - {self.title}'
