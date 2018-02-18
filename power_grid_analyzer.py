from csv import DictReader, DictWriter

import networkx as nx


def create_graph(cities, power_lines):
    G = nx.Graph()
    for city in cities:
        G.add_node(city['city'], area=city['area'])

    for line in power_lines:
        G.add_edge(line['from'], line['to'], weight=int(line['weight']))

    return G


def import_cities(areas):
    """
    :param areas:  a list of areas from which to import cities. For example ['brown', 'red', 'purple']
    :return: dictionary of cities
    """
    with open('data/cities.csv') as source:
        reader = DictReader(source)
        result = [row for row in reader if row['area'] in areas]
    return result


def import_power_lines(cities):
    """
    :param cities: a dictionary of cities with their ares. Example: {'city:'seattle', 'area':'purple'}
    :return:
    """
    city_names = [city['city'] for city in cities]
    with open('data/connections.csv') as source:
        reader = DictReader(source)
        result = [row for row in reader if row['from'] in city_names and row['to'] in city_names]
    return result


def get_cities_to_areas_dict(cities=None):
    cities_to_areas = dict()
    for city in cities:
        cities_to_areas[city['city']] = city['area']
    return cities_to_areas


def create_k_MST_like_graph(G, starting_city: dict, k: int):
    """

    :param G: the complete graph
    :param starting_city: the city from which the player starts
    :param k: the number of cities the subgraph has to have before stopping
    :return: a dictionary containing the results
    """

    # initialise our list of cities and power lines and add the starting city to the list of cities
    power_lines = list()
    connected_cities = list()
    connected_cities.append(starting_city['city'])

    # loop here until we have enough cities
    while len(connected_cities) < k:

        # initialize our minimal_cost variable with something ridiculously high
        # this way it's guaranteed that at least one edge will be cheaper than this
        minimal_cost = 1000
        cheapest_line = None

        # loop through all the connected cities
        for city in connected_cities:
            # loop through all the power lines connected to this city
            for city_a, city_b in nx.edges(G, city):

                # if the cities at both end of the power line are part of our network
                # skip this power line and continue with the next one
                if city_a in connected_cities and city_b in connected_cities:
                    continue

                power_line_cost = G[city_a][city_b]['weight']

                # if the cost of the power line is under our minimal cost,
                # it's a candidate to be the cheapest connection
                if power_line_cost < minimal_cost:
                    minimal_cost = power_line_cost
                    cheapest_line = (city_a, city_b, power_line_cost)

        # when we have looked at ALL the power lines connected to ALL the cities in our current network
        # we have found the cheapest outgoing power line
        power_lines.append(cheapest_line)

        # one of the cities will be already in our list of cities, the other will be just outside it
        # add the one outside to our list of connected cities
        if cheapest_line[0] not in connected_cities:
            connected_cities.append(cheapest_line[0])
        if cheapest_line[1] not in connected_cities:
            connected_cities.append(cheapest_line[1])

    # when the loop terminates, we have the right amount of cities
    # next we can calculate the cost and return our results
    route_cost = sum([e[2] for e in power_lines])
    return {'city': starting_city['city'], 'area': starting_city['area'], 'connected_cities': connected_cities,
            'cost': route_cost}


def analyse(areas: [str], k: int):
    # get the cities and the areas
    imported_cities = import_cities(areas)
    imported_power_lines = import_power_lines(imported_cities)

    # get a dictionary mapping city names to the area where they are
    # we'll need this later
    cities_to_areas = get_cities_to_areas_dict(imported_cities)

    G = create_graph(imported_cities, imported_power_lines)
    analysis_result = []

    for city in imported_cities:
        result = create_k_MST_like_graph(G, city, k=k)

        # calculate how many of these cities area in the starting area
        cities_in_starting_area = len(
            [city for city in result['connected_cities'] if cities_to_areas[city] == city['area']])

        result['cities_in_starting_area'] = cities_in_starting_area
        analysis_result.append(result)

    save_results(analysis_result, areas, k)


def save_results(analysis_result, areas, k):
    with open(f'{len(areas)}_areas_and_network_size_{k}.csv', 'w') as csvfile:
        fieldnames = ['city', 'area', 'cost', 'cities_in_starting_area', 'connected_cities']
        csv_writer = DictWriter(fieldnames=fieldnames, f=csvfile)
        csv_writer.writeheader()
        for r in analysis_result:
            csv_writer.writerow(r)


if __name__ == '__main__':
    areas_to_analyse = ['purple', 'gray', 'red', 'yellow', 'brown']
    size_of_network = 14
    analyse(areas=areas_to_analyse, k=size_of_network)
