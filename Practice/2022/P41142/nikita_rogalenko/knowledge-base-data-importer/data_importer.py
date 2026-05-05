from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, XSD
import json
import datetime
import re


ONTOLOGY_IRI = "https://github.com/RogoGit/F1-knowledge-base/f1-ontology"
f1_graph = Graph()


# Classes
driver_class = URIRef(f"{ONTOLOGY_IRI}#Driver")
car_class = URIRef(f"{ONTOLOGY_IRI}#Car")
car_driving_class = URIRef(f"{ONTOLOGY_IRI}#CarDriving")
circuit_class = URIRef(f"{ONTOLOGY_IRI}#Circuit")
death_accident_class = URIRef(f"{ONTOLOGY_IRI}#DeathAccident")
grand_prix_class = URIRef(f"{ONTOLOGY_IRI}#GrandPrix")
grand_prix_result_class = URIRef(f"{ONTOLOGY_IRI}#GrandPrixResult")
race_result_class = URIRef(f"{ONTOLOGY_IRI}#RaceResult")
qualifying_result_class = URIRef(f"{ONTOLOGY_IRI}#QualifyingResult")
related_creation_class = URIRef(f"{ONTOLOGY_IRI}#RelatedCreation")
creation_can_be_about_class = URIRef(f"{ONTOLOGY_IRI}#CreationCanBeAbout")
book_class = URIRef(f"{ONTOLOGY_IRI}#Book")
movie_class = URIRef(f"{ONTOLOGY_IRI}#Movie")
season_class = URIRef(f"{ONTOLOGY_IRI}#Season")
season_result_class = URIRef(f"{ONTOLOGY_IRI}#SeasonResult")
driver_standing_class = URIRef(f"{ONTOLOGY_IRI}#DriverStanding")
constructor_standing_class = URIRef(f"{ONTOLOGY_IRI}#ConstructorStanding")
team_class = URIRef(f"{ONTOLOGY_IRI}#Team")
team_participation_class = URIRef(f"{ONTOLOGY_IRI}#TeamParticipation")

# Object properties
drivingHasHappenedInSeason_op = URIRef(f"{ONTOLOGY_IRI}#drivingHasHappenedInSeason")    #
grandPrixResultIsRelatedTo_op = URIRef(f"{ONTOLOGY_IRI}#grandPrixResultIsRelatedTo")    #
hasCarDriving_op = URIRef(f"{ONTOLOGY_IRI}#hasCarDriving")  #
hasConstructorStandingResult_op = URIRef(f"{ONTOLOGY_IRI}#hasConstructorStandingResult")    #
hasDiedIn_op = URIRef(f"{ONTOLOGY_IRI}#hasDiedIn")  #
hasDriver_op = URIRef(f"{ONTOLOGY_IRI}#hasDriver")  #
hasDriverDriving_op = URIRef(f"{ONTOLOGY_IRI}#hasDriverDriving")    #
hasDriverGrandPrixResult_op = URIRef(f"{ONTOLOGY_IRI}#hasDriverGrandPrixResult")    #
hasDriverParticipation_op = URIRef(f"{ONTOLOGY_IRI}#hasDriverParticipation")    #
hasDriverStandingResult_op = URIRef(f"{ONTOLOGY_IRI}#hasDriverStandingResult")  #
hasEverBeenATeammate_op = URIRef(f"{ONTOLOGY_IRI}#hasEverBeenATeammate")
hasGrandPrixResult_op = URIRef(f"{ONTOLOGY_IRI}#hasGrandPrixResult")    #
hasResult_op = URIRef(f"{ONTOLOGY_IRI}#hasResult")  #
hasTeam_op = URIRef(f"{ONTOLOGY_IRI}#hasTeam")  #
hasTeamParticipation_op = URIRef(f"{ONTOLOGY_IRI}#hasTeamParticipation")    #
inEvent_op = URIRef(f"{ONTOLOGY_IRI}#inEvent")  #
isAbout_op = URIRef(f"{ONTOLOGY_IRI}#isAbout")
isConstructedBy_op = URIRef(f"{ONTOLOGY_IRI}#isConstructedBy")  #
isConstructorOf_op = URIRef(f"{ONTOLOGY_IRI}#isConstructorOf")  #
isHappendInSeason_op = URIRef(f"{ONTOLOGY_IRI}#isHappendInSeason")  #
isPartOf_op = URIRef(f"{ONTOLOGY_IRI}#isPartOf")    #
seasonConstructorResultIsRelatedTo_op = URIRef(f"{ONTOLOGY_IRI}#seasonConstructorResultIsRelatedTo")    #
seasonDriverResultIsRelatedTo_op = URIRef(f"{ONTOLOGY_IRI}#seasonDriverResultIsRelatedTo")  #
tookPlaceIn_op = URIRef(f"{ONTOLOGY_IRI}#tookPlaceIn")  #

