import random
from abc import abstractmethod, ABCMeta

import requests

from grandpybot.chatbots.openmediawiki import OpenMediaWikiBot
from grandpybot.chatbots.openstreetmap import OpenStreetMapBot


class ChatBotFactory(metaclass=ABCMeta):
    """
    Abstract chat bot factory class
    """

    @abstractmethod
    def build(self):
        """
        Calls the build method of inherited classes
        """

    def get_object(self) -> any:
        """
        Returns the built chat bot item
        """
        return self.build()


class OpenStreetMapBotFactory(ChatBotFactory):
    """
    The OpenStreetMap chat bot factory
    """

    def __init__(self, search_term):
        """
        Initializes an OpenStreetMap chat bot with the user search term
        """
        self.search_term = search_term

    def build(self) -> OpenStreetMapBot:
        """
        Effectively builds the concrete OpenStreetMap chat bot object
        """
        osm_object = self.perform_search(self.search_term)

        display_name = osm_object["display_name"]
        latitude = osm_object["lat"]
        longitude = osm_object["lon"]

        return OpenStreetMapBot(display_name, latitude, longitude)

    @staticmethod
    def perform_search(search_term):
        """
        Performs an OpenStreetMap API call in order to fetch result from a search term
        """
        osm_response = requests.get("https://nominatim.openstreetmap.org/search?"
                                    f"q={search_term}&"
                                    "addressdetails=1&"
                                    "countrycodes=fr&"
                                    "limit=1&"
                                    "format=json")

        return osm_response.json()[0]


class OpenMediaWikiBotFactory(ChatBotFactory):
    """
    The OpenStreetMap chat bot factory
    """

    def __init__(self, latitude, longitude):
        """
        Initializes an OpenMediaWiki chat bot with the user search term
        """
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude

    def build(self) -> OpenMediaWikiBot:
        """
        Effectively builds the concrete OpenMediaWiki chat bot object
        """
        omw_object = self.perform_geo_search(self.latitude, self.longitude)

        page_ids = []
        if "query" in omw_object and "geosearch" in omw_object["query"]:
            for item in omw_object["query"]["geosearch"]:
                page_ids.append(item["pageid"])

        random_index = random.randint(0, len(page_ids) - 1)
        chosen_page_id = page_ids[random_index]

        omw_object = self.perform_query_search(chosen_page_id)

        intro = omw_object["query"]["pages"][str(chosen_page_id)]["extract"]

        return OpenMediaWikiBot(intro)

    @staticmethod
    def perform_geo_search(latitude, longitude):
        """
        Performs an OpenMediaWiki Geo Search API call in order to fetch result from a search term
        """
        omw_response = requests.get("https://fr.wikipedia.org/w/api.php?"
                                    "action=query&"
                                    "list=geosearch&"
                                    f"gscoord={latitude}|{longitude}&"
                                    "gsradius=10000&"  # 10 000 meters, so 10kms max around
                                    "gslimit=10&"  # 10 results max
                                    "format=json")

        return omw_response.json()

    @staticmethod
    def perform_query_search(chosen_page_id):
        """
        Performs an OpenMediaWiki Query Search API call in order to fetch result from a search term
        """
        omw_response = requests.get("https://fr.wikipedia.org/w/api.php?"
                                    "action=query&"
                                    "prop=extracts&"
                                    "exsentences=3&"
                                    f"pageids={chosen_page_id}&"
                                    "format=json")

        return omw_response.json()
