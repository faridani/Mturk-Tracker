from django.db import models

class HitGroup_Status(models.Model):
    id = models.AutoField()
    mturk_group_id = models.DecimalField(max_digits=20, blank = False, null = False)
    crawl_id = models.DecimalField(max_digits=20, blank = False, null = False)
    hits_available = models.DecimalField(max_digits=10, blank = False, null = False)
    page_number = models.DecimalField(max_digits=5, blank = False, null = False)
    inpage_position = models.DecimalField(max_digits=5, blank = False, null = False)
    hit_expiration_date = models.DateTimeField(null = True)

    objects = models.Manager()

    def __str__(self):
        return self.id + "|" + self.mturk_group_id + "|" + self.mturk_group_id