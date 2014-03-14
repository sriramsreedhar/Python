#!/usr/bin/python
import paramiko
import threading
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('puppet-agent', username='sriram', password='*****')
stdin, stdout, stderr = ssh.exec_command("hostname")
#out=stdout.readlines()
#print (out)
#data = stdout.read.splitlines()
data=stdout.readlines()
for line in data:
	print line