# Data properties
wikipediaUrl_dp = URIRef(f"{ONTOLOGY_IRI}#wikipediaUrl")
# Driver (f1_ergast data)
firstName_dp = URIRef(f"{ONTOLOGY_IRI}#firstName")
birthDate_dp = URIRef(f"{ONTOLOGY_IRI}#birthDate")
driverCode_dp = URIRef(f"{ONTOLOGY_IRI}#driverCode")
lastName_dp = URIRef(f"{ONTOLOGY_IRI}#lastName")
nationality_dp = URIRef(f"{ONTOLOGY_IRI}#nationality")
permanentNumber_dp = URIRef(f"{ONTOLOGY_IRI}#permanentNumber")
# Car (f1_technical)
carDesigners_dp = URIRef(f"{ONTOLOGY_IRI}#carDesigners")
carModel_dp = URIRef(f"{ONTOLOGY_IRI}#carModel")
chassisDescription_dp = URIRef(f"{ONTOLOGY_IRI}#chassisDescription")
dimensions_dp = URIRef(f"{ONTOLOGY_IRI}#dimensions")
engineDescription_dp = URIRef(f"{ONTOLOGY_IRI}#engineDescription")
specifications_dp = URIRef(f"{ONTOLOGY_IRI}#specifications")
transmission_dp = URIRef(f"{ONTOLOGY_IRI}#transmission")
# Team (f1_technical, ergast)
foundYear_dp = URIRef(f"{ONTOLOGY_IRI}#foundYear")
teamBasedIn_dp = URIRef(f"{ONTOLOGY_IRI}#teamBasedIn")
teamCountry_dp = URIRef(f"{ONTOLOGY_IRI}#teamCountry")
teamName_dp = URIRef(f"{ONTOLOGY_IRI}#teamName")
# Death Accident (f1_fansite)
accidentDate_dp = URIRef(f"{ONTOLOGY_IRI}#accidentDate")
accidentSession_dp = URIRef(f"{ONTOLOGY_IRI}#accidentSession")
deathCause_dp = URIRef(f"{ONTOLOGY_IRI}#deathCause")
# Season (ergast)
seasonYear_dp = URIRef(f"{ONTOLOGY_IRI}#seasonYear")
# Season results (ergast)
totalPoints_dp = URIRef(f"{ONTOLOGY_IRI}#totalPoints")
totalPosition_dp = URIRef(f"{ONTOLOGY_IRI}#totalPosition")
winsNum_dp = URIRef(f"{ONTOLOGY_IRI}#winsNum")
# Related Creation
creationTitle_dp = URIRef(f"{ONTOLOGY_IRI}#creationTitle")
creationDate_dp = URIRef(f"{ONTOLOGY_IRI}#creationDate")
genre_dp = URIRef(f"{ONTOLOGY_IRI}#genre")
ratingsNum_dp = URIRef(f"{ONTOLOGY_IRI}#ratingsNum")
description_dp = URIRef(f"{ONTOLOGY_IRI}#description")
# Movie
movieDuration_dp = URIRef(f"{ONTOLOGY_IRI}#movieDuration")
imDbRating_dp = URIRef(f"{ONTOLOGY_IRI}#imDbRating")
metacriticRating_dp = URIRef(f"{ONTOLOGY_IRI}#metacriticRating")
# Book
author_dp = URIRef(f"{ONTOLOGY_IRI}#author")
pages_dp = URIRef(f"{ONTOLOGY_IRI}#pages")
reviewsNum_dp = URIRef(f"{ONTOLOGY_IRI}#reviewsNum")
goodreadsRating_dp = URIRef(f"{ONTOLOGY_IRI}#goodreadsRating")
# Grand Prix (ergast, f1 fansite)
grandPrixDate_dp = URIRef(f"{ONTOLOGY_IRI}#grandPrixDate")
grandPrixName_dp = URIRef(f"{ONTOLOGY_IRI}#grandPrixName")
seasonRound_dp = URIRef(f"{ONTOLOGY_IRI}#seasonRound")
totalLaps_dp = URIRef(f"{ONTOLOGY_IRI}#totalLaps")
distance_dp = URIRef(f"{ONTOLOGY_IRI}#distance")
# Circuit (ergast, f1 fansite)
circuitName_dp = URIRef(f"{ONTOLOGY_IRI}#circuitName")
circuitCountry_dp = URIRef(f"{ONTOLOGY_IRI}#circuitCountry")
circuitLocality_dp = URIRef(f"{ONTOLOGY_IRI}#circuitLocality")
circuitLocationLat_dp = URIRef(f"{ONTOLOGY_IRI}#circuitLocationLat")
circuitLocationLong_dp = URIRef(f"{ONTOLOGY_IRI}#circuitLocationLong")
circuitType_dp = URIRef(f"{ONTOLOGY_IRI}#circuitType")
lapDistance_dp = URIRef(f"{ONTOLOGY_IRI}#lapDistance")
# Grand Prix results (ergast)
driverNumber_dp = URIRef(f"{ONTOLOGY_IRI}#driverNumber")
driverPosition_dp = URIRef(f"{ONTOLOGY_IRI}#driverPosition")
# Race results (ergast)
points_dp = URIRef(f"{ONTOLOGY_IRI}#points")
raceTime_dp = URIRef(f"{ONTOLOGY_IRI}#raceTime")
finalStatus_dp = URIRef(f"{ONTOLOGY_IRI}#finalStatus")
grid_dp = URIRef(f"{ONTOLOGY_IRI}#grid")
lapsCompleted_dp = URIRef(f"{ONTOLOGY_IRI}#lapsCompleted")
# Qualifying result (ergast)
Q1Time_dp = URIRef(f"{ONTOLOGY_IRI}#Q1Time")
Q2Time_dp = URIRef(f"{ONTOLOGY_IRI}#Q2Time")
Q3Time_dp = URIRef(f"{ONTOLOGY_IRI}#Q3Time")


