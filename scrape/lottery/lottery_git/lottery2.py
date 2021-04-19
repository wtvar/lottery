#! /usr/bin/python3

import requests
import bs4
import re
import urllib
#import time
import datetime
#import pandas as pd
#from tabulate import tabulate
import csv
import logging
from settings import my_telegram_id, TELEGRAM_TOKEN


#TODO: tidy the imports and see if all needed

# C:\Users\user\Desktop\python\scrape\lottery\lottery.py file location
"""sites used: 
https://www.codementor.io/gergelykovcs/scrape-the-web-with-python-and-get-updates-on-telegram-rv83fbgie
https://github.com/eternnoir/pyTelegramBotAPI#writing-your-first-bot
"""

index_url = "https://www.national-lottery.co.uk/games/euromillions?icid=-:mm:-:mdg:em:dbg:pl:co"
lotto_url = "https://www.national-lottery.co.uk/games/lotto?icid=-:mm:-:mdg:lo:dbg:pl:co"

#set threshold below to be notified when the jackpot exceeds this amount
threshold = 99
lotto_threshold = 20
#also need to add telegram details to settings.py in order for the telegram part to work


""" logging details"""
# set up logging to file
#windows filename: 'C:\\Users\\user\\Desktop\\python\\scrape\\lottery\\lottery.log'
#pi filename: '/home/pi/python/lottery.py'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/home/pi/python/lottery/lottery.log',
                    filemode='a')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...
logging.info('Start of logging.')

logger1 = logging.getLogger('my euormillions logger')
logger2 = logging.getLogger('my telegram logger')
logger3 = logging.getLogger('my lotto  logger')

def write_results_to_csv(text_to_add,csv_name):
	"""writes text given to a csv fike
	inputs:
	text_to_add as a string
	csv.name 
	"""
	#open csv
	#make a list of things to add to csv
	#write to csv
	#close csv
	
	#csv format:
	# date,jackpot
	open_csv = open(csv_name, 'a', newline='')# opens csv with "a" which means append not "w" for (over)write
	
	with open_csv:
		writer = csv.writer(open_csv)
		writer.writerow(text_to_add)
		logger1.info('data written to csv')
		
def telegram_send(message):
	""" sends a telegram message 
	
	inputs needed to be defined previously
	
	-TELEGRAM_TOKEN
	-my_telegram_id
	
	-message: str to send
	
	"""
	requests.get("https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage?chat_id=" + my_telegram_id + "&text={}".format(message))


def check_jackpot():
	"""Find the current Euromillions jackpot and send telegram message
	"""
	
	response = requests.get(index_url)
	soup = bs4.BeautifulSoup(response.text, 'lxml')
	localtime_exact = datetime.datetime.today()
	localtime_date = datetime.date.today()
	#list_of_date_amounts = []
	raffle_text = "" #initialise empty so if the first part fails the message still works
	
	try:
		p=soup.find('p',{'class':'raffle'}).get_text()
		#this looks for the "raffle" which should have the number of millionaire raffles. to be seen once this week passed
		raffle_text = p.strip() # strip to remove all extra spaces&tabs
		
	except:
		#if it fails we just want it to continue
		logger1.info('Raffle wasnt found.')
		pass
	
	try:
		t=soup.find('span',{'class':'amount amount_large'}).get_text()
		#the try checks if scraping works. if it does continue
	except:
		#print("error scraping in 1st block")
		logger1.info('error scraping in 1st block')
		
	try:
		t=soup.find('span',{'class':'amount'}).get_text()
	except:
		#print("error scraping in 2nd block")
		logger1.info('error scraping in 2nd block')
		
		telegram_send("Error occured in 2nd part")
		
		#print("Error occured logging in to telegram at " + str(localtime_exact))
		#error handling here
	else:
		list_of_numbers = re.findall('\d+', t)
		jackpot_number_as_int = int(list_of_numbers[0])

		#print("The Jackpot on " + str(localtime_date) + " is GBP " + str(jackpot_number_as_int) + " Million\n")
		#print for logging by csv
		#print(str(localtime_date) + "," + str(jackpot_number_as_int))
		logger1.info("data for csv: " + str(localtime_date) + "," + str(jackpot_number_as_int))
	
		"""
		#the next part was for making pretty table to print but doesnt work
		list_of_date_amounts.append([localtime_date, jackpot_number_as_int]) #add date and result to list
		df = pd.DataFrame(list_of_date_amounts, columns=["Date","Jackpot"]) #make data frame of the lists
		
		latest_jps = df.iloc[::-1].head() #last 5 lines from dataframe of dates and amounts
		#print(latest_jps)
		tab_of_df = tabulate(latest_jps,headers=["Date","Jackpot"],tablefmt="grid")
		"""
		
		#is there a draw tonight?
		day_of_week = datetime.datetime.today().weekday()
		draw_tonight = False
		if day_of_week == 1 or day_of_week == 4:
			draw_tonight = True
			
		#text changes depending on draw_tonight
		if draw_tonight == True:
			ResultText = "The Jackpot today is GBP " + str(jackpot_number_as_int) + " Million and there is a draw tonight !!" + "\n" + "\n" + index_url + "\n" + raffle_text
		else:
			ResultText = "The Jackpot today is GBP " + str(jackpot_number_as_int) + " Million" + "\n" + "\n" + index_url
			
		ParsedResultText = urllib.parse.quote_plus(ResultText)
		
		#write results to csv
		#TODO: check/correct this as its not writing to file in my pi
		try:
			csv_date = datetime.date.today()
			text_for_csv = [csv_date, str(jackpot_number_as_int)]
			write_results_to_csv(text_for_csv,"/home/pi/python/lottery/lottery_results.csv")
			
		except:
			logger1.info("Error writing data to csv")
			pass
			
		
		"""
		#next part is to check if Jackpot was won
		#this isnt being used for now
		yesterday_jp = list_of_date_amounts[-1][-1] #yesterdays jackpot as int
		jp_won = jackpot_number_as_int < yesterday_jp #this means jackpot was won
		"""
		#if jackpot is over threshold then send a message with link to buy ticket
		#else send message with jackpot but no link
		
		if jackpot_number_as_int >= threshold:
			try:
				telegram_send(ParsedResultText)
				logger2.info("Telegram message sent at " + str(localtime_exact))
			except:
				logger2.info("Telegram message unable to be sent at " + str(localtime_exact))
				pass
			#print("Telegram message sent at " + str(localtime_exact))
			
	
		else:	
			try:
				telegram_send("jackpot is only " + str(jackpot_number_as_int) + " today! :( " + "\n" + raffle_text)
				logger2.info("Telegram message sent at " + str(localtime_exact))
			except:
				logger2.info("Telegram message unable to be sent at " + str(localtime_exact))
				pass

