import csv
import random
import owlready2
from owlready2 import *
import rdflib
from rdflib.plugins import sparql
from rdflib import URIRef, BNode, Literal, Namespace, Graph


def csv_read(file):
    reader = csv.reader(file)
    for row in reader:
        data.append(row)

data = []
csv_path = "data3.csv"
with open(csv_path, "r") as obj:
    csv_read(obj)
del data[0]


owlready2.JAVA_EXE = "C:/Program Files/Java/jre1.8.0_291/bin/java.exe" 

onto = get_ontology("C:/My/Projects/Ontology.owl")
onto.load()

Person1 = onto.Person("Person1")
Subject1 = onto.Subjects("Subject1")
People1 = onto.People("People1")

Add_Tool = onto.AdditionalTool("Add_Tool")

LocationIn = onto.Indoors("LocationIn")
LocationOut = onto.Outdoors("LocationOut")




for i in range(36):
    Lens = onto.TypeLens("Lens" + str(i))
    Lens.FocalLenght = int(data[i][1])
    Lens.AnglePicture = int(data[i][2])
    Lens.MinApecture = int(data[i][5])
    Lens.MaxApecture = float(data[i][4])
    

sync_reasoner_pellet()


for i in range(36):
    Loca = random.choice([LocationIn, LocationOut])
    Model = random.choice([People1, Person1, Subject1])

    Type = onto.TypeOfPhoto("Type" + str(i))
    Type.hasTypeLens = Lens
    Type.hasPlace = Loca
    Type.hasTarget = Model
    
    is_Tool = random.choice([True, False])
    if is_Tool:
        Type.hasAdditionalTool = Add_Tool
    else:
        pass

sync_reasoner_pellet()


prefix = "http://www.semanticweb.org/user/ontologies/2021/3/untitled-ontology-132#"
graph = default_world.as_rdflib_graph() 

# I.    Виды съемок при 20 объективе
typel = '20'
q1 = list(graph.query("""PREFIX : <http://www.semanticweb.org/user/ontologies/2021/3/untitled-ontology-132#> 
                         PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?formatName WHERE 
          { ?len rdf:type owl:NamedIndividual;
                 rdf:type :TypeLens;
                 rdf:type :20.
            ?formatType :hasTypeLens ?len.
            ?formatType rdf:type ?formatName
            FILTER(?formatName != :TypeOfPhoto)
            FILTER(?formatName != owl:NamedIndividual)                        
          }"""))

# for row in q1:
#     print(f'Вид съёмок при 20 объетиве - {row[0].replace(prefix, "")}')

# II.   При каких значениях характеристик классифицируется 20 объектив?
q2 = list(graph.query("""PREFIX : <http://www.semanticweb.org/user/ontologies/2021/3/untitled-ontology-132#> 
                         PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?FocalL ?Angle ?MaxAp ?MinAp WHERE 
          { ?len rdf:type owl:NamedIndividual;
                 rdf:type :TypeLens;
                 rdf:type :20.
            ?len :FocalLenght ?FocalL.
            ?len :AnglePicture ?Angle.
            ?len :MaxApecture ?MaxAp.
            ?len :MinApecture ?MinAp.                    
          }"""))

# for focal, angle, maxap, minap in q2:
#     print(f'Характеристики для 20 объектива - {focal} | {angle} | {maxap} | {minap}')


# III.  К какому типу съемки может подойти соответствующий тип объектива?
q3 = list(graph.query("""PREFIX : <http://www.semanticweb.org/user/ontologies/2021/3/untitled-ontology-132#> 
                         PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?len ?typePh WHERE 
          { ?l rdf:type :TypeLens;
                rdf:type ?len.
            FILTER(?len != :TypeLens)
            FILTER(?len != owl:NamedIndividual)
            ?type rdf:type owl:NamedIndividual;
                  rdf:type :TypeOfPhoto;
                  rdf:type ?typePh.
            FILTER(?typePh != :TypeOfPhoto)
            FILTER(?typePh != owl:NamedIndividual)
          }"""))

for row1, row2 in q3:
    print(f'Объектив {row1.replace(prefix, "")} подходит для {row2.replace(prefix, "")} съёмки.')



#onto.save(file = "TestOwl9.owl")