def load_json_from_file(file_path):
    json_file = open(file_path, 'r')
    result = json.load(json_file)
    json_file.close()
    return result


def add_driver_individual(individual_id, driver_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, driver_class))
    if driver_data["name"] and driver_data["name"].strip():
        f1_graph.add((individual, firstName_dp, Literal(driver_data["name"], datatype=XSD.string)))
    if driver_data["surname"] and driver_data["surname"].strip():
        f1_graph.add((individual, lastName_dp, Literal(driver_data["surname"], datatype=XSD.string)))
    if driver_data["birth_date"] and driver_data["birth_date"].strip():
        f1_graph.add((individual, birthDate_dp,
                      Literal(datetime.datetime.strptime(driver_data["birth_date"], "%d.%m.%Y").strftime("%Y-%m-%d"),
                              datatype=XSD.date)))
    if driver_data["nationality"] and driver_data["nationality"].strip():
        f1_graph.add((individual, nationality_dp, Literal(driver_data["nationality"], datatype=XSD.string)))
    if driver_data["permanent_number"] and driver_data["permanent_number"].strip():
        f1_graph.add((individual, permanentNumber_dp, Literal(driver_data["permanent_number"], datatype=XSD.nonNegativeInteger)))
    if driver_data["driver_code"] and driver_data["driver_code"].strip():
        f1_graph.add((individual, driverCode_dp, Literal(driver_data["driver_code"], datatype=XSD.string)))
    if driver_data["wikipedia_page_url"] and driver_data["wikipedia_page_url"].strip():
        f1_graph.add((individual, wikipediaUrl_dp, Literal(driver_data["wikipedia_page_url"], datatype=XSD.string)))
    return individual


def add_team_individual(individual_id, team_data_ergast, team_data_technical):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, team_class))
    if "name" in team_data_ergast and team_data_ergast["name"].strip():
        f1_graph.add((individual, teamName_dp, Literal(team_data_ergast["name"], datatype=XSD.string)))
    if "wikipedia_page_url" in team_data_ergast and team_data_ergast["wikipedia_page_url"].strip():
        f1_graph.add((individual, wikipediaUrl_dp, Literal(team_data_ergast["wikipedia_page_url"], datatype=XSD.string)))
    if "nationality" in team_data_ergast and team_data_ergast["nationality"].strip():
        f1_graph.add((individual, teamCountry_dp, Literal(team_data_ergast["nationality"], datatype=XSD.string)))
    if team_data_technical is not None and "founded" in team_data_technical and team_data_technical["founded"].strip():
        f1_graph.add((individual, foundYear_dp, Literal(team_data_technical["founded"], datatype=XSD.string)))
    if team_data_technical is not None and "based_in" in team_data_technical and team_data_technical["based_in"].strip():
        f1_graph.add((individual, teamBasedIn_dp, Literal(team_data_technical["based_in"], datatype=XSD.string)))
    return individual


def add_car_individual(individual_id, car_data, teams_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, car_class))
    if car_data["model"] and car_data["model"].strip():
        f1_graph.add((individual, carModel_dp, Literal(car_data["model"], datatype=XSD.string)))
    if "designer" in car_data and car_data["designer"].strip():
        f1_graph.add((individual, carDesigners_dp, Literal(car_data["designer"], datatype=XSD.string)))
    if "chassis" in car_data and car_data["chassis"].strip():
        f1_graph.add((individual, chassisDescription_dp, Literal(car_data["chassis"], datatype=XSD.string)))
    if "dimensions" in car_data and car_data["dimensions"].strip():
        f1_graph.add((individual, dimensions_dp, Literal(car_data["dimensions"], datatype=XSD.string)))
    if "engine" in car_data and car_data["engine"].strip():
        f1_graph.add((individual, engineDescription_dp, Literal(car_data["engine"], datatype=XSD.string)))
    if "specifications" in car_data and car_data["specifications"].strip():
        f1_graph.add((individual, specifications_dp, Literal(car_data["specifications"], datatype=XSD.string)))
    if "transmission" in car_data and car_data["transmission"].strip():
        f1_graph.add((individual, transmission_dp, Literal(car_data["transmission"], datatype=XSD.string)))

    # finding constructor
    constructor_team_matching = next(iter([key for key, value in teams_data.items()
                                           if key.lower() in car_data["team"].replace(' ', '_').lower()]), None)

    if constructor_team_matching is not None:
        team = URIRef(f"{ONTOLOGY_IRI}#team_{teams_data[constructor_team_matching]['name'].replace(' ', '_').lower()}")
        f1_graph.add((individual, isConstructedBy_op, team))
        f1_graph.add((team, isConstructorOf_op, individual))

    return individual


