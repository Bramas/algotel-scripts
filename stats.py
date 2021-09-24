# Statistiques pour algotel'16.
# Modifié pour algotel 2021 (Quentin Bramas <bramas@unistra.fr>)
# 
# Ce script fonctionne sur les 3 fichiers suivants:
authors_file="authors_withcity.csv"
articles_file="papiers.csv"
logs_file="logs.csv"
# pour utiliser les fichiers exemples:
#authors_file="exemple_authors_withcity.csv"
#articles_file="exemple_papiers.csv"
#logs_file="exemple_logs.csv"

## Fichier Auteurs ##
# Le fichier des auteurs s'obtient en exportant les auteurs depuis easychair, dans un fichier "authors.csv", puis en exécutant le script "affiliation_to_city.py" qui va créer le fichier "authors_withcity.csv" (voir dans le script car il y aura probablement besoin de le modifier pour qu'il détecte les villes/labo à partir de l'affiliation).

## Fichier Papiers ##
# le fichier "papiers.csv" s'obtient en sélectionnant la liste des papiers dans 
# easychair (après avoir coché l'ajout des champs supplémentaires), 
# puis copier/coller cette liste dans un fichier papiers.csv
# le format doit être (les espaces entre les champs sont des tabulations):
# 	id	authors	title	_	_	_	_	date_time	<Accept/Reject/Brief>
# où les "_" représentent des valeurs quelconques.
# S'il y a des champs en plus ou en moins, vous pouvez modifier cette fonction
# avec plus ou moins de "_"
def filterArticleFields(line):
	# enlevez ou réordonnez les champs comme vous le souhaitez dans la ligne suivante
	id, a_list, title, _, _, _, _, date_time, accepted = line 
	return (id, a_list, title, date_time, accepted)

## Fichier Logs ##
# De même le fichier logs.csv se construit en sélectionnant la liste des événements
# sur easychair (menu "events"), puis en copiant/collant dans logs.csv

# Vous pouvez ensuite exécuter le script pour avoir toutes les stats, et une carte avec
# la provenance des auteurs qui ont soumis.
# la génération des pdf contient probablement des erreurs, donc à tester/corriger
# si besoin. Vous pouvez commenter des fonctions en fin de fichier si vous ne 
# souhaitez pas tout exécuter

# La position des villes sur la carte est obtenue grâce à ce tableau
# à compléter en fonction des auteurs qui soumettent.

cityCoordinates = {
	'Nice': (1074,975),
	'Paris': (619,335),
	'Sophia-Antipolis': (1015,1026),
	'Toulouse': (538,1001),
	'Bordeaux': (362,840),
	'Strasbourg': (1075,353),
	'Nantes': (286,538),
	'Lyon': (842,728),
	'Grenoble': (926,796),
	'Clermont-Ferrand': (689,727),
	'Amiens': (618,207),
	'Valenciennes': (715,146),
	'Saarbrücken': (1052,260),
	'Eindhoven': (882,19),
	'Roma, Italy': (1110,1062),
	'Compiègne': (673,273),
	'New Delhi': (200,700),
	'Wrocław': (200,740),
	'Bucharest': (200,780)
}

# Voici quelques détails supplémentaires sur les formats de chaque fichier.
# Vous pouvez changer le délimiteur csv si besoin.
#
# Formats: 
#	- authors
#		ID ; <Coresponding author> ; <email> ; <country> ; <affiliation> ; <lab + city>
authorsDelimiter=';'
#	- articles
#		id	authors	title	_	_	_	_	date_time	<Accept/Reject/Brief>	
articlesDelimiter='\t'	
# 	- Logs
#		Jan 29	17:28	file upload for submission 6 (paper)	Christian Glacet
#		Jan 27	13:46	submission 42 withdrawn	
#		Jan 23	11:00	submission page is open only for updates of previously submitted papers	
#		Jan 15	19:49	file deleted for submission 46 (paper)	Jean Valjean
#		Jan 13	21:03	submission of paper 6	Christian Glacet
logsDelimiter='\t'	
# Plus d'informations sur les regex python: https://docs.python.org/2/library/re.html
#
# 
#
################################## READING ##################################
# normalement il n'y a rien à modifier dans cette partie (il y a quand même 
# quelques variables/fonctions qui peuvent être intéressantes en fonction des besoins).

import csv
import re
import sys
from datetime import datetime, timedelta
from collections import defaultdict

