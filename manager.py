from client import Client
from render import Render 

class Manager(object):

	def __init__(self):
		self.client = Client()

	def refresh_map(self):
		status = self.client.get_lift_status()
		return Render(status).render()

	def refresh_map_and_etag(self):
		status = self.client.get_lift_status()
		return Render(status).render_and_etag()