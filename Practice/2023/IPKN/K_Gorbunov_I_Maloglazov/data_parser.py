import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import OWL, RDFS, XSD

# Load data from CSV file
df = pd.read_csv('tickets.csv')
users_df = pd.read_csv('users.csv')

reverse_topic_mapping = {
    'Bank Account services' :0,
    'Credit card or prepaid card':1,
    'Others':2,
    'Theft/Dispute Reporting':3,
    'Mortgage/Loan':4
}

# Create an RDF graph
graph = Graph()

# Define the ontology namespace
onto = Namespace("http://example.org/ontology#")

# Bind namespace prefixes
graph.bind("", onto)
graph.bind("owl", OWL)
graph.bind("rdf", RDF)
graph.bind("rdfs", RDFS)
graph.bind("xsd", XSD)


# Датасет

dataset_uri = onto.BankClientTickets
graph.add((dataset_uri, RDF.type, onto.Dataset))
graph.add((dataset_uri, RDFS.label, Literal("BankClientTickets")))
graph.add((dataset_uri, onto.hasDateCreate, Literal('20.04.2023', datatype=XSD.string)))
graph.add((dataset_uri, onto.hasRowsNum, Literal(1000, datatype=XSD.integer)))

# Модели классификации

model1_uri = onto.SVMClassifier
graph.add((model1_uri, RDF.type, onto.Model))
graph.add((model1_uri, RDFS.label, Literal("SVMClassifier")))
graph.add((model1_uri, onto.hasAccuracy, Literal(0.91, datatype=XSD.double)))
graph.add((model1_uri, onto.isTrainedOn, dataset_uri))

model2_uri = onto.LogRegClassifier
graph.add((model2_uri, RDF.type, onto.Model))
graph.add((model2_uri, RDFS.label, Literal("LogRegClassifier")))
graph.add((model2_uri, onto.hasAccuracy, Literal(0.90, datatype=XSD.double)))
graph.add((model2_uri, onto.isTrainedOn, dataset_uri))

model3_uri = onto.SequentialClassifier
graph.add((model3_uri, RDF.type, onto.Model))
graph.add((model3_uri, RDFS.label, Literal("SequentialClassifier")))
graph.add((model3_uri, onto.hasAccuracy, Literal(0.98, datatype=XSD.double)))
graph.add((model3_uri, onto.isTrainedOn, dataset_uri))

# Департаменты
finance_department_uri = onto.FinanceDepartment
graph.add((finance_department_uri, RDF.type, onto.Department))
graph.add((finance_department_uri, RDFS.label, Literal("FinanceDepartment")))

technical_department_uri = onto.TechnicalDepartment
graph.add((finance_department_uri, RDF.type, onto.Department))
graph.add((finance_department_uri, RDFS.label, Literal("TechnicalDepartment")))

sales_department_uri = onto.SalesDepartment
graph.add((finance_department_uri, RDF.type, onto.Department))
graph.add((finance_department_uri, RDFS.label, Literal("SalesDepartment")))

trash_department_uri = onto.Trash
graph.add((finance_department_uri, RDF.type, onto.Department))
graph.add((finance_department_uri, RDFS.label, Literal("Trash")))

i = 0


# Iterate over each row in the dataframe
for _, row in df.iterrows():    
    # Create URI for user individual
    userId = row['User']
    i+=1

    user = (users_df[users_df['UserId'] == userId].head(1).values.flatten().tolist())

    user_uri = onto[userId]

    # Add user individual to graph
    graph.add((user_uri, RDF.type, onto.User))
    graph.add((user_uri, RDFS.label, Literal(userId)))
    graph.add((user_uri, onto.hasName, Literal(user[2], datatype=XSD.string)))
    graph.add((user_uri, onto.hasPhone, Literal(user[3], datatype=XSD.string)))
    graph.add((user_uri, onto.hasEmail, Literal(user[4], datatype=XSD.string)))

    # Create URI for support request individual
    requestId = row['TicketId']
    i+=1
    support_request_uri = onto[requestId]
    
    # Add support request individual to graph
    graph.add((support_request_uri, RDF.type, onto.Ticket))
    graph.add((support_request_uri, RDFS.label, Literal(requestId)))
    graph.add((support_request_uri, onto.hasTextMessage, Literal(row['complaint_text'], datatype=XSD.string)))

    model = row['isClassifiedBy']
    if(model == 'SVMClassifier'):
        graph.add((support_request_uri, onto.isClassifiedBy, model1_uri))
    elif(model == 'LogRegClassifier'):
        graph.add((support_request_uri, onto.isClassifiedBy, model2_uri))
    else:
        graph.add((support_request_uri, onto.isClassifiedBy, model3_uri))

    # Add relationship between user and support request
    graph.add((support_request_uri, onto.isCreatedBy, user_uri))

    # Classify support request into a department
    if row['Topic'] == 4:
        graph.add((support_request_uri, onto.isClassifiedInto, finance_department_uri))
        graph.add((support_request_uri, onto.isRoutedTo, finance_department_uri))
    elif row['Topic'] == 1:
        graph.add((support_request_uri, onto.isClassifiedInto, technical_department_uri))
        graph.add((support_request_uri, onto.isRoutedTo, technical_department_uri))
    elif row['Topic'] == 0:
        graph.add((support_request_uri, onto.isClassifiedInto, sales_department_uri))
        graph.add((support_request_uri, onto.isRoutedTo, sales_department_uri))
    else:
        graph.add((support_request_uri, onto.isClassifiedInto, trash_department_uri))
        graph.add((support_request_uri, onto.isRoutedTo, trash_department_uri))


# Save the graph as an file
graph.serialize(destination='data.owl', format='turtle')