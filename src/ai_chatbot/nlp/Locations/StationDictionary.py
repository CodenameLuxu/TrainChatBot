from ai_chatbot.nlp.Locations.StationScraper import scrape_wiki_station


def station_dictionary_builder():
    stations = []

    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_A")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_B")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_C")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_D")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_E")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_F")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_G")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_H")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_I")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_J")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_K")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_L")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_M")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_N")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_O")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_P")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_Q")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_R")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_S")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_T")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_U")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_V")
    stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_W")
    # no stations starting with X exist
    # stations += scrape_wiki_station("https://en.wikipedia.org/wiki/UK_railway_stations_%E2%80%93_Y")
    # no stations starting with Z exist

    return stations
