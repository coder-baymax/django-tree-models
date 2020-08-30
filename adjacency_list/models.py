from datetime import datetime

from django.db import models


class Node(models.Model):
    name = models.TextField(null=True, blank=True)
    update_time = models.DateTimeField(null=False, blank=False, default=datetime.utcnow)
    create_time = models.DateTimeField(null=False, blank=False, default=datetime.utcnow)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name="sons")
