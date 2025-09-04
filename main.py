#coding=utf-8
import requests
import os
from icalendar import Calendar, Event, Alarm
from datetime import datetime, date, timedelta
from login import Login

class CalendarExporter:
	def __init__(self, cookie, studentID, locale='zh_MO'):
		self.cookie = cookie
		self.studentID = studentID
		self.locale = locale
		self.headers = {
			'Cookie': cookie,
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
			'Referer': 'https://classtimetable-coes-wmweb.must.edu.mo/my-class-timetable-student',
			'Sec-CH-UA': '"Google Chrome";v="99", "Chromium";v="99", ";Not A Brand";v="99"',
			'Sec-CH-UA-Mobile': '?0',
			'Sec-CH-UA-Platform': '"Windows"',
			'Sec-Fetch-Dest': 'empty',
			'Sec-Fetch-Mode': 'cors',
			'Sec-Fetch-Site': 'same-origin',
			'X-Requested-With': 'XMLHttpRequest',
		}

	def export(self, termCode, trigger=30):
		timeTable_url = f'https://classtimetable-coes-wmweb.must.edu.mo/class-timetable-api/lessons/student-exam-webs?lang={self.locale}&termCode={termCode}&startDate={date.today().replace(year=date.today().year - 1).isoformat()}&endDate={date.today().replace(year=date.today().year + 1).isoformat()}'
		cal = Calendar()
		request = requests.get(timeTable_url, headers=self.headers)
		lessons = request.json()['model']['lesson']
		if not lessons:
			print('[Error] No data found')
			exit()
		else:
			print('Success: ' + str(len(lessons)) + ' lessons found')
		for i in lessons:
			event = Event()
			alert = Alarm()
			
			if self.locale == 'en_US':
				event.add('summary', i['courseEnName'])
				event.add('location', i['roomEngDesc'])
				event.add('description', 'TeacherName: ' + i['teacherEnName'])
				alert.add('description', 'Class Reminder')
			else:
				event.add('summary', i['courseName'])
				event.add('location', i['roomChnDesc'])
				event.add('description', '教師姓名: ' + i['teacherName'])
				alert.add('description', '上課提醒')

			startTime = datetime.strptime(i['lessonDate'] + i['lessonStartTime'], '%Y-%m-%d%H:%M')
			event.add('dtstart', startTime)
			endTime = datetime.strptime(i['lessonDate'] + i['lessonEndTime'], '%Y-%m-%d%H:%M')
			event.add('dtend', endTime)
			
			event.add('dtstamp', datetime.today().date(), parameters={'VALUE': 'DATE'})
			alert.add('action', 'DISPLAY')
			alert.add('trigger', timedelta(minutes=-trigger))
			event.add_component(alert)
			cal.add_component(event)
			
		output_dir = './output'
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		if self.locale == 'en_US':
			with open(f'{output_dir}/{self.studentID}_{termCode}_en.ics', 'wb') as f:
				f.write(cal.to_ical())
			print(f'Success: {self.studentID}_{termCode}_en.ics created')
		else:
			with open(f'{output_dir}/{self.studentID}_{termCode}.ics', 'wb') as f:
				f.write(cal.to_ical())
			print(f'Success: {self.studentID}_{termCode}.ics created')


if __name__ == '__main__':
	try:
		termCode = os.environ['TERM']
	except:
		import config
		termCode = config.termCode

	for i in termCode.split(','):
		if len(i) != 4:
			print('[Error] 学期代码不合法')
			exit()

	try:
		username = os.environ['USERNAME']
		password = os.environ['PASSWORD']
	except:
		import config
		username = config.username
		password = config.password


	login_obj = Login(username, password)
	driver = login_obj.get_driver()
	driver.get('https://classtimetable-coes-wmweb.must.edu.mo/my-class-timetable-student')
	cookies = driver.get_cookies()
	table_cookie = ''
	for i in cookies:
		if i['name'] == 'wm.class-timetable.sid':
			table_cookie = 'wm.class-timetable.sid=' + i['value']
			break
	if table_cookie == '':
		print('[Error] 请检查账号密码是否正确')
		login_obj.close()
		exit()

	exporter = CalendarExporter(table_cookie, locale=os.environ.get('LOCALE', ''), studentID=username)
	for i in termCode.split(','):
		exporter.export(i, trigger=int(os.environ.get('ALERT')))
	login_obj.close()

