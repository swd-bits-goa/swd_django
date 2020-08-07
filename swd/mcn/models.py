from django.db import models


class MCNApplication(models.Model):
    """
    Stores MCN Application of a single student with the documents.
    """

    def __str__(self):
        pass

    class Meta:
        verbose_name = 'MCN Application'
        verbose_name_plural = 'MCN Applications'


class MCNApplicationPeriod(models.Model):
    """
    Stores time period when MCN Application portals were opened and closed.
    """

    def __str__(self):
        pass

    class Meta:
        verbose_name = 'MCN Application Period'
        verbose_name_plural = 'MCN Application Periods'