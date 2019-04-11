#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import ldap
import ldap.modlist
import pprint

class exLdaps:
	"""
	ldap 라이브러리를 사용하여 만든 클래스입니다.
	"""

	def __init__(self, server, user, basedn, password):
		"""
		ldap의 서버초기셋팅
		"""
		self.dn = "{0},{1}".format(user, basedn)
		try:
			self.conn = ldap.initialize(server)
		except Exception as e:
			print e
			sys.exit(1)
		self.bind(password)

	def bind(self, password):
		"""
		ldap 서버에 bind 하는 함수
		"""
		try:
			self.conn.simple_bind_s(self.dn, password)
		except ldap.INVALID_CREDENTIALS:
			try:       	
				self.conn.simple_bind(self.dn, password)
			except:			
				print("Invalid credentials")
				sys.exit(1)
		except ldap.SERVER_DOWN:
			print("Server unavailable")
			sys.exit(1)

	def search(self, dn=None, flter="(uid=*)", attrs=["*"]):
		"""
		ldap을 search하는 함수
		"""
		if not dn:
			dn = self.dn
		results = []
		try:
			results = self.conn.search_s(dn, ldap.SCOPE_ONELEVEL, flter, attrs)
			#results.sort()
		except Exception as e:
			print(e)
			return None
		return results

	def addUser(self, dn=None, userlist={}):
		"""
		ldap에 user를 추가하는 함수
		"""
		if type(userlist) != dict:
			print("userlist가 리스트형태가 아닙니다.!")
			return None
		if not dn:
			print("not dn")
			return None
		try:
			ldif=ldap.modlist.addModlist(userlist)
			self.conn.add_s(dn,ldif)
		except Exception as e:
			print(e)
			sys.exit(1)
		return True

	def unbind(self):
		"""
		ldap을 bind 해제하는 함수
		"""
		try:		
			self.conn.unbind_s()
		except:
			try:
				self.conn.unbind()
			except Exception as e:
				print e
				sys.exit(1)


def maxUidnum(results=[], filternum=1000):
	"""
	ldap의 모든 결과중 fiternum 보다 
	작은 uidNumber 리스트들 중  가장 큰값을 가져온다.
	"""
	if not results:
		return None
	uidNum=[]
	for i in results:
		uidNum.append(i[1]["uidNumber"][0])
	if not uidNum:
		return None
	numlist=map(int, uidNum)
	numlist=list(filter(lambda x: x < filternum, numlist))
	#del max # 'list' object is not callable 오류가 날때 실행.
	num=max(numlist)
	return num

def settingUserlist(name, sung, num):
	"""
	ldap의 user를 추가하기 위해 필요한 유저 구성 함수	
	"""
	userlist = {
			"cn": "test add",
			"gecos": "test",
			"gidNumber": "1055",
			"givenName": "test",
			"loginShell": "/bin/bash",
			"homeDirectory": "/home/test",
			"mail": "test@example.com",
			"objectClass": ["top", "person", "organizationalPerson", "inetorgperson", "posixAccount"],			
			"sn": "add",
			"uid": "test",	
			"uidNumber": "1061",
	}

	userlist['cn'] = name + " " + sung
	userlist['gecos'] = name
	userlist['givenName'] = name
	userlist['homeDirectory'] = "home/"+name
	userlist['mail'] = name+"@example.com"
	userlist['sn'] = sung
	userlist['uid'] = name
	userlist['uidNumber'] = str(num)
	return userlist

def main():
	server = "ldap//example.com:389" #ldap://servername:port
	rootuser = "uid=admin"
	rootbasedn = "ou=administrators,ou=topologymanagement,o=netscaperoot"
	password = "1234" #password
	l =  exLdaps(server, rootuser, rootbasedn, password)

	searchdn= "ou=People,dc=example,dc=com"
	results=l.search(searchdn)
	pprint.pprint(results)

	num = maxUidnum(results, 2000)
	print(num)
	num += 1
	print num

	name, sung= "will", "bob"
	adddn  = "uid={0},ou=People,dc=example,dc=com".format(name)
	userlist = settingUserlist(name, sung, num)
	print userlist
	s = l.addUser(adddn, userlist)
	print s
	if s:
		results=l.search(searchdn)
		pprint.pprint(results)
	l.unbind()

if __name__ == '__main__':
	main()
