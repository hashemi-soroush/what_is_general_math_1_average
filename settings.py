import os

number_of_threads = 40
first_student_id = 93100000
last_student_id =  93101200
# TODO:
# student_id_list_file_path = None 

url = 'http://mehr.sharif.ir/~calculus/gm1_2017/Results.php?course=eng'
method = 'POST'
headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 
	'Accept-Encoding': 'gzip, deflate', 
	'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,fa;q=0.7', 
	'Cache-Control': 'max-age=0', 
	'Connection': 'keep-alive', 
	'Content-Length': '11', 
	'Content-Type': 'application/x-www-form-urlencoded', 
	'Host': 'mehr.sharif.ir', 
	'Origin': 'http://mehr.sharif.ir', 
	'Referer': 'http://mehr.sharif.ir/~calculus/gm1_2017/Results.php?course=eng', 
	'Upgrade-Insecure-Requests': '1', 
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36', 
}
query_string = 'course=eng'
form_data = 'ID={0}'

retry_count = 10
timeout = (2, 2)

if not os.path.exists('res_files'):
	os.mkdir('res_files')
res_file_path_template = os.path.join('res_files', 'res_{0}_to_{1}.csv')
log_file_path_template = os.path.join('res_files', 'bad_ids_{0}_to_{1}.csv')