# Plot
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab
import matplotlib.dates as md
from matplotlib.backends.backend_pdf import PdfPages

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# Exit au premier warning ?
WError = True

# s'il n'y a pas l'année dans les logs?
year="2021"


# Articles publiés ? : 
if len(sys.argv) > 1 and sys.argv[1] == "accepted":
	def ispublished(article):
		return (article["accept"])
else:
	def ispublished(article):
		return (article["accept"] or article["brief"])
# Comme certains champs sont manquants (exemple un étranger n'a pas de labo de rattachement), on utilise nc dans ce cas :
nc = "nc."





# Respectivement indexés par 'prénom nom' ; 'id article' ; 'id article'  (on pourrait fusioner les deux derniers, mais ça ne change pas grand chose à vrai dire)
authors = {} ; articles = {} ; logs = {}


with open(authors_file) as f: 
	r = csv.reader(f, delimiter=authorsDelimiter, quotechar='"')
	nb_authors = 0
	for author in r:
		id, name, mail, country, affiliation, city_lab = author  

		name = name.lower()
		if name not in authors: # Certains authors sont présent plusieurs fois dans le fichier d'entrée (1 fois par article soumis?)
			authors[name] = {}
			authors[name]["id"] 	= id
			authors[name]["name"] 	= name
			authors[name]["mail"] 	= mail
			authors[name]["country"] 	= country
			authors[name]["affiliation"] 	= affiliation
			authors[name]["city"] 	= city_lab
			# Deux types d'affiliations : 
			if (re.match(r'^Étranger',city_lab) != None): # à l'étranger "Étranger - pays"
				authors[name]["country"] = re.sub(r'Étranger - (.*)', r'\1', city_lab)
				authors[name]["city"] =  "Étranger" # nc 
				authors[name]["lab"] =  country # nc
			else: # en france "ville (labo)"
				reg = r'(.*) \((.*)\)'
				authors[name]["city"] = re.sub(reg,r'\1', city_lab)
				authors[name]["lab"] = re.sub(reg,r'\2', city_lab)
			nb_authors += 1

with open(articles_file) as f: 
	r = csv.reader(f, delimiter=articlesDelimiter, quotechar='"')
	nb_articles = 0 
	for article in r:
		id, a_list, title, date_time, accepted = filterArticleFields(article)
		articles[id] = {}
		articles[id]["authors"] 		= list(map(lambda x: x.lower().strip(), re.split(", | and ",a_list)))
		articles[id]["title"] 		= title
		articles[id]["date_time"]	= date_time
		articles[id]["brief"] = (accepted.lower() == "brief")
		articles[id]["reject"] = (accepted.lower() == "reject")
		articles[id]["accept"] = (accepted.lower() == "accept")
		nb_articles += 1

with open(logs_file) as f: 
	r = csv.reader(f, delimiter=logsDelimiter, quotechar='"')
	for log in r:
		day, hour, txt, author = log
		# On change le format de la date dans le but de 
		# trier les évènements par date (probablement déjà triés ?). 
		# Doc: https://docs.python.org/2/library/datetime.html
		# 	-	%b	Month as locale’s abbreviated name:	Jan, Feb,
		#	-	%d	Day of the month as a zero-padded decimal number:	01, 02,
		#	-	%H	Hour (24-hour clock) as a zero-padded decimal number:	00, 01,
		#	-	%M	Minute as a zero-padded decimal number:	00, 01
		gmt_delta = timedelta(hours=1)
		if '2020' not in day: 
			timestamp=datetime.strptime(year+" "+day+" "+hour,"%Y %b %d %H:%M")+gmt_delta
		else:
			timestamp=datetime.strptime(day+" "+hour,"%b %d, %Y %H:%M")+gmt_delta

		# Est-ce une soumission ?
		submission=(re.match(r'^submission of',txt) != None) 
		# Ou un téléversement de fichier ? 
		file_upload=(re.match(r'^file upload',txt) != None) 
		# Ou encore une suppression de fichier ? 
		file_deleted=(re.match(r'^file deleted',txt) != None) 
		# Ou alors un retrait de fichier ? 
		withdrawn=(re.match(r'submission [0-9]* withdrawn',txt) != None) 

		# Récupérer l'id du article (2 formats) :
		#	-	"submission x"
		#	-	"submission of paper x"
		id, found = re.subn(r'.*submission (of paper ){0,1}([0-9]+).*', r'\2', txt)


		# Certaines lignes ne concernent pas des articles, mais sont des choses génériques, on les ignore
		if (found > 0):
			# Est-ce la première fois qu'on a des info sur cet article? 
			if id not in logs:
				logs[id] = {}
				logs[id]["author"] 	= author
				logs[id]["uploads"] = []
				logs[id]["deletions"] = []
				logs[id]["withdrawns"] = []
			if submission:
				logs[id]["submission"] = timestamp
			elif file_upload:
				logs[id]["uploads"].append(timestamp)
			elif file_deleted:
				logs[id]["deletions"].append(timestamp)
			elif withdrawn:
				logs[id]["withdrawns"].append(timestamp)
			else:
				print("Notice: entrée de log ingorée: ", log)

