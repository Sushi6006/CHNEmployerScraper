import csv

lines = []
with open('db.csv', 'r') as f:
	for line in f.readlines():
		lines.append(line.split(','))

with open('db.csv', 'w') as f:
	for line in lines:
		phone = line[1]
		phone = phone[0:4] + ' ' + phone[4:7] + ' ' + phone[7:]
		f.write("{},{},{},{}".format(line[0], phone, line[2], line[3]))
