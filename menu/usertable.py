from menu.userdata import UserData
import os.path

class UserTable:

  COUNT = 10

  def __init__(self, file = None):
    self.table = [None] * self.COUNT
    self.file = file
    for i in range(self.COUNT):
      self.table[i] = UserData()
    if file is not None and os.path.exists('data/table.txt'):
      self.read()

  def read(self):
    fp = open(self.file, 'r')
    lines = fp.readlines()
    line_count = len(lines)
    for i in range(self.COUNT):
      if i == line_count:
        break
      user_data = self.table[i]
      user_data.from_string(lines[i])
    fp.close()

  def write(self):
    fp = open(self.file, 'w')
    for i in range(self.COUNT):
      s = self.table[i].to_string()
      fp.write(s)
      fp.write("\n")
    fp.close()

  def sort(self):
    self.table.sort(key = lambda x: x.score, reverse = True)