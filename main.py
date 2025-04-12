#coding=utf-8
import requests
import os
from icalendar import Calendar, Event, Alarm
from datetime import datetime, date, timedelta
import login


def classTimeTable(cookie, termCode):
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
	# request = requests.get('https://classtimetable-coes-wmweb.must.edu.mo/class-timetable-api/common/terms?lang=zh_MO', headers=headers)
	
	# if request.status_code != 200:
	# 	print('Failed to get data from server')
	# 	exit()
	

	timeTable_url = 'https://classtimetable-coes-wmweb.must.edu.mo/class-timetable-api/lessons/student-exam-webs?lang=zh_MO&termCode='+ termCode +'&startDate=' +  date.today().replace(year=date.today().year - 1).isoformat() + '&endDate=' + date.today().replace(year=date.today().year + 1).isoformat()
	# print(timeTable_url)


	cal = Calendar()

	request = requests.get(timeTable_url, headers=headers)
	# print(request.status_code)
	# print(request.text)

	if(request.json()['model']['lesson'] == []):
		print('Error: No data found')
		exit()
	else:
		print('Success: ' + str(len(request.json()['model']['lesson'])) + ' lessons found')

	for i in request.json()['model']['lesson']:
		event = Event()

		event.add('summary', i['courseName'])
		# convert iso date and time to ical format

		startTime = datetime.strptime(i['lessonDate'] + i['lessonStartTime'], '%Y-%m-%d%H:%M')
		event.add('dtstart', startTime)
		endTime = datetime.strptime(i['lessonDate'] + i['lessonEndTime'], '%Y-%m-%d%H:%M')
		event.add('dtend', endTime)
		event.add('location', i['roomChnDesc'])
		event.add('description', 'TeacherName:' + i['teacherName'])
		event.add('dtstamp', datetime.today().date(), parameters={'VALUE': 'DATE'})

		# alarm 30 minutes before class
		alart = Alarm()
		alart.add('action', 'DISPLAY')
		alart.add('description', '上課提醒')
		alart.add('trigger', timedelta(minutes=-30))
		event.add_component(alart)

		cal.add_component(event)
	
	f = open('output_'+termCode+'.ics', 'wb')
	f.write(cal.to_ical())
	f.close()
	

if __name__ == '__main__':
	try:
		termCode = os.environ['TERM']
	except:
		import config
		termCode = config.termCode

	for i in termCode.split(','):
		if len(i) != 4:
			print('Error: 学期代码不合法')
			exit()

	try:
		driver = login.login(os.environ['USERNAME'], os.environ['PASSWORD'])
	except:
		import config
		driver = login.login(config.username, config.password)


	# enter the 2nd page
	driver.get('https://classtimetable-coes-wmweb.must.edu.mo/my-class-timetable-student')
	
	cookies = driver.get_cookies()
	# find exact cookie
	for i in cookies:
		if i['name'] == 'wm.class-timetable.sid':
			table_cookie = 'wm.class-timetable.sid=' + i['value']
			break
	
	if table_cookie == '':
		print('Error: 请检查账号密码是否正确')
		exit()

	for i in termCode.split(','):
		classTimeTable(table_cookie, i)

	driver.close()
	
