class UserData:
	def __init__(self, str = None):
		self.name = ''
		self.score = 0
		self.level = 0
		if str is not None:
			self.from_string(str)

	def from_string(self, str):
		values = str.split(',')
		self.name = values[0]
		self.score = int(values[1])
		self.level = int(values[2])


	def to_string(self):
		return f'{self.name},{self.score},{self.level}'