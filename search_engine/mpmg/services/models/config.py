from django.db import models

class Config(models.Model):
    ALGORITHMS = (
        ('BM25', 'Okapi BM-25'),
        ('DFR', 'Divergence from Randomness (DFR)'),
        ('DFI', 'Divergence from Independence (DFI)'),
        ('LMD', 'LM Dirichlet'),
    )
    algorithm = models.CharField(max_length=50, choices=ALGORITHMS, blank=False, default='BM25')

    