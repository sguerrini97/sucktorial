import datetime
import logging
import os
import pickle
import sys
from typing import Optional

import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values


class Factorial:
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        # Check if both email and password are  (CLI usage)
        if (email and not password) or (password and not email):
            raise ValueError("Specify both email and password")

        # Load config from .env file
        self.config = dotenv_values()

        # If email and password are specified, override the config
        if (email and password):
            self.config["EMAIL"] = email
            self.config["PASSWORD"] = password
        # Check if email and password are correctly specified in the .env file
        elif not self.config.get("EMAIL") or not self.config.get("PASSWORD"):
            raise ValueError("Both email and password are required, fix your .env file")
        
        # Setup internal stuffs
        logging.basicConfig(
            # Set the logging level to DEBUG if --debug is specified in the CLI
            level=logging.DEBUG if "--debug" in sys.argv else logging.INFO,
            format="%(asctime)s | %(name)s | %(levelname)s - %(message)s",
        )
        # Create a logger for the current class with the name "factorial"
        self.logger = logging.getLogger("factorial")

        # Create a session for the requests
        self.session = requests.Session()
        # Load the session from the cookie file
        self.__load_session()

        self.logger.info("Factorial client initialized")

    def login(self):
        # TODO: Controllare se l'utente è già loggato
        authenticity_token = self.__get_authenticity_token()
        self.logger.debug(f"Authenticity token: {authenticity_token}")
        payload = {
            "authenticity_token": authenticity_token,
            "user[email]": self.config.get("EMAIL"),
            "user[password]": self.config.get("PASSWORD"),
            "user[remember_me]": 0,
            "commit": "Accedi",
        }
        self.logger.debug(f"Payload: {payload}")
        response = self.session.post(url=self.config.get("LOGIN_URL"), data=payload)
        if response.status_code != 200:
            self.logger.error(f"Can't login ({response.status_code})")
            self.logger.debug(response.text)
            raise ValueError("Can't login")
        self.logger.info("Login successful")
        self.__save_session()

        return True

    def logout(self):
        response = self.session.delete(url=self.config.get("SESSION_URL"))
        logout_correcty = response.status_code == 204
        self.logger.info("Logout successfully {}".format(logout_correcty))
        self.session = requests.Session()
        self.__delete_session()
        return logout_correcty

    def clock_in(self):
        # TODO: Controllare se e' gia' in clock in
        payload = {
            # {"now":"2023-07-10T00:10:58+02:00","source":"desktop"}
            "now": datetime.now().isoformat(),
            "source": "desktop",
        }
        response = self.session.post(url=self.config.get("CLOCK_IN_URL"), data=payload)
        if response.status_code not in {200, 201}:
            self.logger.error(f"Can't clock in ({response.status_code})")
            self.logger.debug(response.text)
            raise ValueError("Can't clock in")
        self.logger.info("Clock in successful at {}".format(datetime.now().isoformat()))
        return True

    def clock_out(self):
        # TODO: Controllare se e' gia' in clock out
        payload = {
            # {"now":"2023-07-10T00:10:58+02:00","source":"desktop"}
            "now": datetime.now().isoformat(),
            "source": "desktop",
        }
        response = self.session.post(url=self.config.get("CLOCK_OUT_URL"), data=payload)
        if response.status_code not in {200, 201}:
            self.logger.error(f"Can't clock in ({response.status_code})")
            self.logger.debug(response.text)
            raise ValueError("Can't clock in")
        self.logger.info("Clock in successful at {}".format(datetime.now().isoformat()))
        return True

    def is_clocked_in(self) -> bool:
        return len(self.open_shift()) == 0

    def open_shift(self) -> dict:
        response = self.session.get(url=self.config.get("OPEN_SHIFT_URL"))
        if response.status_code != 200:
            self.logger.error(f"Can't get open shift ({response.status_code})")
            self.logger.debug(response.text)
            raise ValueError("Can't get open shift")
        self.logger.info("Open shift successful")
        return response.json()

    def shifts(self):
        response = self.session.get(url=self.config.get("SHIFTS_URL"))
        if response.status_code != 200:
            self.logger.error(f"Can't get shifts ({response.status_code})")
            self.logger.debug(response.text)
            raise ValueError("Can't get shifts")
        self.logger.info("Shifts successful")
        return response.json()
    
    def delete_last_shift(self):
        shifts = self.shifts()
        if len(shifts) == 0:
            self.logger.warning("No shifts to delete")
            return False
        last_shift = shifts[-1]
        response = self.session.delete(url=self.config.get("SHIFTS_URL") + f"/{last_shift['id']}")
        if response.status_code != 204:
            self.logger.error(f"Can't delete shift ({response.status_code})")
            self.logger.debug(response.text)
            raise ValueError("Can't delete shift")
        self.logger.info("Shift deleted")
        return True

    def __save_session(self):
        with open(self.config.get("COOKIE_FILE"), "wb") as file:
            pickle.dump(self.session.cookies, file)
            self.logger.info("Sessions saved")
    
    def __load_session(self):
        if os.path.exists(self.config.get("COOKIE_FILE")):
            with open(self.config.get("COOKIE_FILE"), "rb") as file:
                self.session.cookies.update(pickle.load(file))
                self.logger.info("Sessions loaded")
                
    def __delete_session(self):
        if os.path.exists(self.config.get("COOKIE_FILE")):
            os.remove(self.config.get("COOKIE_FILE"))
            self.logger.info("Sessions deleted")

    def __get_authenticity_token(self):
        response = self.session.get(url=self.config.get("LOGIN_URL"))
        if response.status_code != 200:
            self.logger.error(f"Can't retrieve the login page ({response.status_code})")
            self.logger.debug(response.text)
            raise ValueError("Can't retrieve the login page")
        html_content = BeautifulSoup(response.text, "html.parser")
        auth_token = html_content.find("input", attrs={"name": "authenticity_token"}).get("value")
        if not auth_token:
            raise ValueError("Can't retrieve the authenticity token")
        return auth_token


if __name__ == "__main__":
    from time import sleep

    factorial = Factorial()
    print(factorial.config)
    factorial.login()
    sleep(3)
    factorial.clock_in()
    sleep(10)
    factorial.clock_out()
    sleep(3)
    factorial.logout()