# Trier les logs par date
for id, log in logs.items():
	log["uploads"].sort()
	log["deletions"].sort()
	log["withdrawns"].sort()


# Au cas où ...
for id, p in articles.items():
	for name in p["authors"]:
		# ... ça ne devrait pas arriver, mais on ne sait jamais
		if name not in authors:
			authors[name] = {}
			aut = authors[name]
			aut["id"] 	= -1
			aut["name"] 	= nc
			aut["mail"] 	= nc
			aut["country"] 	= nc
			aut["lab"] 	= nc
			aut["city"] 	= nc
			if WError:
				print(name+" n'est pas dans la liste des auteurs!!")
				exit(1)	

################################## STATS ##################################

# Longueur du titre selon acceptés ou non: 
brief_title_len = []
rejected_title_len = []
accepted_title_len = []


print("\n ############## Date et heures de soumssion/upload ############## \n")

# Pour chaque auteur on aura des métriques soit pondérées par son implication (eg : 1/x si il y a x auteurs)
# ou non pondérées (1 par article)
for name, aut in authors.items():
	aut["accept"] = 0
	aut["publish"] = 0
	aut["reject"] = 0
	aut["brief"]  = 0
	aut["articles"] = 0
	# versions non pondérés
	aut["nb_articles"] = 0
	aut["nb_accepts"] = 0
	aut["nb_briefs"] = 0
	aut["nb_published"] = 0

# Accepts/Brief/Reject par auteur 
for id, p in articles.items():
	b=0; a=0; r=0;
	if (p["brief"]):
		b = 1
		brief_title_len.append(len(p["title"]))
	elif (p["reject"]):
		r = 1
		rejected_title_len.append(len(p["title"]))
	elif (p["accept"]):
		a = 1
		accepted_title_len.append(len(p["title"]))
	if (a + b + r != 1):
		print("Erreur, l'article "+p["title"]+" n'est pas accept/brief/reject !")
		exit(1)

	for name in p["authors"]:
		aut = authors[name]
		aut["accept"] += float(a)/len(p["authors"])
		aut["publish"] += float(a+b)/len(p["authors"])
		aut["reject"] += float(r)/len(p["authors"])
		aut["brief"]  += float(b)/len(p["authors"])
		aut["articles"] += 1./len(p["authors"])
		# version non pondérée: 
		aut["nb_articles"] += 1
		aut["nb_accepts"] += a
		aut["nb_briefs"] += b
		aut["nb_published"] += a+b


print("Longueur moyenne du titre des articles: ")
print("== Acceptés ==")
print('\t - mean =', np.mean(accepted_title_len))
print('\t - std = ', np.std(accepted_title_len))
if len(brief_title_len) != 0:
	print("== Brief ==")
	print('\t - mean =', np.mean(brief_title_len))
	print('\t - std = ', np.std(brief_title_len))

print("== Refusés ==")
print('\t - mean =', np.mean(rejected_title_len))
print('\t - std = ', np.std(rejected_title_len))


