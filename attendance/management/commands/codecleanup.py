from django.core.management.base import BaseCommand, CommandError

from attendance.models import *

class Command(BaseCommand):
	help = "Command to start the WebSockets Server"

	def add_arguments(self, parser):
		pass
		#parser.add_argument('port', nargs="+", type=int)
		#parser.add_argument('iterations', nargs="+", type=int)
		#parser.add_argument('delay', nargs="+", type=int)

	def handle(self, *args, **options):
		#PUT CODE HERE
		print("Hello World")