def add_season_individual(individual_id, year, wiki_url):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, season_class))
    f1_graph.add((individual, seasonYear_dp, Literal(year, datatype=XSD.integer)))
    f1_graph.add((individual, wikipediaUrl_dp, Literal(wiki_url, datatype=XSD.string)))
    return individual


def add_team_participation_individual(individual_id, year, participation_data):
    driver_name = participation_data["driver"].replace(" ", "_").replace(";", "")\
        .replace("(has_contract)", "").replace("(confirmed)", "").lower()
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, team_participation_class))
    f1_graph.add((individual, isHappendInSeason_op, URIRef(f"{ONTOLOGY_IRI}#season_{year}")))
    f1_graph.add((individual, hasDriver_op, URIRef(f'{ONTOLOGY_IRI}#driver_{driver_name}')))
    f1_graph.add((individual, hasTeam_op,
                  URIRef(f"{ONTOLOGY_IRI}#team_{participation_data['team'].replace(' ', '_').lower()}")))
    f1_graph.add((URIRef(f'{ONTOLOGY_IRI}#driver_{driver_name}'), hasDriverParticipation_op, individual))
    f1_graph.add((URIRef(f"{ONTOLOGY_IRI}#team_{participation_data['team'].replace(' ', '_').lower()}"),
                  hasTeamParticipation_op, individual))
    return individual


def add_car_driving_individual(individual_id, year, car_data, driver_name):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, car_driving_class))
    f1_graph.add((individual, drivingHasHappenedInSeason_op, URIRef(f"{ONTOLOGY_IRI}#season_{year}")))
    car = URIRef(f"{ONTOLOGY_IRI}#car_{car_data['model'].replace(' ', '_').replace('(', '').replace(')', '').lower()}")
    driver = URIRef(f"{ONTOLOGY_IRI}#driver_{driver_name}")
    f1_graph.add((car, hasCarDriving_op, individual))
    f1_graph.add((driver, hasDriverDriving_op, individual))
    return individual


def add_driver_standing_individual(individual_id, year, season_result, driver_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, driver_standing_class))
    f1_graph.add((individual, totalPoints_dp,  Literal(season_result["points"], datatype=XSD.double)))
    f1_graph.add((individual, totalPosition_dp, Literal(season_result["position"], datatype=XSD.positiveInteger)))
    f1_graph.add((individual, winsNum_dp,  Literal(season_result["wins"], datatype=XSD.nonNegativeInteger)))
    f1_graph.add((URIRef(f"{ONTOLOGY_IRI}#season_{year}"), hasResult_op, individual))
    driver = URIRef(f"{ONTOLOGY_IRI}#driver_{driver_data['name'].replace(' ', '_').lower()}"
                    f"_{driver_data['surname'].replace(' ', '_').lower()}")
    f1_graph.add((individual, seasonDriverResultIsRelatedTo_op, driver))
    f1_graph.add((driver, hasDriverStandingResult_op, individual))
    return individual


def add_constructor_standing_individual(individual_id, year, season_result, constructor_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, constructor_standing_class))
    f1_graph.add((individual, totalPoints_dp,  Literal(season_result["points"], datatype=XSD.double)))
    f1_graph.add((individual, totalPosition_dp, Literal(season_result["position"], datatype=XSD.positiveInteger)))
    f1_graph.add((individual, winsNum_dp,  Literal(season_result["wins"], datatype=XSD.nonNegativeInteger)))
    f1_graph.add((URIRef(f"{ONTOLOGY_IRI}#season_{year}"), hasResult_op, individual))
    constructor = URIRef(f"{ONTOLOGY_IRI}#team_{constructor_data['name'].replace(' ', '_').lower()}")
    f1_graph.add((individual, seasonConstructorResultIsRelatedTo_op, constructor))
    f1_graph.add((constructor, hasConstructorStandingResult_op, individual))
    return individual


def add_circuit_individual(individual_id, circuit_data_ergast, circuit_data_fansite):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, circuit_class))
    f1_graph.add((individual, circuitName_dp, Literal(circuit_data_ergast["name"], datatype=XSD.string)))
    f1_graph.add((individual, circuitCountry_dp, Literal(circuit_data_ergast["country"], datatype=XSD.string)))
    f1_graph.add((individual, circuitLocality_dp, Literal(circuit_data_ergast["locality"], datatype=XSD.string)))
    f1_graph.add((individual, wikipediaUrl_dp, Literal(circuit_data_ergast["wikipedia_page_url"], datatype=XSD.string)))
    f1_graph.add((individual, circuitLocationLat_dp, Literal(circuit_data_ergast["latitude"], datatype=XSD.double)))
    f1_graph.add((individual, circuitLocationLong_dp, Literal(circuit_data_ergast["longitude"], datatype=XSD.double)))
    if circuit_data_fansite is not None:
        f1_graph.add((individual, circuitType_dp, Literal(circuit_data_fansite["type"], datatype=XSD.string)))
        f1_graph.add((individual, lapDistance_dp, Literal(circuit_data_fansite["lap_dist_km"], datatype=XSD.string)))
    return individual


