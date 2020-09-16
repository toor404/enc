from django.db import models

class Device(models.Model):
    id = models.AutoField
    ip_address = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    sshport = models.IntegerField(default=22)

    VENDOR_CHOICES = (
        ('mikrotik', 'Mikrotik'),
        ('cisco', 'Cisco'),
        ('ransnet', 'Ransnet'),
        ('hored', 'Hored')
    )
    vendor = models.CharField(max_length=255, choices=VENDOR_CHOICES)

    def __str__(self):
        return "{} - {}".format(self.ip_address, self.hostname)

class Log(models.Model):
    target = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    time = models.DateTimeField(null=True)
    messages = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{} - {} - {}".format(self.target, self.action, self.status)