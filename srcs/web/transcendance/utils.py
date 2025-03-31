import rom # type: ignore
import inspect
import logging
import time
import importlib

logger = logging.getLogger('default')

def add_methods_rom(module_name):
	module = importlib.import_module(module_name)
	classes = [obj for _, obj in inspect.getmembers(module, inspect.isclass) if issubclass(obj, rom.Model)]

	def save(self, *args, max_retry=5, **kwargs):
		for _ in range(max_retry):
			try:
				return super(self.__class__, self).save(*args, **kwargs)
			except rom.exceptions.DataRaceError as e:
				logger.warning(f"[{self.__class__.__name__}] DataRace detected on save (retrying)")
				self.refresh(force=True)
				time.sleep(0.01)
			except rom.exceptions.EntityDeletedError as e:
				logger.warning(f"[{self.__class__.__name__}] EntityDeletedError detected on save (ignoring)")
				return
		logger.error(f"[{self.__class__.__name__}] Save failed after {max_retry} retries due to DataRace.")

	def delete(self, *args, max_retry=5, **kwargs):
		for _ in range(max_retry):
			try:
				return super(self.__class__, self).delete(*args, **kwargs)
			except rom.exceptions.DataRaceError as e:
				logger.warning(f"[{self.__class__.__name__}] DataRace detected on delete (retrying): {e}")
				self.refresh(force=True)
				time.sleep(0.01)
		logger.error(f"[{self.__class__.__name__}] Delete failed after {max_retry} retries due to DataRace.")

	def update(self, max_retry=5, **kwargs):
		for _ in range(max_retry):
			try:
				for key, value in kwargs.items():
					setattr(self, key, value)
				return super(self.__class__, self).save()
			except rom.exceptions.DataRaceError as e:
				logger.warning(f"[{self.__class__.__name__}] DataRace detected on update (retrying): {e}")
				self.refresh(force=True)
				time.sleep(0.01)
		logger.error(f"[{self.__class__.__name__}] Update failed after {max_retry} retries due to DataRace.")
	
	functions = [save, update, delete]
	for cls in classes:
		if hasattr(cls, '_DATARACE_PROTECT'):
			continue
		for func in functions:
			setattr(cls, func.__name__, func)
			# logger.info(f"function {func.__name__} surcharged in {name}")
		cls._DATARACE_PROTECT = True