def statByDate():
	# Acceptation en fonction de l'heure: 
				#    times = pd.date_range("1/1/2000 00:00", "2/1/2000 00:00", freq="1h30min").time
	# On fait des groupes par crénaux horaires de durée 'H:M':
	H = 3
	M = 0
	S = 0
	# Les groupes sont à partir de minuit
	hh = 00
	mm = 00
	ss = 00

	day="01"
	grps = []
	while True :
		time=datetime.strptime("1970 Jan "+day+" 00:00","%Y %b %d %H:%M")+timedelta(hours=hh,minutes=mm,seconds=ss)
		day=datetime.strftime(time, "%d")
		if day != "01":
			break
		grps.append(datetime.strftime(time, "%H:%M"))
		hh += H
		mm += M
		ss += S

	grps.append("23:59")
	# Pour chaque article, on le classe dans un des groupe horaire
	# Pour cela, on crée un dictionaire ayant pour clefs <day dans {1,..,365}> x <créneaux> (dict de dict)
	# Pour une clef donnée la valeur associée est simplement la liste des ID des articles soumis/uploadés sur ce créneaux 
	submissions = defaultdict(lambda: defaultdict(list))
	uploads = defaultdict(lambda: defaultdict(list))
	# Pour le graphique temps: soumission vs. upload 
	x = list()
	y = list()
	colors = list()
	c1 = "#0034EE"
	c2 = "#FF2222"
	size = list()
	for id, p in articles.items():
		if id in logs:
			# Logs correspondants
			log=logs[id]
			# Si les données qu'on cherche sont bien présente pour cet article:
			if "submission" in log and len(log["uploads"]) > 0:
				# remarque: %j	Day of the year as a zero-padded decimal number.
				submission_t, submission_d = datetime.strftime(log["submission"], "%H:%M"), datetime.strftime(log["submission"], "%j") 
				last_upload_t, last_upload_d = datetime.strftime(log["uploads"][-1], "%H:%M"), datetime.strftime(log["uploads"][-1], "%j")  

				x.append(log["submission"])
				y.append(log["uploads"][-1])
				colors.append(c1 if ispublished(p) else c2)
				size.append(len(log["uploads"])**2*10)

				# On parcourt tous les créneaux à chaque fois 
				for i in range(len(grps)-1):
					if (grps[i] < submission_t and submission_t < grps[i+1]):
						submissions[int(str(submission_d))][str(grps[i])].append(id)
					if (grps[i] < last_upload_t and last_upload_t < grps[i+1]):
						uploads[int(str(last_upload_d))][str(grps[i])].append(id)
		
	fig = plt.figure()

	plt.ylabel('Dernier upload')
	plt.xlabel('Soumission')
	plt.xticks( rotation= 60 )
	plt.scatter(x,y,c=colors,alpha=.5, s=size)

	xaxis = plt.gca().get_xaxis()
	yaxis = plt.gca().get_yaxis()
	xaxis.set_major_formatter(md.DateFormatter('%b %d'))
	yaxis.set_major_formatter(md.DateFormatter('%b %d'))
	pad = timedelta(hours=12)
	plt.xlim(min(x)-pad, max(x)+pad) 
	plt.ylim(min(y)-pad, max(y)+pad) 
	##ax.xaxis.set_major_locator(md.DayLocator(bymonthday=range(1,32),interval=1)) # Xlim à régler !
	#ax.xlim. ... 

	pp = PdfPages("soumission_upload.pdf")
	pp.savefig(fig, bbox_inches='tight')
	pp.close()

	pp = PdfPages("soumission_upload_zoom.pdf")
	f = datetime.strptime
	##xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
	##yaxis.set_major_formatter(md.DateFormatter('%H:%M'))
	##plt.xlim(f("Feb 10 08:45 "+str(year), "%b %d %H:%M %Y"), f("Feb 17 00:15 "+str(year), "%b %d %H:%M %Y")) 
	##plt.ylim(f("Feb 17 13:01 "+str(year), "%b %d %H:%M %Y"), f("Feb 28 01:01 "+str(year), "%b %d %H:%M %Y"))

	##plt.xlim(f("Feb 17 08:45 "+str(year), "%b %d %H:%M %Y"), f("Feb 18 02:15 "+str(year), "%b %d %H:%M %Y")) 
	## plt.ylim(f("Feb 26 13:01 "+str(year), "%b %d %H:%M %Y"), f("Feb 27 02:01 "+str(year), "%b %d %H:%M %Y"))

	xaxis.set_major_formatter(md.DateFormatter('%d, %H:%M'))
	yaxis.set_major_formatter(md.DateFormatter('%d, %H:%M'))
	plt.xlim(f("Feb 14 08:01 "+str(year), "%b %d %H:%M %Y"), f("Feb 18 02:01 "+str(year), "%b %d %H:%M %Y")) 
	plt.ylim(f("Feb 24 08:01 "+str(year), "%b %d %H:%M %Y"), f("Feb 27 02:01 "+str(year), "%b %d %H:%M %Y"))

	pp.savefig(fig, bbox_inches='tight')
	pp.close()


	print("Dates et heures de soumission: ")
	time_vs_accpept(grps, submissions, "submissions.pdf")
	print("Dates et heures de dernier upload: ")
	time_vs_accpept(grps, uploads, "uploads.pdf")

