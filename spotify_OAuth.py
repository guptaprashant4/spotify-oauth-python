"""
This python file can be used to authenticate with spotify Web API
It supports all the authentication types mentioned in the Spotify Web API documentation

Note: Redirect URL passed within any class has to be same and also need to be in the 
    spotify developers app portal
"""

from selenium import webdriver
from random import randint
from hashlib import sha256
import requests
import time
import base64


class AuthCodeFlow:

    def __init__(self, id: str, secret: str):
        """
        The AuthCodeFlow class uses spotify's authorization code flow to authenticate a
        user.

        To initiate this code flow cliend id and secret generated from spotify website has 
        to be passed to the class.

        After the class is initiated various functions can be used to obtain authorization
        code or access token.
        """

        self.client_id = id
        self.client_secret = secret

    def user_auth(self, redirect_url: str, scope: str ="", **kwargs): 
        """
        This method can be used to accquire a authentication code that can be later used to
        get an access token.

        This method returns a json with the authorization code and state (if used).

        **kwargs can be provided with accordance to spotify Web API documentation if any additional
        parameters need to be provided(optional).

        Note: After approving the request the browser window closes automatically and the output is
        returned in the program.
        """

        auth_endpoint = "https://accounts.spotify.com/authorize"
        parameters = {
            "client_id" : self.client_id,
            "response_type" : "code",
            "redirect_uri" : redirect_url,
            "scope" : scope,
        }

        # Add any extra arguments provided in the method to the parameters thats being passed in the request
        for (key, value) in kwargs.items():
            parameters[key] = value

        # Making an request to the authorize endpoint of Spotify to get user authorization
        response = requests.get(auth_endpoint, params=parameters)

        #Opening the request in Chrome browser to verify user then returning the callback url
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(options=options)

        driver.get(response.url)

        while redirect_url not in driver.current_url:
            time.sleep(1)

        # Fetch the callback url from the browser   
        acs_code = driver.current_url.split("?")[1].split("&")

        driver.quit()

        # Clean the callback url and return a json with returned values
        returned_response = {}
        for items in acs_code:
            key = items.split("=")[0]
            value = items.split("=")[1]
            returned_response[key] = value

        return returned_response
    
    def acs_token(self, redirect_url: str, auth_code:str = "", scope: str = "", refresh_token: str = ""):
        """
        This method can be used to accquire an access token using the Authorization Code Flow
        (if authorization code is passed to the auth_code is passed).

        This method can also be used to accquire access token using refresh token(if refresh token is
        passed to the refresh_token parameter).

        Warning: Only pass one of the parameters auth_code or refresh_token else the program will throw 
        an exception.
        """

        token_endpoint = "https://accounts.spotify.com/api/token"

        # Encode client id and client secret to base64
        auth_header = base64.urlsafe_b64encode((self.client_id + ':' + self.client_secret).encode('ascii'))
        head = {
                "Authorization" : 'Basic %s' % auth_header.decode('ascii'),
                "Content-Type" : "application/x-www-form-urlencoded",
            }

        # Determine whether to request a refresh access token or a new access token
        if auth_code and refresh_token:
            raise ValueError("Only one parameter is required: Passed two, auth_code and refresh_token")
        
        elif refresh_token:
            body = {
                "grant_type" : "refresh_token",
                "refresh_token" : refresh_token,
            }

            response = requests.post(token_endpoint, headers=head, data=body)       
                 
            return response.json()
        
        elif auth_code:
            body = {
                "grant_type" : "authorization_code",
                "code" : auth_code,
                "redirect_uri" : redirect_url,
            }

            response = requests.post(token_endpoint, headers=head, data=body)

            return response.json()
        
        

class ClientCredentials:

    def __init__(self, id: str, secret: str):
        """
        The ClientCredentials class uses the client credentials flow of Spotify Web API authentication.
        
        This is the most basic form of authentication and is not recommended for use on consumer based
        applications.

        To initiate this code flow client id and client secret generated from Spotify website has to be
        passed to the class.
        """

        self.client_id = id
        self.client_secret = secret

    def acs_token(self):
        """
        No argument is required to excute this method. All the necessary arguments are hardcoded in the method.

        The output is a json with a basic access token, its type and expiry(in seconds).
        """

        token_endpoint = "https://accounts.spotify.com/api/token"

        # Encode cliend id and secret to base64 url form
        auth_header = base64.urlsafe_b64encode((self.client_id + ':' + self.client_secret).encode('ascii'))
        head = {
            "Authorization" : "Basic %s" % auth_header.decode("ascii"),
            "Content-Type" : "application/x-www-form-urlencoded",
        }

        body = {
            "grant_type" : "client_credentials",
        }

        # Make a request to the Spotify API
        response = requests.post(token_endpoint, headers=head, params=body)
        acs_token = response.json()

        return acs_token


