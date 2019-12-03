import csv
import os
import aniffinity
import random
import pickle
from userCrawler import *
# Enter your username below
base_user="Xinil"
limit=1000

def readcsv(path):
	if(is_non_zero_file(path)):
		with open(path,"r") as f:
			csvreader=csv.reader(f)
			return [x for x in csvreader]
	else:
		return []

def writecsv(path,data):
	f=open(path,"w+")
	csvwriter=csv.writer(f)
	for x in data:
		csvwriter.writerow(x)
	f.close()

def updatefiles(scores):
	scores.sort(key= lambda x: x[1],reverse=True)
	writecsv("./scores",scores)

#Return affinity, shared, msg, where:
#	affinity: float		-> [-100,100] 	-> are user2 and base_user tastes similar - greater is better
#				      or -200 	-> error: too few common anime to say or invalid username, don't try to score this user again
#				      or -300	-> error: unrelated to the above, try to score this user again
#	shared: int		->        >=0	-> number of common anime
#				      or -200 	-> error: too few common anime to say or invalid username, don't try to score this user again
#				      or -300	-> error: unrelated to the above, try to score this user again
#	msg: string		->     	   ""	-> no error has occured
#				->    or else	-> name in string format of error that occured 
def score(user2,af,scores,refresh=False):
	scoredusers=[x[0] for x in scores]
	if(user2 in scoredusers and not refresh):
		i=scoredusers.index(user2)
		return scores[i][1],scores[i][2],""

	affinity, shared, msg = -200, -200, ""
	try:	
		affinity, shared = af.calculate_affinity(user2, service="MyAnimeList")
	except aniffinity.exceptions.RateLimitExceededError:
		return -300, -300, "RateLimitExceeded"
	except aniffinity.exceptions.InvalidUserError:
		affinity, shared, msg = -200, -200, "InvalidUserError"
	except aniffinity.exceptions.NoAffinityError:
		affinity, shared, msg = -200, -200, "NoAffinityError"
	except KeyboardInterrupt:
		return -300, -300, "KeyboardInterrupt"
	except:
		return -300, -300, "OtherError"
	scores.append([user2,affinity,shared])
	return affinity, shared, msg



if(__name__=="__main__"):
	
	#INPUT
	scores=[[x[0],float(x[1]),int(float(x[2]))] for x in readcsv("./scores")]

	users=Crawler(readfile("noncrawled"),readfile("crawled")).dump()
	
	scoredusers=[x[0] for x in scores]
	newusers=[x for x in users if (x not in scoredusers)]

	#Load cached Aniffinity object or create a new one
	if (is_non_zero_file("./af")):
		f=open("./af","rb")
		af=pickle.load(f)
		f.close()
	else:
		af = Aniffinity(base_user, base_service="MyAnimeList")
		f=open("./af","wb")
		pickle.dump(af,f)
		f.close()


	for i in range(limit):
		#Backup every ten ratings
		if(i%10 == 9):
				updatefiles(scores)
		if(len(newusers)==0):
				print("No users left to check")
				break
		user=random.choice(newusers)
		affinity,shared,msg=score(user,af,scores)
		#If -300 then let's try again to score this user in the future
		#if(affinity!=-300):
		#	newusers.remove(user)
		# The above is equivalent to:
		scoredusers=[x[0] for x in scores]
		newusers=[x for x in users if (x not in scoredusers)]
		if(msg!=""):
			#An error has occured
			print(str(i+1)+": "+user + "				"+msg)
			if(msg=="KeyboardInterrupt"):
				break
		else:
			#No error
			print(str(i+1)+": "+user + "				"+str(affinity)+", " +str(shared))

	updatefiles(scores)
	print(scores)
