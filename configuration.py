# -*- coding: utf-8 -*-

import os
import codecs
from ConfigParser import SafeConfigParser


class Config(object):
	_instance = None

	cfg_vals = {}

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
		return cls._instance


	def __init__(self, prog_filename):
		self.fn = os.path.splitext(os.path.abspath(prog_filename))[0] + '.ini'

		if not os.access(self.fn, os.R_OK):
			raise ConfigException("No se puede leer %s" % self.fn)

		self.parser = SafeConfigParser()
		try:
			codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)
			fp = codecs.open(self.fn, 'r', encoding='utf-8')
			self.parser.readfp(fp)
		except:
			raise ConfigException(u"Fichero de configuración debe ser UTF-8: %s" % self.fn)

		self.read()
		self.validate()


	def read(self):
		try:
			self.cfg_vals['SCH_HOUR' ] = int(self.parser.get('schedule_settings', 'sch_hour'))
			self.cfg_vals['SCH_MIN'  ] = int(self.parser.get('schedule_settings', 'sch_minute'))
			self.cfg_vals['SMTP_SERV'] = self.parser.get('mail_settings', 'smtp_server')
			self.cfg_vals['SMTP_USER'] = self.parser.get('mail_settings', 'smtp_user')
			self.cfg_vals['SMTP_PASS'] = self.parser.get('mail_settings', 'smtp_pass')
			self.cfg_vals['MAIL_FROM'] = self.parser.get('mail_settings', 'mail_from')
			self.cfg_vals['MAIL_DEST'] = self.parser.get('mail_settings', 'mail_dest')
			self.cfg_vals['MAIL_BODY'] = self.parser.get('mail_contents', 'mail_body')
		except Exception as e:
			raise ConfigException(str(e))

        
	def validate(self):
		def isEmpty(str):
			if str is None or str == '': return True
			return False

		for k, v in self.cfg_vals.items():
			if isEmpty(v) and k != 'MAIL_BODY':
				raise ConfigException("El valor de \'%s\' no se ha definido." % k.lower())

		if self.cfg_vals['SCH_HOUR'] > 23 or self.cfg_vals['SCH_MIN'] > 59:
			raise ConfigException(u"La hora configurada no es válida")
	

	def get(self, key):
		return self.cfg_vals[key]


	def set(self, key, val):
		self.cfg_vals[key] = val


	def getFilename(self):
		return self.fn

	def save(self):
		self.validate()

		self.parser.set('schedule_settings', 'sch_hour', "%s" % self.cfg_vals['SCH_HOUR'])
		self.parser.set('schedule_settings', 'sch_minute', "%s" % self.cfg_vals['SCH_MIN'])
		self.parser.set('mail_settings', 'smtp_server', self.cfg_vals['SMTP_SERV'])
		self.parser.set('mail_settings', 'smtp_user', self.cfg_vals['SMTP_USER'])
		self.parser.set('mail_settings', 'smtp_pass', self.cfg_vals['SMTP_PASS'])
		self.parser.set('mail_settings', 'mail_from', self.cfg_vals['MAIL_FROM'])
		self.parser.set('mail_settings', 'mail_dest', self.cfg_vals['MAIL_DEST'])
		self.parser.set('mail_contents', 'mail_body', self.cfg_vals['MAIL_BODY'])

		try:
			codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)
			fp = codecs.open(self.fn, 'wb', encoding='utf-8')
			self.parser.write(fp)
			fp.close()
		except:
			raise ConfigException(u"Error al escribir: %s" % self.fn)


class ConfigException(Exception):
	def __init__(self, msg):
		self.message = "ERR_CONFIG: "+ msg
