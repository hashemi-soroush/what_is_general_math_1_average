import os
from config import *

course_id_to_course_name = {
	1: 'calc1', 
	2: 'calc2', 
	3: 'diff', 
	4: 'eng'
}

# TODO:
# student_id_list_file_path = None 

number_of_threads = 40
retry_count = 10
timeout = (2, 2)

url = 'http://calculus.math.sharif.edu/gm2_2018/Results.php'
method = 'POST'
query_string = 'course={0}'.format(course_id_to_course_name[course])
form_data = 'ID={0}'
headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 
	'Accept-Encoding': 'gzip, deflate', 
	'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,fa;q=0.7', 
	'Cache-Control': 'max-age=0', 
	'Connection': 'keep-alive', 
	'Content-Length': '11', 
	'Content-Type': 'application/x-www-form-urlencoded', 
	'Host': 'calculus.math.sharif.edu', 
	'Origin': "http://calculus.math.sharif.edu", 
	'Referer': "http://calculus.math.sharif.edu/gm2_2018/Results.php?course=calc2", 
	'Upgrade-Insecure-Requests': '1', 
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36', 
}

if not os.path.exists('res_files'):
	os.mkdir('res_files')
marks_file_path_template = os.path.join('res_files', course_id_to_course_name[course] + '_marks_{0}_to_{1}.csv')
failures_file_path_template = os.path.join('res_files', course_id_to_course_name[course] + '_failures_{0}_to_{1}.csv')