# plt.show()

def plot_accepts(grps, timestamps,nb_papers,acceptance,outfile):
	times=[datetime.strptime(t,"%H:%M")for t in timestamps]
	fig = plt.figure()
	plt.bar(times,nb_papers,width=1./len(grps),color='#81B3D3')
	plt.bar(times,acceptance,width=1./len(grps),color='#2075C8')
	plt.xticks( rotation= 60 )

	ax = plt.gca()
	ax.xaxis.set_major_formatter(md.DateFormatter('%Hh'))
	ax.xaxis.set_major_locator(md.HourLocator(byhour=range(24), interval=1))

	pp = PdfPages(outfile)
	pp.savefig(fig)
	pp.close()

def time_vs_accpept(grps, data,outfile):
	nb = 0	
	total_a_before_deadline = 0
	total_p_before_deadline = 0
	for d in sorted(data.keys()):
		print("\tJour",d)
		total_d_accepts = 0
		total_d_articles = 0
		timestamps = list()
		acceptance = list()
		nb_papers = list()
		for h in sorted(data[d].keys()):
			ids = sorted(data[d][h])
			nb_accept = sum(map(lambda x: 1 if ispublished(articles[x]) else 0, ids))
			nb_articles = len(ids)
			pc_accept = float(nb_accept)/nb_articles*100
			total_d_accepts += nb_accept
			total_d_articles += nb_articles
			print("\t\t",h, nb_articles, "articles, ", str(pc_accept)+"% d'acceptation") #, ids)
			nb += len(data[d][h])
			timestamps.append(h)
			acceptance.append(nb_accept)
			nb_papers.append(nb_articles)

			# Total acceptation avant le jour de la deadline:
			if int(d) < 57:
				total_p_before_deadline += nb_articles
				total_a_before_deadline += nb_accept
		# Plot: 
		if outfile=="uploads.pdf": # jour de la deadline pour l'upload
			plot_accepts(grps, timestamps,nb_papers,acceptance,outfile)
		if outfile=="submissions.pdf": # jour de la deadline pour les soumissions
			plot_accepts(grps, timestamps,nb_papers,acceptance,outfile)

		pc_accept = float(total_d_accepts)/total_d_articles*100
		print("\t\t--------------------")
		print("\t\tTotal", total_d_articles, "articles, ", str(float(total_d_accepts)/total_d_articles*100)+"% d'acceptation" )

	if outfile=="uploads.pdf":
		print("Accept : ", total_a_before_deadline, "/", total_p_before_deadline)
		print("Articles publiés au moins 24h avant la deadline :", total_p_before_deadline, "articles", str(float(total_a_before_deadline)/total_p_before_deadline*100)+"% acceptés.")

	print(nb)


