#coding=utf-8
import requests
import os
from icalendar import Calendar, Event
from datetime import datetime, date




if __name__ == '__main__':
	# try get cookie from environment variable, if not found, use the cookie from config.py
	try:
		cookie = os.environ['COOKIE']
	except:
		import config
		cookie = config.cookie


	# print(cookie)
	headers = {
		'Cookie': cookie,
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Referer': 'https://classtimetable-coes-wmweb.must.edu.mo/my-class-timetable-student',
		'Sec-CH-UA': '"Google Chrome";v="99", "Chromium";v="99", ";Not A Brand";v="99"',
		'Sec-CH-UA-Mobile': '?0',
		'Sec-CH-UA-Platform': '"Windows"',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'Connection': 'keep-alive',
		'Host': 'classtimetable-coes-wmweb.must.edu.mo',
		'Dnt': '1',
		'X-Requested-With': 'XMLHttpRequest',
	}

	# get latest term code
	request = requests.get('https://classtimetable-coes-wmweb.must.edu.mo/class-timetable-api/common/terms?lang=zh_MO', headers=headers)
	
	if request.status_code != 200:
		print('Failed to get data from server')
		exit()
	
	termCode = request.json()["model"][0]
	# print(termCode)


	timeTable_url = 'https://classtimetable-coes-wmweb.must.edu.mo/class-timetable-api/lessons/student-exam-webs?lang=zh_MO&termCode='+ termCode +'&startDate=' +  date.today().isoformat() + '&endDate=' + date.today().replace(year=date.today().year + 1).isoformat()
	# print(timeTable_url)


	cal = Calendar()

	request = requests.get(timeTable_url, headers=headers)
	# print(request.status_code)
	# print(request.text)


	for i in request.json()['model']['lesson']:
		event = Event()

		# print(i['courseName'])
		event.add('summary', i['courseName'])
		# convert iso date and time to ical format

		startTime = datetime.strptime(i['lessonDate'] + i['lessonStartTime'], '%Y-%m-%d%H:%M')
		event.add('dtstart', startTime)
		endTime = datetime.strptime(i['lessonDate'] + i['lessonEndTime'], '%Y-%m-%d%H:%M')
		event.add('dtend', endTime)
		event.add('location', i['roomChnDesc'])
		event.add('description', 'TeacherName:' + i['teacherName'])
		event.add('dtstamp', datetime.today().date(), parameters={'VALUE': 'DATE'})

		cal.add_component(event)


	print(cal.to_ical().decode('utf-8')) 
	
	f = open('output.ics', 'wb')
	f.write(cal.to_ical())
	f.close()
	