def add_grand_prix_individual(individual_id, grand_prix_data_ergast, grand_prix_data_fansite):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, grand_prix_class))
    f1_graph.add((individual, grandPrixName_dp, Literal(grand_prix_data_ergast["name"], datatype=XSD.string)))
    f1_graph.add((individual, grandPrixDate_dp,
                  Literal(datetime.datetime.strptime(grand_prix_data_ergast["date"], "%d.%m.%Y").strftime("%Y-%m-%d"), datatype=XSD.date)))
    f1_graph.add((individual, seasonRound_dp, Literal(grand_prix_data_ergast["round"], datatype=XSD.positiveInteger)))
    f1_graph.add((individual, wikipediaUrl_dp, Literal(grand_prix_data_ergast["wikipedia_page_url"], datatype=XSD.string)))
    if grand_prix_data_fansite is not None:
        f1_graph.add((individual, totalLaps_dp, Literal(grand_prix_data_fansite["total_laps"], datatype=XSD.positiveInteger)))
        f1_graph.add((individual, distance_dp, Literal(grand_prix_data_fansite["distance_km"], datatype=XSD.string)))
    season = URIRef(f"{ONTOLOGY_IRI}#season_{grand_prix_data_ergast['season']}")
    circuit = URIRef(f"{ONTOLOGY_IRI}#circuit_{grand_prix_data_ergast['ergast_circuit_id'].replace(' ', '_').lower()}")
    f1_graph.add((individual, isPartOf_op, season))
    f1_graph.add((individual, tookPlaceIn_op, circuit))
    return individual


def add_death_accident_individual(individual_id, accident_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, death_accident_class))
    f1_graph.add((individual, accidentDate_dp,
                  Literal(datetime.datetime.strptime(accident_data["incident_date"], "%b %d, %Y").strftime("%Y-%m-%d"),
                          datatype=XSD.date)))
    f1_graph.add((individual, deathCause_dp, Literal(accident_data["cause"], datatype=XSD.string)))
    f1_graph.add((individual, accidentSession_dp, Literal(accident_data["session"], datatype=XSD.string)))
    driver = URIRef(f"{ONTOLOGY_IRI}#driver_{accident_data['driver'].replace(' ', '_').lower()}")
    grand_prix = URIRef(f"{ONTOLOGY_IRI}#grand_prix_{accident_data['incident_date'].split(',')[1].strip()}"
                        f"_{accident_data['event'].replace(' F1', '').replace('GP', 'grand_prix').replace(' ','_').lower()}")
    f1_graph.add((driver, hasDiedIn_op, individual))
    f1_graph.add((individual, inEvent_op, grand_prix))
    return individual


def add_race_result_individual(individual_id, result_data, grand_prix_name, driver_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, race_result_class))
    if "number" in result_data and result_data["number"].strip():
        f1_graph.add((individual, driverNumber_dp, Literal(result_data["number"], datatype=XSD.nonNegativeInteger)))
    f1_graph.add((individual, driverPosition_dp, Literal(result_data["position"], datatype=XSD.positiveInteger)))
    f1_graph.add((individual, points_dp, Literal(result_data["points"], datatype=XSD.double)))
    if "time" in result_data and result_data["time"].strip():
        f1_graph.add((individual, raceTime_dp, Literal(result_data["time"], datatype=XSD.string)))
    f1_graph.add((individual, finalStatus_dp, Literal(result_data["status"], datatype=XSD.string)))
    f1_graph.add((individual, grid_dp, Literal(result_data["grid"], datatype=XSD.nonNegativeInteger)))
    f1_graph.add((individual, lapsCompleted_dp, Literal(result_data["laps"], datatype=XSD.nonNegativeInteger)))
    f1_graph.add((URIRef(f"{ONTOLOGY_IRI}#grand_prix_{grand_prix_name}"), hasGrandPrixResult_op, individual))
    driver = URIRef(f"{ONTOLOGY_IRI}#driver_{driver_data['name'].replace(' ', '_').lower()}"
                    f"_{driver_data['surname'].replace(' ', '_').lower()}")
    f1_graph.add((driver, hasDriverGrandPrixResult_op, individual))
    f1_graph.add((individual, grandPrixResultIsRelatedTo_op, driver))
    return individual


