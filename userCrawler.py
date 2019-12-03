import os
from jikanpy import Jikan
jikan = Jikan()

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

def readfile(path):
	if(is_non_zero_file(path)):
		f=open(path)
		return [x.replace("\n","") for x in f.readlines()]
	else:
		return []

def writefile(path,data):
	f=open(path,"w+")
	for str_ in data:
		f.write(str_+"\n")
	
	f.close()	

class Crawler:
	
	def __init__(self,noncrawled,crawled):
		self.noncrawled=noncrawled
		self.crawled=crawled
	
	def crawl(self,limit):
		discovered=[]
		for user in self.noncrawled:
			if (self.count()+len(discovered)<limit):
				for friend in jikan.user(username=user, request='friends')['friends']:
					if(friend['username'] not in self.dump()):
						discovered.append(friend['username'])
				self.noncrawled.remove(user)
				self.crawled.append(user)
				print(self.count()+len([x for x in discovered if x not in self.dump()]))
			else:
				break
		self.noncrawled+=[x for x in discovered if (x not in self.dump())]
	
	def save(self,noncrawledPath="noncrawled",crawledPath="crawled"):
		for path,data in [[noncrawledPath,self.noncrawled],[crawledPath,self.crawled]]:
			writefile(path,data)
	
	def dump(self):
		return self.noncrawled+self.crawled
	
	def count(self):
		return len(self.dump())

if(__name__=="__main__"):
	
	#If there are no users to start crawling from, start from Xinil
	if(not is_non_zero_file("noncrawled")):
		writefile("noncrawled",["Xinil"])	
	
	crawler=Crawler(readfile("noncrawled"),readfile("crawled"))
	limit=1100

	while(crawler.count()<limit and crawler.noncrawled != []):
		print(crawler.count())
		crawler.crawl(limit=limit)

	print(crawler.count())
	crawler.save("noncrawled","crawled")

