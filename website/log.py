from threading import Lock
from multiprocessing import Lock

class Log:
	__DEBUG_ONLY_THIS__ = False
	__DEBUG__ = True
	__INFO__  = True
	__WARN__  = True
	__ERROR__ = True
	
	def __init__(self, func_name, print_lock = None, parent_log = None):
		if (print_lock != None):
			self.print_lock = print_lock
			self.func_name  = func_name
			
		elif (parent_log != None):
			self.print_lock = parent_log.print_lock
			self.func_name  = parent_log.func_name + " - " + func_name
			
	def debug(self, string):
		if self.__DEBUG__ and not self.__DEBUG_ONLY_THIS__:
			with self.print_lock:
				print ("[DEBUG] <" + self.func_name + ">: " + string)

	def info(self, string):
		if self.__INFO__ and not self.__DEBUG_ONLY_THIS__:
			with self.print_lock:
				print ("[INFO] <" + self.func_name + ">: " + string)
	
	def warn(self, string):
		if self.__WARN__:
			with self.print_lock:
				print ("[WARN] <" + self.func_name + ">: " + string)
				
	def error(self, string):
		if self.__ERROR__:
			with self.print_lock:
				print ("[ERROR] <" + self.func_name + ">: " + string)
			
	def debug_only_this(self, string):
		if self.__DEBUG__ or self.__DEBUG_ONLY_THIS__:
			with self.print_lock:
				print ("[DEBUG ONLY THIS] <" + self.func_name + ">: " + string)