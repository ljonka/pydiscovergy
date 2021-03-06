import logging
from requests_oauthlib import OAuth1Session
import requests
import json
import sys
from models import Meter

TIMEOUT = 10
_LOGGER = logging.getLogger(__name__)


class PyDiscovergy:

    def __init__(self, app_name):
        """
        Initialize the Python Discovergy class.
        :param app_name: App name for OAuth process
        """

        self._app_name = app_name
        self._username = ""
        self._password = ""
        self._oauth_key = ""
        self._oauth_secret = ""

        self._discovergy_oauth = None

        self._base_url = "https://api.discovergy.com/public/v1"
        self._consumer_token_url = self._base_url + "/oauth1/consumer_token"
        self._request_token_url = self._base_url + "/oauth1/request_token"
        self._authorization_base_url = self._base_url + "/oauth1/authorize"
        self._access_token_url = self._base_url + "/oauth1/access_token"

    def _fetch_consumer_tokens(self):
        """Fetches consumer token for app name"""

        try:
            consumer_response = requests.post(self._consumer_token_url, data={"client": self._app_name}, headers={},
                                              timeout=TIMEOUT)
            consumer_tokens = json.loads(consumer_response.content.decode("utf-8"))
            self._oauth_key = consumer_tokens["key"]
            self._oauth_secret = consumer_tokens["secret"]
            return consumer_tokens

        except Exception as exception:
            _LOGGER.error("Exception: " + str(exception))
            return False

    def _fetch_request_token(self):
        """Fetch request token"""
        try:
            request_token_oauth = OAuth1Session(self._oauth_key, client_secret=self._oauth_secret,
                            callback_uri='oob')
            oauth_token_response = request_token_oauth.fetch_request_token(self._request_token_url)
            return {"token": oauth_token_response.get('oauth_token'), "token_secret":  oauth_token_response.get('oauth_token_secret')}

        except Exception as exception:
            _LOGGER.error("Exception: " + str(exception))
            return False

    def _authorize_request_token(self, email, password, resource_owner_key):
        """Authorize request token for account"""
        try:
            url = self._authorization_base_url + "?oauth_token=" + resource_owner_key + \
                  "&email=" + email + "&password=" + password
            response = requests.get(url, headers={}, timeout=TIMEOUT)
            if sys.version_info >= (3,0):
                from urllib.parse import parse_qs
                parsed_response = parse_qs(response.content.decode('utf-8'))
            else:
                from urlparse import parse_qs
                parsed_response = parse_qs(response.content.decode('utf-8'))

            verifier = parsed_response["oauth_verifier"][0]
            return verifier

        except Exception as exception:
            _LOGGER.error("Exception: " + str(exception))
            return False

    def _fetch_access_token(self, resource_owner_key, resource_owner_secret, verifier):
        """Fetch access token"""
        try:
            access_token_oauth = OAuth1Session(self._oauth_key,
                                               client_secret=self._oauth_secret,
                                               resource_owner_key=resource_owner_key,
                                               resource_owner_secret=resource_owner_secret,
                                               verifier=verifier)
            oauth_tokens = access_token_oauth.fetch_access_token(self._access_token_url)
            return {"token": oauth_tokens.get('oauth_token'),
                    "token_secret": oauth_tokens.get('oauth_token_secret')}

        except Exception as exception:
            _LOGGER.error("Exception: " + str(exception))
            return False

    def login(self, email, password):
        """
        Do the auth workflow

        :param str email: E-Mail address of the account
        :param str password: Password of the account
        :rtype bool:
        """

        try:
            self._fetch_consumer_tokens()

            request_tokens = self._fetch_request_token()
            resource_owner_key = request_tokens["token"]
            resource_owner_secret = request_tokens["token_secret"]

            verifier = self._authorize_request_token(email, password, resource_owner_key)

            access_token = self._fetch_access_token(resource_owner_key, resource_owner_secret, verifier)
            resource_owner_key = access_token["token"]
            resource_owner_secret = access_token["token_secret"]

            # Construct OAuth session with access token
            self._discovergy_oauth = OAuth1Session(self._oauth_key,
                                                   client_secret=self._oauth_secret,
                                                   resource_owner_key=resource_owner_key,
                                                   resource_owner_secret=resource_owner_secret)

        except requests.exceptions.HTTPError as exception_instance:
            _LOGGER.error("HTTPError: " + str(exception_instance))
            return False

        except Exception as exception_instance:
            _LOGGER.error("Exception: " + str(exception_instance))
            return False

        else:
            return True

    def get_meters(self):
        """
        Get smart meters
        :rtype: list[models.Meter]
        """

        try:
            response = self._discovergy_oauth.get(self._base_url + "/meters")
            if response:
                meters_response = json.loads(response.content.decode("utf-8"))
                meters = []
                for mr in meters_response:
                    meter = Meter(**mr)
                    meters.append(meter)
                return meters
            else:
                return []
        except Exception as exception_instance:
            _LOGGER.error("Exception: " + str(exception_instance))
            return []

    def get_fieldnames_for_meter(self, meter_id):
        """Get field names for meter id"""

        try:
            response = self._discovergy_oauth.get(self._base_url + "/field_names?meterId=" + str(meter_id))
            if response:
                return json.loads(response.content.decode("utf-8"))
            else:
                return False
        except Exception as exception_instance:
            _LOGGER.error("Exception: " + str(exception_instance))
            return False

    def get_devices_for_meter(self, meter_id):
        """Get devices by meter id"""

        try:
            response = self._discovergy_oauth.get(self._base_url + "/devices?meterId=" + str(meter_id))
            if response:
                return json.loads(response.content.decode("utf-8"))
            else:
                return False
        except Exception as exception_instance:
            _LOGGER.error("Exception: " + str(exception_instance))
            return False

    def get_last_reading(self, meter_id):
        """Get last reading for meter"""

        try:
            response = self._discovergy_oauth.get(self._base_url + "/last_reading?meterId=" + str(meter_id))
            if response:
                return json.loads(response.content.decode("utf-8"))
            else:
                return False
        except Exception as exception_instance:
            _LOGGER.error("Exception: " + str(exception_instance))
            return False
    def get_readings(self, meter_id, fields, from_timestamp, to_timestamp, resolution, disaggregation):
        """Get readings for meter"""

        try:
            response = self._discovergy_oauth.get(self._base_url + "/readings?meterId=" + str(meter_id) + "&from=" + int(from_timestamp))
            if response:
                return json.loads(response.content.decode("utf-8"))
            else:
                return False
        except Exception as exception_instance:
            _LOGGER.error("Exception: " + str(exception_instance))
            return False
