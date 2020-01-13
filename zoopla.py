import os
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json



class DataCrawler:
    def __init__(self):
        self.username = "bill.wpmlaw@solicltors.com"
        self.password = "monster1."
        self.loginURL = "https://www.zoopla.co.uk/signin/"
        self.do_login()

    def do_login(self):
        global driver, timeout
        timeout= 7
        driver = webdriver.Chrome("chromedriver.exe")
        driver.get(self.loginURL)
        driver.maximize_window()
        try:
            u = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID,"signin_email")))
            u.send_keys(self.username)
            driver.find_element_by_id("signin_password").send_keys(self.password)
            driver.find_element_by_id("signin_submit").click()
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"nav#main-nav")))
            print("logged in successfully")
        except Exception:
            print("Login error")

    def property_search(self, location, minPrice, maxPrice):
        driver.get("https://www.zoopla.co.uk/for-sale/")
        print("Adding Search criteria...")
        try:
            loc_feild = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#search-input-location")))
            loc_feild.send_keys(location)
            min_price = driver.find_element_by_css_selector("select#forsale_price_min")
            min_price.click()
            option = min_price.find_elements_by_tag_name("option")
            for x in option:
                if minPrice in x.get_attribute("value"):
                    x.click()
                    break
            max_price = driver.find_element_by_css_selector("select#forsale_price_max")
            max_price.click()
            option = max_price.find_elements_by_tag_name("option")
            for x in option:
                if maxPrice in x.get_attribute("value"):
                    x.click()
                    break
            btn = driver.find_element_by_css_selector("button#search-submit")
            btn.click()
            print("Criteria added successfully....")
            status = True
        except Exception as ex:
            print("error while adding criteria",ex)
            status = False

        return status

    def get_all_properties(self):
        agents_link = []
        driver.get(driver.current_url+"&page_size=100")
        try:
            time.sleep(1)
            pagination = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.paginate.bg-muted")))
            pages = pagination.find_elements_by_tag_name("a")
            if pages:
                try: 
                    last_page = int(pages[-1].text)
                except Exception:
                    last_page = int(pages[-2].text)
                
        except:
            last_page = 1
        print("Total pages ",last_page)

        for i in range(1,last_page+1):
            if "pn" not in driver.current_url:
                driver.get(driver.current_url+"&pn="+str(i))
            else:
                url = driver.current_url.split("&pn=")
                driver.get(url[0]+"&pn="+str(i))

            try:
                list_results = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"ul.listing-results")))
                if list_results: 
                    items = list_results[-1].find_elements_by_tag_name("li")
                    for x in items:
                        try:
                            footer = x.find_element_by_css_selector("div.listing-results-footer")
                            footer_right = footer.find_element_by_css_selector("div.listing-results-right")
                            contact_icon = footer_right.find_element_by_css_selector("i.icon-mail")
                            get_link = contact_icon.find_element_by_xpath("..")
                            link = get_link.get_attribute("href")
                            agents_link.append(link)
                        except Exception:
                            pass
                print("Total Properties found yet: ",len(agents_link))
            except Exception:
                pass
        return agents_link

    def send_msg_to_agent(self, agent_link):
        driver.get(agent_link)
        pass

    def main(self, loc, min_price, max_price):
        status = self.property_search(loc, min_price, max_price)
        if status:
            all_agents = self.get_all_properties()
            if all_agents:
                for link in all_agents:
                    self.send_msg_to_agent(link)
        else:
            print("error in criteria retry..")

if __name__ == "__main__":
    DataCrawler().main("London","2100000","2200000")