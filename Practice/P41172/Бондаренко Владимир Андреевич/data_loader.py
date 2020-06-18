import csv
from rdflib import  Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import re


def check_obj(name):
    if name in obj_buff:
        return obj_buff[name]
    else:
        return obj_buff.setdefault(name, URIRef(prefix + re.sub('\W', '_', name)))


def label(s):
    return str(g.label(s))


def regex_prepare(name):
    return re.sub('\W', '_', name)


g = Graph()
g.parse("scam_base.owl")
pref = dict(g.namespaces())['']

g.bind('pref', pref)
with open("data.csv") as fp:
    reader = csv.reader(fp, delimiter=";")
    data_read = [row for row in reader if row]
prefix = dict(g.namespaces())['']
classes = {label(o):o for o, p, s in g if p == RDF.type and s == OWL.Class}
properties = {label(o):o for o, p, s in g if p == RDF.type and s == OWL.ObjectProperty}
obj_buff = {}


for [object_, property_, subject] in data_read:
    if property_ == 'a':
        if subject not in classes:
            raise ValueError(f'Unknown class: {subject}')
        g.add((check_obj(object_), RDF.type, OWL.NamedIndividual))
        g.add((check_obj(object_), RDF.type, classes[subject]))
        g.add((check_obj(object_), RDFS.label, Literal(object_)))
    else:
        if object_ not in obj_buff:
            raise ValueError(f'Object {object_} doesnt exist')
        if subject not in obj_buff:
            raise ValueError(f'Object {subject} doesnt exist')
        if property_ not in properties:
            raise ValueError(f'Unknown property: {property_}')
        g.add((check_obj(object_), properties[property_], check_obj(subject)))

### Скаммерские компании в Мумбае
q1 = g.query(
    """SELECT ?comp
       WHERE {{
          ?comp rdf:type :Half-legal_company;
                         :Located_at :Mumbai__India
       }}""")
for q in q1:
    print(q)
print('#'*20)

### Персональные номера "продавцов", числящихся в Tech_Support_Pro
q2= g.query(
    """SELECT ?label
       WHERE {{
          ?scammer a :Popup_seller;
            :Employee_of :Tech_Support_Pro; 
            :Using_phone_number ?number.
          ?number rdfs:label ?label.  
       }}""")
for q in q2:
    print(q)
print('#' * 20)
### Все известные работники скаммерскийх организаций
q3= g.query(
    """SELECT ?person
       WHERE {{
          ?company a :Half-legal_company.
          ?person :Employee_of ?company.
       }}""")
for q in q3:
    print(q)
print('#' * 20)
### Количество номеров используемых организацией
q4= g.query(
    """SELECT ?company (COUNT(?company) AS ?numOfWorkers)
       WHERE {
          ?company a :Half-legal_company.
          ?company :Owns_VoIP_phone_number  ?number.
       }
       GROUP BY ?company
       ORDER BY DESC(?numOfWorkers)""")
for q in q4:
    print(q)
print('#' * 20)