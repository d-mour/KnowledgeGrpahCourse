import rdflib
from rdflib import Graph,BNode, Literal, RDF,RDFS,OWL, URIRef
from rdflib.namespace import XSD
import csv

g = Graph()
g.parse("Cars_faults.owl")
pref = dict(g.namespaces())['']
print("PREFIX is: ", pref)
g.bind('pref', pref)

predicates = {}
for s, p, o in g.triples((None, RDFS.range, None)):
    predicates[s] = o == XSD.string

file = open('Entities.csv', 'r')
reader = csv.reader(file)
next(reader)
subjects = {}

for s, p, o in reader:
    if p == "a":
        new = BNode()
        g.add((new, RDF.type, pref + o))
        subjects[s] = new
    else:
        if predicates[pref+p]:
            g.add((subjects[s], pref + p, Literal(o)))
        else:
            g.add((subjects[s], pref + p, subjects[o]))

# Вывести названия всех авто
query_res1 = g.query(
    """SELECT ?Car_Model
       WHERE {
          ?object a pref:Car.
          ?object pref:Has_car_model_name ?Car_Model.
       }""")

# вывести описание всех ошибок для TOYOTA RAV4
queru_res2 = g.query(
    """SELECT ?code ?code_desc
       WHERE {
          ?object a pref:Fault_code.
          ?object pref:Has_code ?code.
          ?object pref:Has_fault_code_description ?code_desc.
          ?object pref:Appears_on_a_car ?car.
          ?car pref:Has_car_model_name "RAV4"
       }""")

# Для автомобиля RAV4 с ошибкой P0115 вывести способы диагностики возможных неисправностей и способы устранения
query_res3 = g.query(
    """SELECT ?f_desc ?t_desc ?h_desc
        WHERE {
            ?symptom a pref:Symptoms.
            ?symptom pref:Occurs_on ?car.
            ?car pref:Has_car_model_name "RAV4".
            ?symptom pref:Have_fault_code ?code.
            ?symptom pref:Tell_to_do ?todo.
            ?todo pref:Finds_out_fault ?fault.
            ?fault pref:Has_fault_description ?f_desc.
            ?todo pref:Has_todo_description ?t_desc.
            ?code pref:Has_code "P0115".
            ?fix a pref:Way_to_fix.
            ?fix pref:Aims_to_fix ?fault.
            ?fix pref:Fits_with ?car.
            ?fix pref:How_to_fix ?h_desc.
        }""")

print()
print("Список Авто: ")
for row in query_res1:
    print("%s" % row)

print()
print("Коды ошибок для TOYOTA RAV4:")
for row in queru_res2:
    print("Код ошибки: %s, Описание: %s" % row)

print()
print("На RAV4 компьютер выдает ошибку P0115:")
for row in query_res3:
    print("     Возможная неисправность:    %s" % row[0])
    print("     Что нужно сделать:          %s" % row[1])
    print("     Способ исправления:         %s" % row[2])
    print()