# nombre d'uploads vs acceptation
def upload_and_acceptation():
	print("\n ############## Nombre de versions ############## \n")

	nb_papers = defaultdict(int)
	nb_accepts = defaultdict(int)
	for id, log in logs.items(): 
		if (id in articles):
			nb_upload = len(logs[id]["uploads"])
			nb_papers[nb_upload] += 1
			if ispublished(articles[id]):
				nb_accepts[nb_upload] += 1
	for nb_upload, nb_paper in nb_papers.items():
		print("Les articles ("+str(nb_paper)+") ayant", nb_upload, "version(s) ont un taux d'acceptation moyen de", float(nb_accepts[nb_upload])/nb_paper*100, "%")

	# Taux acceptation en fonction de l'affiliation:
	print("\n ############## Affiliation ############## \n")

	lab_a = defaultdict(float) ; lab_p = defaultdict(float)
	city_a = defaultdict(float) ; city_p = defaultdict(float)
	country_a = defaultdict(float) ; country_p = defaultdict(float)
	for name, aut in authors.items():
		lab_a[aut["lab"]] += aut["publish"]
		lab_p[aut["lab"]] += aut["articles"]
		city_a[aut["city"]] += aut["publish"]
		city_p[aut["city"]] += aut["articles"]
		country_a[aut["country"]] += aut["publish"]
		country_p[aut["country"]] += aut["articles"]

	print("Taux d'acceptation par laboratoire: ")
	for id in sorted(lab_a.keys(), key=lambda x: float(lab_p[x]), reverse=True):
		if (lab_p[id] > 0):
			print("\t - ", id, ":", float(lab_a[id])/lab_p[id]*100, "(", lab_a[id], "/", lab_p[id], ")")
	print("Taux d'acceptation par ville: ")
	for id in sorted(city_a.keys(), key=lambda x: float(city_p[x]), reverse=True):
		if (city_p[id] > 0):
			print("\t - ", id, ":", float(city_a[id])/city_p[id]*100, "(", city_a[id], "/", city_p[id], ")")
	print("Taux d'acceptation par pays: ")
	for id in sorted(country_a.keys(), key=lambda x: float(country_p[x]), reverse=True):
		if (country_p[id] > 0):
			print("\t - ", id, ":", float(country_a[id])/country_p[id]*100, "(", country_a[id], "/", country_p[id], ")" )

	print("En Valeurs Absolues?")
	lab_a = defaultdict(float) ; lab_p = defaultdict(float)
	city_a = defaultdict(float) ; city_p = defaultdict(float)
	country_a = defaultdict(float) ; country_p = defaultdict(float)
	for name, aut in authors.items():
		lab_a[aut["lab"]] += (1 if aut["nb_published"] >= 1 else 0)
		lab_p[aut["lab"]] += (1 if aut["nb_articles"] >= 1 else 0)
		city_a[aut["city"]] += (1 if aut["nb_published"] >= 1 else 0)
		city_p[aut["city"]] += (1 if aut["nb_articles"] >= 1 else 0)
		country_a[aut["country"]] += (1 if aut["nb_published"] >= 1 else 0)
		country_p[aut["country"]] += (1 if aut["nb_articles"] >= 1 else 0)

	print("Taux d'acceptation par laboratoire: ")
	for id in sorted(lab_a.keys(), key=lambda x: float(lab_p[x]), reverse=True):
		if (lab_p[id] > 0):
			print("\t - ", id, ":", float(lab_a[id])/lab_p[id]*100, "(", lab_p[id], ")")
	print("Taux d'acceptation par ville: ")
	for id in sorted(city_a.keys(), key=lambda x: float(city_p[x]), reverse=True):
		if (city_p[id] > 0):
			print("\t - ", id, ":", float(city_a[id])/city_p[id]*100, "(", city_p[id], ")")
	print("Taux d'acceptation par pays: ")
	for id in sorted(country_a.keys(), key=lambda x: float(country_p[x]), reverse=True):
		if (country_p[id] > 0):
			print("\t - ", id, ":", float(country_a[id])/country_p[id]*100, "(", country_p[id], ")" )



	# Taux acceptation en fonction du nombre d'auteurs 
	accept_vs_nb_authors = defaultdict(int)
	nb_articles_vs_nb_authors = defaultdict(int)
	for id, p in articles.items():
		nb = len(list(p["authors"]))
		if ispublished(p):
			accept_vs_nb_authors[nb] += 1
		nb_articles_vs_nb_authors[nb] += 1
	print("Taux d'acceptation en fonction du nombre d'auteurs : ")
	for nb in sorted(accept_vs_nb_authors.keys()):
		nb_a = accept_vs_nb_authors[nb]
		nb_p = nb_articles_vs_nb_authors[nb]
		print("\t -", nb, "auteurs :", float(nb_a)/nb_p*100,"% ("+ str(nb_p)+" articles)")

	# Acceptation pour affiliation mixtes vs. tous dans le même labo
	mixtes_a = 0
	mono_a = 0
	mixtes_p = 0
	nb_articles = 0
	for id, p in articles.items():
		same_lab = True 
		i = 0
		while same_lab and (i+1 < len(list(p["authors"]))):
			same_lab = (authors[p["authors"][i]]["lab"]==authors[p["authors"][i+1]]["lab"] and authors[p["authors"][i]]["lab"]!=nc)
			i += 1
		nb_articles += 1
		if same_lab:
			mixtes_p += 1
			if ispublished(p):
				mixtes_a += 1
		elif ispublished(p):
			mono_a += 1
	print("Taux acceptation des articles ("+ str(mixtes_p) +") labo-mixtes : ", float(mixtes_a)/mixtes_p*100, "%")
	if nb_articles-mixtes_p == 0:
		print("Pas de papier avec une seul affiliation")
	else:
		print("Taux acceptation des articles ("+ str(nb_articles-mixtes_p) +") avec une seule affiliation : ", float(mono_a)/(nb_articles-mixtes_p)*100, "%")

	# Acceptation pour affiliation mixtes vs. tous dans la même ville
	mixtes_a = 0
	mono_a = 0
	mixtes_p = 0
	nb_articles = 0
	for id, p in articles.items():
		same_city = True 
		i = 0
		while same_city and (i+1 < len(list(p["authors"]))):
			same_city = (authors[p["authors"][i]]["city"]==authors[p["authors"][i+1]]["city"] and authors[p["authors"][i]]["city"]!=nc)
			i += 1
		nb_articles += 1
		if same_city:
			mixtes_p += 1
			if ispublished(p):
				mixtes_a += 1
		elif ispublished(p):
			mono_a += 1
	print("Taux acceptation des articles ("+ str(mixtes_p) +") ville-mixtes : ", float(mixtes_a)/mixtes_p*100, "%")

	if nb_articles-mixtes_p == 0:
		print("Pas d'articles avec une seule ville")
	else:
		print("Taux acceptation des articles ("+ str(nb_articles-mixtes_p) +") avec une seule ville : ", float(mono_a)/(nb_articles-mixtes_p)*100, "%")


	print("\n ############## Nombre de soumissions ############## \n")

	# Taux d’acceptation fonction du nombre d'article soumis 
	nb_accept_vs_nb_sub = defaultdict(int)
	nb_articles_vs_nb_sub = defaultdict(int)
	for id, p in articles.items():
		for a in p["authors"]: 
			articles_aut = authors[a]["nb_articles"] 
			nb_articles_vs_nb_sub[articles_aut] += 1
			if ispublished(p):
				nb_accept_vs_nb_sub[articles_aut] += 1

	print("nombre total d'auteurs :", len(authors))
	print("Taux d'acceptation par nombre de soumission :")
	for nb_sub in sorted(nb_accept_vs_nb_sub.keys()):
		if nb_sub > 0:
			nb_a = nb_accept_vs_nb_sub[nb_sub]
			nb_p = nb_articles_vs_nb_sub[nb_sub]
			print("\t - Les ("+str(int(float(nb_p)/nb_sub))+") auteurs ayant", nb_sub ,"soumissions ont un taux d'acceptation moyen de", float(nb_a)/nb_p*100 ,"% ("+str(nb_a)+"/"+str(nb_p)+")")
		else:
			print("\t -", nb_p, "auteurs n'ont aucune publication")

	# Qui sont-ils ?
	print("Ceux qui publient beaucoup (participation estimée sur le postulat que tous les co-auteurs d'un article participent à hauteurs égales)" )
	for name,aut in authors.items():
		if aut["nb_articles"] >= 2:
			print("\t - ", name, aut["nb_accepts"], '/', aut["nb_articles"], "soumissions, participation estimée :", aut["articles"], " article écrit, \n taux acceptation (pondéré)", float(aut["publish"])/aut["articles"]*100 ,"taux acceptation (brut)", float(aut["nb_accepts"])/aut["nb_articles"]*100)

