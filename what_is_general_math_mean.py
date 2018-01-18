import multiprocessing
import requests
from lxml import etree
import csv

import settings

def get_html(student_id):
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
	parser = etree.XMLParser(recover=True)
	html_etree = etree.fromstring(html_text, parser)
	grades = html_etree.xpath('//*[@id="M1Q1"]/text()')
	return grades

def get_grade(student_id):
	html_text = get_html(student_id)
	grades = parse(html_text)
	return grades

def save_results(grade_list, res_file_path):
	with open(res_file_path, 'a') as res_file:
		csv_writer = csv.writer(res_file)
		csv_writer.writerows(grade_list)

def save_logs(failed_list, log_file_path):
	return
	with open(log_file_path, 'a') as res_file:
		csv_writer = csv.writer(res_file)
		csv_writer.writerows(failed_list)

def get_grade_list(student_id_list):
	first_id = student_id_list[0]
	last_id = student_id_list[-1]

	res_file_path = settings.res_file_path_template.format(first_id, last_id)
	log_file_path = settings.log_file_path_template.format(first_id, last_id)

	grade_list = []
	failed_list = []
	counter = 0
	for i in range(first_id, last_id):
		counter += 1
		student_id = i
		print('checking {0} . . .'.format(student_id))

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

def get_student_id_list():
	start = settings.first_student_id
	end = settings.last_student_id
	count = settings.number_of_threads

	student_id_list = []
	step = int((end - start) / count)
	for i in range(count):
		student_id_list.append([start + i*step, start + (i+1)*step])
	student_id_list[-1] += list(range(student_id_list[-1][-1], end))

	return student_id_list

def attack():
	student_id_list = get_student_id_list()
	pool = multiprocessing.Pool(settings.number_of_threads)
	
	print('let\'s light up the party ...')

	pool.map(get_grade_list, student_id_list)
	pool.close()
	pool.join()

	print('')

def main():
	attack()

if __name__ == '__main__':
	main()
