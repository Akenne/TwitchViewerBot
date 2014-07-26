import requests
import subprocess
import json
import sys
import threading
import time
from queue import Queue 
 
numberOfViewers = 10
builderThreads = 25
startTime = time.time()
numberOfSockets = 0
concurrent = 25
urls = []
urlsUsed = []
 
def getURL(): # Get tokens
  output = subprocess.Popen(["livestreamer", "www.twitch.tv/espacefr", "-j"], stdout=subprocess.PIPE).communicate()[0]
  l = json.loads(output.decode()) # Parse json and return the URL parameter
  if 'streams' in l and 'worst' in l['streams'] and 'url' in l['streams']['worst']:
  	return l['streams']['worst']['url']
 
def build(): # Builds a set of tokens, aka viewers
	global numberOfSockets
	global numberOfViewers
	while True:
		if numberOfSockets < numberOfViewers:
			numberOfSockets += 1
			print ("Building viewers " + str(numberOfSockets) + "/" + str(numberOfViewers))
			urls.append(getURL())
 
def view(): # Opens connections to send views
	global numberOfSockets
	while True:
		url=q.get()
		requests.head(url)
		if (url in urlsUsed):
			urls.remove(url)
			urlsUsed.remove(url)
			numberOfSockets -= 1
		else:
			urlsUsed.append(url)
		q.task_done()
		print('beep')
 
if __name__ == '__main__':
	for i in range(0, builderThreads):
		threading.Thread(target = build).start()
	
	while True:
		while (numberOfViewers != numberOfSockets): # Wait until sockets are built
			time.sleep(1)
 
		q=Queue(concurrent*2)
		for i in range(concurrent):
			try:
				t=threading.Thread(target=view)
				t.daemon=True
				t.start()
			except:
				print ('thread error')
		try:
			for url in urls:
				q.put(url.strip())
				q.join()
		except KeyboardInterrupt:
			sys.exit(1)