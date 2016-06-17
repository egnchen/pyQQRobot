#!/usr/bin/env python3
import json

class qqFriends():
	def __init__(self):
		self.f=dict()
		self.g=dict()
		self.d=dict()
		self.c=[]

	def parseFriends(self,j):
		if type(j) == str:
			j=json.loads(j)
		j=j['result']

		# category, uin & flag
		for e in j['friends']:
			self.f[e['uin']]=dict()
			self.f[e['uin']]['category']=e['categories']
			self.f[e['uin']]['flag']=e['flag']

		# marknames
		for e in j['marknames']:
			self.f[e['uin']]['markname']=e['markname']
			#self.f[e['uin']]['mType']=e['type']

		# vipinfo
		for e in j['vipinfo']:
			self.f[e['u']]['vip']=e['is_vip'] and e['vip_level']

		# user info
		for e in j['info']:
			self.f[e['uin']]['nickname']=e['nick']
			self.f[e['uin']]['face']=e['face']
			self.f[e['uin']]['flag']=e['flag']

		# categories
		for e in j['categories']:
			self.c.append(e['name'])

		# print(json.dumps(self.f,indent=2))
		# print(self.c)
	
	def parseGroups(self,j):
		if type(j) == str:
			j=json.loads(j)
		j=j['result']

		for e in j['gnamelist']:
			self.g[e['gid']]=dict()
			self.g[e['gid']]['flag']=e['flag']
			self.g[e['gid']]['name']=e['name']
			self.g[e['gid']]['code']=e['code']

		# print(self.g)

	def parseDiscus(self,j):
		if type(j) == str:
			j=json.loads(j)
		j=j['result']

		for e in j['dnamelist']:
			self.d[e['did']]=dict()
			self.d[e['did']]['name']=e['name']

		# print(self.d)