def add_qualifying_result_individual(individual_id, result_data, grand_prix_name, driver_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, qualifying_result_class))
    if "number" in result_data and result_data["number"].strip():
        f1_graph.add((individual, driverNumber_dp, Literal(result_data["number"], datatype=XSD.nonNegativeInteger)))
    f1_graph.add((individual, driverPosition_dp, Literal(result_data["position"], datatype=XSD.positiveInteger)))
    if "Q1" in result_data and result_data["Q1"].strip():
        f1_graph.add((individual, Q1Time_dp, Literal(result_data["Q1"], datatype=XSD.string)))
    if "Q2" in result_data and result_data["Q2"].strip():
        f1_graph.add((individual, Q2Time_dp, Literal(result_data["Q2"], datatype=XSD.string)))
    if "Q3" in result_data and result_data["Q3"].strip():
        f1_graph.add((individual, Q3Time_dp, Literal(result_data["Q3"], datatype=XSD.string)))
    f1_graph.add((URIRef(f"{ONTOLOGY_IRI}#grand_prix_{grand_prix_name}"), hasGrandPrixResult_op, individual))
    driver = URIRef(f"{ONTOLOGY_IRI}#driver_{driver_data['name'].replace(' ', '_').lower()}"
                    f"_{driver_data['surname'].replace(' ', '_').lower()}")
    f1_graph.add((driver, hasDriverGrandPrixResult_op, individual))
    f1_graph.add((individual, grandPrixResultIsRelatedTo_op, driver))
    return individual