class ImplicitGrant:

    def __init__(self, id: str):
        """
        The ImplicitGrant class uses implicit grant code flow of Spotify Web API.

        Client Id obtained from Spotify website is required to innitiate this class.

        The implicit grant code flow can be used if storing client secret to environment
        variables is not possible or is risky.
        """

        self.client_id = id

    def acs_token(self, redirect_url: str, **kwargs):
        """
        The acs_token method acciqures access token from Spotify Web API.

        Only one argument is required to execute the acs_token method.

        **kwargs takes any other arguments that has to be passed to the request.

        Note: After approving the request the browser window closes automatically and the output is
        returned in the program.
        """

        token_endpoint = "https://accounts.spotify.com/authorize"
        body = {
            "client_id" : self.client_id,
            "response_type" : "token",
            "redirect_uri" : redirect_url,
        }

        for (key, value) in kwargs.items():
            body[key] = value

        # Make an request to the Spotify Web API for access token
        response = requests.get(token_endpoint, params=body)
        
        # Start chrome browser to authenticate user
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(options=options)

        driver.get(response.url)

        while redirect_url not in driver.current_url:
            time.sleep(1)

        # Fetch the callback URL from the browser    
        acs_code = driver.current_url.split("#")[1].split("&")

        driver.quit()

        # Clean the callback url and return a json with returned values
        returned_response = {}
        for items in acs_code:
            key = items.split("=")[0]
            value = items.split("=")[1]
            returned_response[key] = value

        return returned_response

class PKCEFlow:

    def __init__(self, id: str):
        """
        The PKCEFlow class uses Authorization with PKCE Extension code flow
        of authenticating with Spotify Web API.

        Client ID needs to be passed to the class to initiate PKCE code flow.

        After the class is initiated various functions can be used to obtain authorization
        code or access token.
        """
        self.client_id = id

    def gen_random_str(self, length: int):
        """
        The gen_random_str method generates a random string using alphabet
        characters, digits, tildes, periods, underscores and hyphens.

        To execute gen_random_str method the lenght of the string to be generated
        must be passed to the method as an integer.

        Note: The lenght of the string can only be between and including 43 to 128.
            This method is works same as Code Verifier referred to in the Spotify documentation.
        """

        possible_char = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789~._-"
        text = ""

        if length < 43 or length > 128:
            raise ValueError("The value of length should be between 43 and 128")

        else:
            is_code_short = True
            while is_code_short:
                if len(text) < length:
                    random_index = randint(0, len(possible_char) - 1)
                    text += possible_char[random_index]

                else:
                    is_code_short = False

            return text
        
    def hash_str(self, random_text: str):
        """
        The hash_str method takes a string of any lenght as an input and returns a Base64 encoded
        string which is hashed using the SHA256 algorithm.

        Note: This method is works same as Code Challenge referred to in the Spotify documentation.
        """
        encoder = random_text.encode()
        hashed_str = sha256(encoder).digest()
        b64_encoded_str = base64.urlsafe_b64encode(hashed_str)

        return b64_encoded_str.decode().rstrip("=")
        

    def usr_auth(self, redirect_url: str, hash_value, scope: str = "", state: str = ""):

        auth_endpoint = "https://accounts.spotify.com/authorize"
        body = {
            "client_id" : self.client_id,
            "response_type" : "code",
            "redirect_uri" : redirect_url,
            "state" : state,
            "scope" : scope,
            "code_challenge_method" : "S256",
            "code_challenge" : hash_value,
        }

        response = requests.get(auth_endpoint, params=body)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(options=options)

        driver.get(response.url)

        while redirect_url not in driver.current_url:
            time.sleep(1)
            
        acs_code = driver.current_url.split("?")[1].split("&")

        driver.quit()

        returned_response = {}
        for items in acs_code:
            key = items.split("=")[0]
            value = items.split("=")[1]
            returned_response[key] = value

        return returned_response
    
    def acs_token(self, code, redirect_url, random_text):

        token_endpoint = "https://accounts.spotify.com/api/token"
        head = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        body = {
            "grant_type" : "authorization_code",
            "redirect_uri" : redirect_url,
            "client_id" : self.client_id,
            "code_verifier" : random_text,
            "code" : code,
        }

        response = requests.post(token_endpoint, headers=head, params=body)

        print(response.text)