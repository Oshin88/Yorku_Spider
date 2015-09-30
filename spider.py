#from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
import urllib2
import cookielib
import requests
import re
import mechanize


class Spider(object):
	#initializer
	def __init__(self):
		pass

	#extract all the links from a websites provided given the url
	def get_links(self, url):
		uri_list = []
		source_code = requests.get(url)
		plain_txt = source_code.text
		soup = BeautifulSoup(plain_txt)
		for link in soup.findAll('a', {'target': '_new'}):
			href = link.get('href')
			uri_list.append(href)
			print(href)
		return uri_list

	#given the uri_list select the needed links to download the content
	def download_data(self, path, regex, file_ext, uri_list):
		i = 1
		for url in uri_list:
			match = re.search(regex, url)
			if match:
				print url
				f = urllib2.urlopen(url)
				data = f.read()
				full_path = path + str(i) + file_ext
				with open(full_path, "wb") as code:
					code.write(data)
				i += 1

	#get scrape data from the website 			
	def get_data(self, url, html_tag, html_param, param_val, key):
		data_list = []
		source_code = requests.get(url)
		plain_txt = source_code.text
		soup = BeautifulSoup(plain_txt)
		for item in soup.findAll(html_tag, {html_param: param_val}):
			data = item.get(key)
			data_list.append(data)
			print(data)
		return data_list

	#to access a YorkU login page for grades
	def log_in(self, url, user_id, password):
		browser = mechanize.Browser()
		cookiejar = cookielib.LWPCookieJar()
  		browser.set_cookiejar(cookiejar)
		browser.set_handle_equiv(True)
		browser.set_handle_redirect(True)
		browser.set_handle_referer(True)
		browser.set_handle_robots(False)
		browser.open(url)
		browser.select_form(name='loginform')
		browser['mli'] = user_id
		browser['password'] = password
		browser.submit()
		return browser

	#calculate yorku gpa
	def calc_gpa(self, browser):
		grade_dict = {'A+' : 9.0,
					  'A'  : 8.0,
					  'B+' : 7.0,
					  'B'  : 6.0,
					  'C+' : 5.0,
					  'C'  : 4.0,
					  'D+' : 3.0,
					  'D'  : 2.0,
					  'E'  : 1.0,
					  'F'  : 0.0
					 }
		grades_link = '/Apps/WebObjects/ydml.woa/wa/DirectAction/document?name=CourseListv1'
		browser.open(grades_link)
		soup = BeautifulSoup(browser.response().read())
		#print(soup) #for testing 
		table = soup.find("table", {"class":"bodytext"})
		counter = 0
		points = 0.0
		credits = 0.0
		for row in table.findAll('tr'):
			if counter > 0:
				course_weight = float(row.findAll('td')[1].text.split()[3])
				grade_str = row.findAll('td')[-1].text
				if "NCR" not in grade_str and "P" not in grade_str: #if no 'NCR'
					grade = grade_dict[grade_str.strip()]
					points += grade * course_weight
					credits += course_weight
			counter += 1
		return points / credits #GPA


	#get your credit status 
	def progress(self, browser):
		grades_link = '/Apps/WebObjects/ydml.woa/wa/DirectAction/document?name=CourseListv1'
		browser.open(grades_link)
		soup = BeautifulSoup(browser.response().read())
		#print(soup) #for testing 
		table = soup.find("table", {"class":"bodytext"})
		counter = 0
		for row in table.findAll('tr'):
			if counter > 0:
				return 0
