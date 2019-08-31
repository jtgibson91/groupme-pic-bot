import requests
import time, datetime
from random import randrange
import logging

# Configure the logger
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
    		    level=logging.INFO,
    		    datefmt='%Y-%m-%d %H:%M:%S', 
		    filename='groupme_pic_bot.log')


# Fill these 3 items with your group id, groupme token id, and bot id
GROUP_ID = None
TOKEN_ID = None
BOT_ID = None

# If None, the bot will use the local system timezone
TIMEZONE = None



def message_is_from_day(date_to_examine, month_to_match=None, day_to_match=None):
	""" Returns True if date_to_examine has a month and day that matches month_to_match and day_to_match, and isn't
	    from the current year. If month_to_match and day_to_match are None, the current time is used. 

		:param date_to_examine: The unknown date to check the month and day for
		:type date_to_examine: datetime.datetime
		:param month_to_match: The month to check date_to_examine against. 1=January, 12=December
		:type month_to_match: Int
		:param day_to_match: The day to check date_to_examine against
		:type day_to_match: Int

	"""

	if not month_to_match and not day_to_match:
		current_time = datetime.datetime.now(tz=TIMEZONE)
		month_to_match = current_time.month
		day_to_match = current_time.day

	current_year = datetime.datetime.now(tz=TIMEZONE).year

	# Real version
	return date_to_examine.month == month_to_match and date_to_examine.day == day_to_match and not \
		   date_to_examine.year == current_year

	# Test version
	# return date_to_examine.month == month_to_match and date_to_examine.day == day_to_match


msgs = None
lowest_message_id_scanned = None
total_messages_in_group = None
# Array to hold matched images - each match is a dict with format:
# {'url': url, 'time': time_posted, 'posted_by': poster}
image_urls = []

while not msgs or msgs.status_code != 304:

	# This will start off the scanning (get first (most recent) group of messages)
	if not lowest_message_id_scanned:
		url = f'https://api.groupme.com/v3/groups/{GROUP_ID}/messages?token={TOKEN_ID}&limit=100'

	else:
		url = f'https://api.groupme.com/v3/groups/{GROUP_ID}/messages?token={TOKEN_ID}&limit=100&before_id={lowest_message_id_scanned}'

	msgs = requests.get(url)

	# If no messages are left, groupme returns 304
	if msgs.status_code == 304:
		break

	json = msgs.json()

	response = json['response']

	# All messages in a dict
	messages = response['messages']

	i = 1
	for msg in messages:

		if i == 1:
			total_messages_in_group = response['count']

		# Convert to human readable local time from seconds since epoch
		ctime_posted = time.ctime(msg['created_at'])

		time_posted = datetime.datetime.strptime(time.ctime(msg['created_at']), "%a %b %d %H:%M:%S %Y")

		if message_is_from_day(time_posted, month_to_match=None, day_to_match=None) and msg['attachments'] and \
			msg['sender_type'] != 'bot':

			for attachment in msg['attachments']:
				if attachment['type'] == 'image':
					image_urls.append({'url': attachment['url'], 'time': ctime_posted, 'posted_by': msg['name']})
		
		# If this is the last message in the 'page', record the message id 
		if i == len(messages):
			lowest_message_id_scanned = msg['id']

		i += 1

# Total # of messages in the groupchat
print(f'Scanned thru: {total_messages_in_group} messages')
logging.info(f'Scanned thru: {total_messages_in_group} messages')

# On this day in previous years of the chat, how many pictures were posted by non bots
print(f'Number of images posted on this day in past years: {len(image_urls)}')
logging.info(f'Number of images posted on this day in past years: {len(image_urls)}')

# Select a random image from the matches
if image_urls:
	chosen_image = image_urls[randrange(len(image_urls))]

	poster = chosen_image['posted_by']
	# Format the date to just MM/DD/YY
	date = datetime.datetime.strptime(chosen_image['time'], "%a %b %d %H:%M:%S %Y").strftime("%b %d %Y")
	url = chosen_image['url']

	headers = {
    'Content-Type': 'application/json',
	}

	data = f'{{"bot_id" : "{BOT_ID}", "text" : "Posted by {poster} on {date}", "attachments" : [ {{ "type"  : "image", "url"   : "{url}" }}]}}'

	# Post it to the group
	response = requests.post('https://api.groupme.com/v3/bots/post', headers=headers, data=data)

	if response.ok:
		print(f'Image posted to group: {chosen_image}')
		logging.info(f'Image posted to group: {chosen_image}')

else:
	logging.info('No matched images')
	print('No matched images')
