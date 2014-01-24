
import urllib
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb

NO_DEVICE_NAMED = 'no_device_name'

def device_key(device_name = NO_DEVICE_NAMED):
	"""constructs Datastore key for SensorRecord entity with device_name """
	return ndb.Key('DeviceGroup', device_name)


class SensorRecord(ndb.Model) :
	"""Models a single PinRead from an Arduino with record creation time,  sensor min/max, and Device name"""
	sensormin = ndb.IntegerProperty()
	sensormax = ndb.IntegerProperty()
	sensorreading = ndb.IntegerProperty()
	recordentrytime = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def sensorRecordQuery_by_device(cls,device_name):
			device_readings_list = []
			device_records_query = SensorRecord.query(
			ancestor = device_key(device_name)).order(-SensorRecord.recordentrytime)
			# device_records is a list object only returns sensor reading and time for parsing. 
			device_records = device_records_query.fetch( projection=[SensorRecord.sensorreading, SensorRecord.recordentrytime])

		#create methods for pulling different streams of data out for processing. 
			for device_record in device_records:
				device_readings_list.append(device_record.sensorreading)
			return device_readings_list

class MainHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write('hello world')

class CreateRecordHandler(webapp2.RequestHandler):
    
    def get(self):
    	# populates datastore Model Objects with GET Params and creates Datastore Entity
        self.response.headers['Content-Type'] = 'text/plain'

        device_name = self.request.GET['devicename']


        r = SensorRecord(parent = device_key(device_name),
        				sensorreading = int(self.request.GET['sensorreading']),
        				sensormin = int(self.request.GET['sensormin']),
        				sensormax = int(self.request.GET['sensormax']))
        r_key= r.put()



class ReadRecordsHandler(webapp2.RequestHandler):

	def get(self): 
		this = self
		this.response.headers['Content-Type'] = 'text/plain'
		#self.response.write(self.request.GET['devicename'])
		try:
			device_name= self.request.GET['devicename']

		except KeyError:
			self.response.write ('NO DEVICE PARAMETER SUBMITTED')
		else:
			self.response.write(
			SensorRecord.sensorRecordQuery_by_device(device_name))


app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/write', CreateRecordHandler),
	('/read', ReadRecordsHandler)
], debug=True)
 