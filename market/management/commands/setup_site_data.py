from django.contrib.sites.models import Site
from django.db import transaction
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Saves site name and domain name in database"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Writing Sites framework data to the database")

        mysite = Site.objects.get_current()
        mysite.domain = 'markedsspillet.dk'
        mysite.name = 'Markedsspillet'
        mysite.save()
