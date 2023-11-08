from django.db import models


# Create your models here.
class ChatHistory(models.Model):
    room_name = models.CharField(max_length=99, null=True)
    message = models.TextField()

    def __str__(self) -> str:
        return f"{self.room_name} {self.message[:20]}"