def first_according_to(authors, key):
	nb_rangs = 5 
	for name,aut in sorted(authors.items(), key=lambda x: authors[x[0]][key], reverse=True):
		if aut["articles"] != 0:
			print("\t - ", name, " participation : ", aut["articles"], ", publiés : ", aut["publish"] , ", ratio : ", float(aut["publish"])/aut["articles"]*100)
		nb_rangs -= 1
		if (nb_rangs == 0):
			break

print("Les auteurs qui ont écrit le plus de texte soumis: ")
first_according_to(authors,"articles")
print("Les auteurs qui ont écrit le plus de texte accepté: ")
first_according_to(authors,"publish")

def byLetter():
	# ordre alphabétique et acceptation /
	first_letter_vs_accept = defaultdict(int)
	first_letter_vs_nb_articles = defaultdict(int)
	first_letter_vs_nb_persons = defaultdict(int)
	for name, aut in authors.items():
		if ' ' not in name: continue
		l = name.split(' ')[1][0] # Première lettre du nom
		first_letter_vs_nb_articles[l] += aut["articles"]
		first_letter_vs_accept[l] += aut["publish"]
		first_letter_vs_nb_persons[l] += 1
	print("Taux d'acceptation par première lettre du nom :" )
	# Triés par:
	#for l in sorted(first_letter_vs_accept.keys(), key=lambda x : float(first_letter_vs_accept[x])/first_letter_vs_nb_articles[x], reverse=True):
	for l in sorted(first_letter_vs_accept.keys(), key=lambda x : first_letter_vs_nb_articles[x], reverse=True):
		nb_p = first_letter_vs_nb_articles[l]
		nb_a = first_letter_vs_accept[l]
		persons = first_letter_vs_nb_persons[l]
		if nb_p > 0:
			print("\t - ", l.upper(), "("+str(persons)+"/"+str(nb_authors)+") : ", float(nb_a)/nb_p*100, "%" )

	size = list()
	x_tick = list()
	x = list()
	y = list()
	i = 0
	for l in sorted(first_letter_vs_accept.keys()):
		x_tick.append(l)
		if first_letter_vs_nb_articles[l] > 0:
			y.append(float(first_letter_vs_accept[l])/first_letter_vs_nb_articles[l]*100)
			x.append(i)
			i += 1	
			size.append(first_letter_vs_nb_persons[l]**2)

	print(x)
	print(y)
	print(size)

	fig = plt.figure()
	plt.ylabel("Pourcentage d acceptation")
	plt.xlabel('Premiere lettre du nom')
	plt.scatter(x,y,s=size)

	plt.xticks(x,x_tick)
	plt.xlim(min(x)-1, max(x)+1) 
	plt.ylim(min(y)-1, max(y)+1) 

	pp = PdfPages("premiere_lettre.pdf")
	pp.savefig(fig, bbox_inches='tight')
	pp.close()

