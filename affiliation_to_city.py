# Script qui converti le fichier
authors_file="authors.csv"
# en fichier
authors_wc_file="authors_withcity.csv"
# qui contient un champs en plus "Ville (Labo)"

# si l'affiliation contient "le texte de gauche", 
# alors ça ville est "le texte de droite"
# Si l'affiliation d'une personne en particulier
# n'est pas "détectable", alors on peut lui affecter un ville/labo
# directemetn en ajoutant une ligne avec son email:
# ex:
#    'bramas@unistra.fr' : 'Strasbourg',

# attention c'est sensible à la casse.


a2c = {
    'Sorbonne Université': 'Paris',
    'Universite Pierre et Marie Curie': 'Paris',
    'Nokia Bell Labs': 'Paris',
    'Saclay': 'Paris',
    'Paris': 'Paris',
    'Caisse des Depots': 'Paris',
    'Cnam': 'Paris',
    'CNAM': 'Paris',
    'IRIT': 'Toulouse',
    'Toulouse': 'Toulouse',
    'LAAS': 'Toulouse',
    'Strasbourg': 'Strasbourg',
    'UDS': 'Strasbourg',
    'Nantes': 'Nantes',
    'LIP6': 'Paris',
    'LRI': 'Paris',
    'LIG': 'Grenoble',
    'VERIMAG': 'Grenoble',
    'Clermont': 'Clermont-Ferrand',
    'Bordeaux': 'Bordeaux',
    'Compiègne': 'Compiègne',
    'Comiègne': 'Compiègne',
    'Roma': 'Roma, Italy',
    'Université Côte d’Azur': 'Nice',
    'Université Côte d\'Azur': 'Nice',
    'Université de Picardie': 'Amiens',
    'Lyon': 'Lyon',
    'Laboratoire d\'Informatique du Parallélisme': 'Lyon',
    'CISPA Helmholtz Center for Information Security': 'Saarbrücken',
    'Orange Labs': 'Paris',
    'Huawei': 'Paris',
    'Polytechnique Hauts-de-France': 'Valenciennes',
    'Jamia Millia Islamia': 'New Delhi',
    'INRIA Sophia-Antipolis': 'Nice',
    'Wrocław University of Science and Technology': 'Wrocław',
    'Université Technologique d\'Eindhoven': 'Eindhoven',
    'Bucharest': 'Bucharest',
    '@lesfurets.com' : 'Paris',
    '@ens-lyon.org': 'Lyon',
}

a2lab = {
    'Sorbonne Université': 'Sorbonne Université Lip6 UPMC',
    'Universite Pierre et Marie Curie': 'Sorbonne Université Lip6 UPMC',
    'LIP6': 'Sorbonne Université Lip6 UPMC',
    'Nokia Bell Labs': 'Paris',
    'Saclay': 'Saclay',
    'Caisse des Depots': 'Caisse des Depots',
    'Cnam': 'CNAM',
    'CNAM': 'CNAM',
    'I3S': 'I3S',
    'IRIT': 'IRIT',
    'LAAS': 'LAAS',
    'Strasbourg': 'ICUBE',
    'UDS': 'ICUBE',
    'LRI': 'LRI',
    'LIG': 'LIG',
    'VERIMAG': 'VERIMAG',
    'Université Clermont': 'LIMOS',
    'Compiègne': 'Compiègne',
    'Comiègne': 'Compiègne',
    'Laboratoire d\'Informatique du Parallélisme': 'LIP',
    'CISPA Helmholtz Center for Information Security': 'CISPA Helmholtz Center for Information Security',
    'Orange Labs': 'Orange Labs',
    'Huawei': 'Huawei',
    'Polytechnique Hauts-de-France': 'Polytechnique Hauts-de-France',
    'Jamia Millia Islamia': 'Jamia Millia Islamia',
    'INRIA Sophia-Antipolis': 'I3S',
    'Wrocław University of Science and Technology': 'Wrocław',
    'Université Technologique d\'Eindhoven': 'Eindhoven',
    'Bucharest': 'Bucharest',
    '@lesfurets.com' : 'lesfurets',
    '@ens-lyon.org': 'ENS Lyon',
    '@cnrs.fr': 'CNRS',
    'INSPE': 'INSPE',
    'LaBRI': 'LaBRI',
    'Nantes': 'L2S',
    'LIMOS': 'LIMOS',
    'Sapienza Università': 'Sapienza Università',
    'MIS': 'MIS',
    '@lri.fr': 'LRI'
}


import csv


def findCity(affiliation):
    for a, c in a2c.items():
        if a in affiliation:
            return c
    return None

def findLab(affiliation):
    for a, c in a2lab.items():
        if a in affiliation:
            return c
    return None

with open(authors_file) as f: 
    with open(authors_wc_file, 'w') as out: 
        r = csv.reader(f, delimiter=';', quotechar='"')
        nb_authors = 0
        for author in r:
            id, name, mail, country, affiliation = author  
            city = findCity(affiliation)
            if city is None:
                city = findCity(mail)
                if city is None:
                    print(mail, affiliation)
                    exit(1)
            lab = findLab(affiliation)
            if lab is None:
                lab = findLab(mail)
                if lab is None:
                    print('lab', mail, affiliation)
                    exit(1)
            out.write('"'+id+'";"'+name+'";"'+mail+'";"'+country+'";"'+affiliation+'";"'+city+' ('+lab+')"\n')
        out.close()
            