import os
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from settings import MODELS_DIR


class TypeModel(models.Model):
    name = models.CharField(max_length=250)
    graph_dir = models.CharField(max_length=250, default="")


class AnnRun(models.Model):
    name = models.CharField(max_length=120, default='')
    status = models.CharField(max_length=120, default='Ready')
    datetime = datetime.now


class EntityAnn(models.Model):
    ann_run = models.ForeignKey(AnnRun, on_delete=models.CASCADE)
    results = models.CharField(max_length=500, default='')
    col_id = models.PositiveIntegerField()
    model = models.ForeignKey(on_delete=models.CASCADE)

    @property
    def cells(self):
        return Cell.objects.filter(entity_ann=self)

    def __str__(self):
        return str(self.id) + '> ' + self.ann_run.name


class Cell(models.Model):
    entity_ann = models.ForeignKey(EntityAnn, on_delete=models.CASCADE)
    text_value = models.TextField()

    @property
    def entities(self):
        return Entity.objects.filter(cell=self)

    def __str__(self):
        return self.entity_ann.ann_run.name + ' - ' + self.text_value


class Entity(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    entity = models.CharField(max_length=250)

    @property
    def classes(self):
        return CClass.objects.filter(entity=self)

    class Meta:
        verbose_name_plural = "Entities"

    def __str__(self):
        return self.cell.text_value + ' - ' + self.entity


class CClass(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    cclass = models.CharField(max_length=250)

    class Meta:
        verbose_name_plural = "CClasses"

    def __str__(self):
        return self.entity.entity + ' - ' + self.cclass