def check_lotto_jackpot():
	"""Find the current UK Lotto jackpot and send telegram message
	"""
	response = requests.get(lotto_url)
	soup = bs4.BeautifulSoup(response.text, 'lxml')
	localtime_exact = datetime.datetime.today()
	localtime_date = datetime.date.today()
	
	try:
		t=soup.find('span',{'class':'amount amount_large'}).get_text()
	except:
		logger3.info('error scraping in 1st block')
		
	try:
		t=soup.find('span',{'class':'amount'}).get_text()
	except:
		#print("error scraping in 2nd block")
		logger3.info('error scraping in 2nd block')
		
		telegram_send("Error occured in 2nd part")
		
	else:
		list_of_numbers = re.findall('\d+', t)
		jackpot_number_as_int = int(list_of_numbers[0])

		#print("The Jackpot on " + str(localtime_date) + " is GBP " + str(jackpot_number_as_int) + " Million\n")
		#print for logging by csv
		#print(str(localtime_date) + "," + str(jackpot_number_as_int))
		logger3.info("data for csv: " + str(localtime_date) + "," + str(jackpot_number_as_int))
	
		#is there a draw tonight?
		day_of_week = datetime.datetime.today().weekday()
		draw_tonight = False
		if day_of_week == 2 or day_of_week == 5:
			draw_tonight = True
			
		#text changes depending on draw_tonight
		if draw_tonight == True:
			ResultText = "The Lotto Jackpot today is GBP " + str(jackpot_number_as_int) + " Million and there is a draw tonight !!" + "\n" + "\n" + index_url + "\n" + raffle_text
		else:
			ResultText = "The Lotto Jackpot today is GBP " + str(jackpot_number_as_int) + " Million" + "\n" + "\n" + index_url
			
		ParsedResultText = urllib.parse.quote_plus(ResultText)
		
		#write results to csv
		#TODO: check/correct this as its not writing to file in my pi
		try:
			csv_date = datetime.date.today()
			text_for_csv = [csv_date, str(jackpot_number_as_int)]
			write_results_to_csv(text_for_csv,"/home/pi/python/lottery/lotto_results.csv")
			
		except:
			logger3.info("Error writing data to csv")
			pass
			
		#if jackpot is over threshold then send a message with link to buy ticket
		#else send message with jackpot but no link
		
		if jackpot_number_as_int >= lotto_threshold:
			try:
				telegram_send(ParsedResultText)
				logger2.info("Telegram message sent for Lotto at " + str(localtime_exact))
			except:
				logger2.info("Telegram message for Lotto unable to be sent at " + str(localtime_exact))
				pass
			#print("Telegram message sent at " + str(localtime_exact))
			
	
		else:	
			try:
				telegram_send("Lotto jackpot is only " + str(jackpot_number_as_int) + " today! :( ")
				logger2.info("Telegram message for Lotto sent at " + str(localtime_exact))
			except:
				logger2.info("Telegram message for Lotto unable to be sent at " + str(localtime_exact))
				pass			
		
		#TODO:
		#can then do some playing/analysis after
		#ideas:
		#days since last win
		#jp has been over 99 for x days or x draws
		#average time it takes to go from being won to over 99 again
		

check_jackpot()	
check_lotto_jackpot()
