from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Config(models.Model):
    ALGORITHMS = (
        ('BM25', 'Okapi BM25'),
        ('DFR', 'Divergence from Randomness (DFR)'),
        ('DFI', 'Divergence from Independence (DFI)'),
        ('IB', 'Information based model'),
        ('LMDirichlet', 'Language Model: Dirichlet priors'),
        ('LMJelinekMercer', 'Language Model: Jelinek-Mercer smoothing method'),
    )
    algorithm = models.CharField(max_length=50, choices=ALGORITHMS, blank=False, default='BM25')
    num_repl = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(50), MinValueValidator(0)])
    max_result_window = models.PositiveIntegerField(default=10000, validators=[MinValueValidator(1)])

    