def cityMap(withLinks=False):
	cityAuthor = {}
	for name, a in authors.items():
		if a["city"] not in cityAuthor: 
			cityAuthor[a["city"]] = 0
		cityAuthor[a["city"]] += 1
	
	img = Image.open('France.jpg')
	draw = ImageDraw.Draw(img)
	
	if withLinks:
		for k, p in articles.items():
			for a1 in p['authors']:
				for a2 in p['authors']:
					if a1 >= a2 or authors[a1]['city'] ==  authors[a2]['city']: continue
					x1,y1 = cityCoordinates[authors[a1]['city']]
					x2,y2 = cityCoordinates[authors[a2]['city']]
					draw.line((x1, y1, x2, y2), 'red', width=2)
	
	
	
	for c in ['New Delhi', 'Wrocław', 'Bucharest']:
		if c not in cityCoordinates: continue
		x, y = cityCoordinates[c]
		v = 1
		fsize = (math.ceil(v**0.8)+6)*4
		font = ImageFont.truetype('/Library/Fonts/Arial.ttf', fsize)
		w, h = draw.textsize(c, font=font)
		draw.text((x-w-25, y-h/2), c, (0, 0, 0), font=font)

	for c, v in cityAuthor.items():
		if c not in cityCoordinates: continue
		x, y = cityCoordinates[c]
		txt = str(v)
		fsize = (math.ceil(v**0.8)+5)*4
		font = ImageFont.truetype('/Library/Fonts/Arial.ttf', fsize)
		w, h = draw.textsize(txt, font=font)
		m = max(w,h)
		draw.ellipse((x-m, y-m, x+m, y+m), fill = (200,200,200), outline ='black')
		draw.text((x-w/2, y-h/2), txt, (0, 0, 0), font=font)
	
	img.save('France_with_stats.jpg')

def linkMap():
	img = Image.open('France.jpg')
	draw = ImageDraw.Draw(img)

	for k, p in articles.items():
		for a1 in p['authors']:
			for a2 in p['authors']:
				if a1 >= a2 or authors[a1]['city'] ==  authors[a2]['city']: continue
				x1,y1 = cityCoordinates[authors[a1]['city']]
				x2,y2 = cityCoordinates[authors[a2]['city']]
				draw.line((x1, y1, x2, y2), 'red', width=2)

	img.save('France_with_links.jpg')
					


		

statByDate()
byLetter()
upload_and_acceptation()

cityMap(withLinks=True)
#linkMap()