def add_movie_individual(individual_id, movie_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, movie_class))
    f1_graph.add((individual, creationTitle_dp, Literal(movie_data["title"], datatype=XSD.string)))
    if "date" in movie_data and movie_data["date"] is not None and movie_data["date"].strip():
        f1_graph.add((individual, creationDate_dp,
                      Literal(datetime.datetime.strptime(movie_data["date"], "%Y").strftime("%Y"), datatype=XSD.date)))
    if "genres" in movie_data and movie_data["genres"] is not None and movie_data["genres"].strip():
        f1_graph.add((individual, genre_dp, Literal(movie_data["genres"], datatype=XSD.string)))
    if "description" in movie_data and movie_data["description"] is not None and movie_data["description"].strip():
        f1_graph.add((individual, description_dp, Literal(movie_data["description"], datatype=XSD.string)))
    if "imDbRatingVotes" in movie_data and movie_data["imDbRatingVotes"] is not None and movie_data["imDbRatingVotes"].strip():
        f1_graph.add((individual, ratingsNum_dp, Literal(movie_data["imDbRatingVotes"], datatype=XSD.nonNegativeInteger)))
    if "imDbRating" in movie_data and movie_data["imDbRating"] is not None and movie_data["imDbRating"].strip():
        f1_graph.add((individual, imDbRating_dp, Literal(movie_data["imDbRating"], datatype=XSD.double)))
    if "metacriticRating" in movie_data and movie_data["metacriticRating"] is not None and movie_data["metacriticRating"].strip():
        f1_graph.add((individual, metacriticRating_dp, Literal(movie_data["metacriticRating"], datatype=XSD.nonNegativeInteger)))
    if "runtime" in movie_data and movie_data["runtime"] is not None and movie_data["runtime"].strip():
        f1_graph.add((individual, movieDuration_dp, Literal(movie_data["runtime"], datatype=XSD.string)))
    if "drivers" in movie_data["isAbout"]:
        for driver in movie_data["isAbout"]["drivers"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#driver_{driver.replace(' ', '_').lower()}")))
    if "seasons" in movie_data["isAbout"]:
        for season in movie_data["isAbout"]["seasons"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#season_{season}")))
    if "teams" in movie_data["isAbout"]:
        for team in movie_data["isAbout"]["teams"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#team_{team.replace(' ', '_').lower()}")))
    if "cars" in movie_data["isAbout"]:
        for car in movie_data["isAbout"]["cars"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#car_{car.replace(' ', '_').lower()}")))
    if "grand_prixes" in movie_data["isAbout"]:
        for grand_prix in movie_data["isAbout"]["grand_prixes"]:
            try:
                f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#grand_prix"
                                                             f"_{movie_data['isAbout']['seasons'][-1]}"
                                                             f"_{grand_prix.replace(' ', '_').lower()}")))
            except KeyError:
                continue
    return individual


def add_book_individual(individual_id, book_data):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")
    f1_graph.add((individual, RDF.type, book_class))
    f1_graph.add((individual, creationTitle_dp, Literal(book_data["title"], datatype=XSD.string)))
    if "date" in book_data and book_data["date"] is not None and book_data["date"].strip():
        f1_graph.add((individual, creationDate_dp,
                      Literal(datetime.datetime.strptime(book_data["date"], "%d.%m.%Y").strftime("%Y-%m-%d"),
                              datatype=XSD.date)))
    if "genres" in book_data and book_data["genres"] is not None and len(book_data["genres"]) > 0:
        f1_graph.add((individual, genre_dp, Literal(', '.join(genre for genre in book_data["genres"]), datatype=XSD.string)))
    if "description" in book_data and book_data["description"] is not None and book_data["description"].strip():
        f1_graph.add((individual, description_dp, Literal(book_data["description"], datatype=XSD.string)))
    if "ratings_num" in book_data and book_data["ratings_num"] is not None:
        f1_graph.add((individual, ratingsNum_dp, Literal(book_data["ratings_num"], datatype=XSD.nonNegativeInteger)))
    if "reviews_num" in book_data and book_data["reviews_num"] is not None:
        f1_graph.add((individual, reviewsNum_dp, Literal(book_data["reviews_num"], datatype=XSD.nonNegativeInteger)))
    if "number_of_pages" in book_data and book_data["number_of_pages"] is not None and book_data["number_of_pages"].strip():
        f1_graph.add((individual, pages_dp, Literal(book_data["number_of_pages"], datatype=XSD.nonNegativeInteger)))
    if "author" in book_data and book_data["author"] is not None and book_data["author"].strip():
        f1_graph.add((individual, author_dp, Literal(book_data["author"], datatype=XSD.string)))
    if "rating" in book_data and book_data["rating"] is not None and book_data["rating"].strip():
        f1_graph.add((individual, goodreadsRating_dp, Literal(book_data["rating"], datatype=XSD.double)))

    description = book_data["description"] if book_data["description"] is not None else None

    if "drivers" in book_data["isAbout"]:
        for driver in book_data["isAbout"]["drivers"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#driver_{driver.replace(' ', '_').lower()}")))
    if "seasons" in book_data["isAbout"]:
        for season in book_data["isAbout"]["seasons"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#season_{season}")))
    if "teams" in book_data["isAbout"]:
        for team in book_data["isAbout"]["teams"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#team_{team.replace(' ', '_').lower()}")))
    if "cars" in book_data["isAbout"]:
        for car in book_data["isAbout"]["cars"]:
            f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#car_{car.replace(' ', '_').lower()}")))
    if "grand_prixes" in book_data["isAbout"] and "seasons" in book_data["isAbout"]:
        for grand_prix in book_data["isAbout"]["grand_prixes"]:
            if len(book_data["isAbout"]["seasons"]) == 1:
                f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#grand_prix"
                                                             f"_{book_data['isAbout']['seasons'][0]}"
                                                             f"_{grand_prix.replace(' ', '_').lower()}")))
            else:
                for season in book_data["isAbout"]["seasons"]:
                    if f'{season} {grand_prix}' in description or f'{grand_prix} in {season}' in description or\
                            f'{grand_prix} {season}' in description:
                        f1_graph.add((individual, isAbout_op, URIRef(f"{ONTOLOGY_IRI}#grand_prix"
                                                                     f"_{season}"
                                                                     f"_{grand_prix.replace(' ', '_').lower()}")))
    return individual


def fill_f1_graph(ontology_path, data_format, f1_data_path, result_path):
    f1_graph.parse(ontology_path, format=data_format)

    drivers_data_dict = load_json_from_file(f'{f1_data_path}/ergast-drivers.json')
    for driver in drivers_data_dict:
        add_driver_individual(f"driver_{drivers_data_dict[driver]['name'].replace(' ', '_').lower()}_"
                              f"{drivers_data_dict[driver]['surname'].replace(' ', '_').lower()}",
                              drivers_data_dict[driver])

    teams_data_dict_ergast = load_json_from_file(f'{f1_data_path}/ergast-constructors.json')
    teams_data_dict_technical = load_json_from_file(f'{f1_data_path}/f1-technical-teams.json')
    for team in teams_data_dict_ergast:
        f1_technical_match_team = next(iter([key for key, value in teams_data_dict_technical.items()
                                   if teams_data_dict_ergast[team]["name"].replace(' ', '_').lower() in key.lower()]), None)

        if f1_technical_match_team is not None:
            team_key = teams_data_dict_technical[f1_technical_match_team]
        else:
            team_key = None

        add_team_individual(f"team_{teams_data_dict_ergast[team]['name'].replace(' ', '_').lower()}",
                            teams_data_dict_ergast[team], team_key)

    cars_data_dict = load_json_from_file(f'{f1_data_path}/f1-technical-cars.json')
    for car in cars_data_dict:
        add_car_individual(f"car_{cars_data_dict[car]['model'].replace(' ', '_').replace('(', '').replace(')', '').lower()}",
                           cars_data_dict[car], teams_data_dict_ergast)

    seasons_data_dict = load_json_from_file(f'{f1_data_path}/ergast-seasons.json')
    for season in seasons_data_dict:
        add_season_individual(f"season_{seasons_data_dict[season]['year']}",
                              int(seasons_data_dict[season]['year']), seasons_data_dict[season]['wikipedia_page_url'])

    team_participation_data_dict = load_json_from_file(f'{f1_data_path}/f1-fansite-team-participations.json')
    for season in team_participation_data_dict:
        season_participations = team_participation_data_dict[season]
        for participation in season_participations:
            if int(season) <= 2013:
                add_team_participation_individual(f"team_participation_{season}_{participation['driver'].replace(' ', '_').replace('(has_contract)', '').replace('(confirmed)', '').lower()}"
                                                  f"_{participation['team'].replace(' ', '_').lower()}", season, participation)
            else:
                add_team_participation_individual(
                    f"team_participation_{season}_{participation['drivers'][0]['driver'].replace(' ', '_').replace('(has_contract)', '').replace('(confirmed)', '').lower()}"
                    f"_{participation['team'].replace(' ', '_').lower()}", season,
                    {"driver": participation['drivers'][0]['driver'], "team": participation['team']})
                add_team_participation_individual(
                    f"team_participation_{season}_{participation['drivers'][1]['driver'].replace(' ', '_').replace('(has_contract)', '').replace('(confirmed)', '').lower()}"
                    f"_{participation['team'].replace(' ', '_').lower()}", season,
                    {"driver": participation['drivers'][1]['driver'], "team": participation['team']})

    # car driving
    for car in cars_data_dict:
        if "years" in cars_data_dict[car]:
            for year in cars_data_dict[car]["years"]:
                if "drivers" in cars_data_dict[car]:
                    for driver in re.split('[,/]', re.sub(r'\([^)]*\)', '', cars_data_dict[car]["drivers"])):
                        driver_name = re.sub(r'\([^)]*\)', '', driver).strip().lower().replace(' ', '_')
                        add_car_driving_individual(f"car_driving_{year}_{driver_name}_"
                                                   f"{cars_data_dict[car]['model'].replace(' ', '_').replace('(', '').replace(')', '').lower()}",
                                                   year, cars_data_dict[car], driver_name)

    driver_standings_data_dict = load_json_from_file(f'{f1_data_path}/ergast-driver-standings.json')
    for season_year in driver_standings_data_dict:
        for standing in driver_standings_data_dict[season_year]:
            year = season_year.split("_")[0]
            driver = drivers_data_dict[standing["ergast_driver_id"]]
            add_driver_standing_individual(f"driver_standing_{year}_{driver['name'].replace(' ', '_').lower()}"
                                           f"_{driver['surname'].replace(' ', '_').lower()}", year, standing, driver)

    constructor_standings_data_dict = load_json_from_file(f'{f1_data_path}/ergast-constructor-standings.json')
    for season_year in constructor_standings_data_dict:
        for standing in constructor_standings_data_dict[season_year]:
            year = season_year.split("_")[0]
            team = teams_data_dict_ergast[standing["ergast_constructor_id"]]
            add_constructor_standing_individual(f"constructor_standing_{year}_{team['name'].replace(' ', '_').lower()}",
                                                year, standing, team)

    circuits_data_dict_ergast = load_json_from_file(f'{f1_data_path}/ergast-circuits.json')
    circuits_data_dict_fansite = load_json_from_file(f'{f1_data_path}/f1-fansite-circuit.json')
    for circuit in circuits_data_dict_ergast:
        fansite_matching_circuit = next(iter([key for key, value in circuits_data_dict_fansite.items() if circuit in key]), None)
        if fansite_matching_circuit is not None:
            fansite_data = circuits_data_dict_fansite[fansite_matching_circuit]
        else:
            fansite_data = None
        add_circuit_individual(f"circuit_{circuit.replace(' ', '_').lower()}",
                               circuits_data_dict_ergast[circuit], fansite_data)

    grand_prix_data_dict_ergast = load_json_from_file(f'{f1_data_path}/ergast-races.json')
    grand_prix_data_dict_fansite = load_json_from_file(f'{f1_data_path}/f1-fansite-grand-prix.json')
    for grand_prix in grand_prix_data_dict_ergast:
        fansite_matching_grand_prix = next(iter([key for key, value in grand_prix_data_dict_fansite.items()
                                                 if key in grand_prix]), None)
        if fansite_matching_grand_prix is not None:
            fansite_data = grand_prix_data_dict_fansite[fansite_matching_grand_prix]
        else:
            fansite_data = None
        add_grand_prix_individual(f"grand_prix_{grand_prix}", grand_prix_data_dict_ergast[grand_prix], fansite_data)

    death_accidents_data_dict = load_json_from_file(f'{f1_data_path}/f1-fansite-deaths.json')
    for death in death_accidents_data_dict:
        add_death_accident_individual(f"death_accident_{death_accidents_data_dict[death]['driver'].replace(' ', '_').lower()}",
                                      death_accidents_data_dict[death])

    race_results_data_dict = load_json_from_file(f'{f1_data_path}/ergast-results.json')
    for grand_prix_results_key in race_results_data_dict:
        for race_result in race_results_data_dict[grand_prix_results_key]:
            add_race_result_individual(f"race_result_{grand_prix_results_key}_{race_result['ergast_driver_id']}",
                                       race_result, grand_prix_results_key, drivers_data_dict[race_result['ergast_driver_id']])

    qualifying_results_data_dict = load_json_from_file(f'{f1_data_path}/ergast-qualifying.json')
    for grand_prix_results_key in qualifying_results_data_dict:
        for qualifying_result in qualifying_results_data_dict[grand_prix_results_key]:
            add_qualifying_result_individual(f"qualifying_result_{grand_prix_results_key}_{qualifying_result['ergast_driver_id']}",
                                             qualifying_result, grand_prix_results_key,
                                             drivers_data_dict[qualifying_result['ergast_driver_id']])

    movies_data = load_json_from_file(f'{f1_data_path}/f1-movies.json')
    for movie in movies_data:
        add_movie_individual(f"movie_{movie['title'].replace(' ', '_').replace('(', '').replace(')', '').lower()}", movie)

    books_data = load_json_from_file(f'{f1_data_path}/f1-books.json')
    for book in books_data:
        add_book_individual(f"book_{book['title'].replace(' ', '_').replace('(', '').replace(')', '').lower()}", book)

    f1_graph.serialize(destination=result_path, format=data_format)

