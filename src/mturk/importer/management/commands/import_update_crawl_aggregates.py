from django.core.management.base import BaseCommand
from mturk.main.management.commands import update_crawl_agregates

class Command(BaseCommand):


    def handle(self, **options):
        
        update_crawl_agregates()