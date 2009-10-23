from django.core.management.base import BaseCommand
from mturk.main.management.commands import clean_duplicates

class Command(BaseCommand):
    help = 'Cleans corrupted data'

    def handle(self, **options):

        clean_duplicates()
        
        
