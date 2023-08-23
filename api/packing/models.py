from django.db import models


class PalleteType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Pallete(models.Model):
    STATUS_CHOICES = (
        ('created', 'created'), 
        ('in_process', 'in progress'),
        ('finished', 'finished'),
    )

    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    max_weight = models.FloatField()
    type = models.ForeignKey(PalleteType, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    active = models.BooleanField(default=False)

    def get_current_weight(self):
        return self.item_set.aggregate(
            current_weight=models.Sum('weight')
        )['current_weight'] or 0

    def will_be_overweight(self, item_weight, current_weight=None):
        if current_weight is None:
            current_weight = self.get_current_weight()

        return current_weight + item_weight > self.max_weight


class Item(models.Model):
    external_id = models.CharField(max_length=100)
    pallete = models.ForeignKey(Pallete, on_delete=models.CASCADE)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    weight = models.FloatField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    rotate = models.BooleanField()
    need_edge_l = models.BooleanField()
    complete_edge_l = models.BooleanField()
    need_edge_t = models.BooleanField()
    complete_edge_t = models.BooleanField()
    need_edge_r = models.BooleanField()
    complete_edge_r = models.BooleanField()
    need_edge_b = models.BooleanField()
    complete_edge_b = models.BooleanField()
    xnc_need = models.BooleanField()

