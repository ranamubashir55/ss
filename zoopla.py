import os
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, requests
import json, re



class DataCrawler:
    def __init__(self):
        self.username = "bill.wpmlaw@solicltors.com"
        self.password = "monster1."
        self.loginURL = "https://www.zoopla.co.uk/signin/"
        self.API_KEY = "5eb9fc97e70f710fa844f83854a867af"
        self.proxy={}
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
    
    def solve_captcha(self, _dr, _sitekey, _input_field):
        _unresolved = True
        while _unresolved:
            _session = requests.Session()
            _captcha_id = _session.post(f"http://2captcha.com/in.php?key={self.API_KEY}&method=userrecaptcha&lang=zh&googlekey={_sitekey}&pageurl={_dr.current_url}",proxies=self.proxy).text
            _captcha_id = _captcha_id.split('|')[1]
            time.sleep(20)
            _recaptcha_answer = _session.get(f"http://2captcha.com/res.php?key={self.API_KEY}&action=get&id={_captcha_id}",proxies=self.proxy).text

            while 'CAPCHA_NOT_READY' in _recaptcha_answer:
                try:
                    time.sleep(5)
                    _recaptcha_answer = _session.get(
                        f"http://2captcha.com/res.php?key={self.API_KEY}&action=get&id={_captcha_id}",
                        proxies=self.proxy).text
                except Exception as e:
                    print(e)
                    _recaptcha_answer = 'CAPCHA_NOT_READY'

            if 'ERROR' in _recaptcha_answer:
                print('2captcha unsucceded in solving...')
                return False
            _answer = _recaptcha_answer.split('|')[1]
            # _response = _input_field
            try:
                _dr.execute_script("document.getElementsByClassName('g-recaptcha-response')[0].value = '"+_answer+"'")
                _dr.execute_script("recaptchaSuccess();")
                _unresolved = False
            except Exception as _error:
                print(_error)
        return None

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

    def send_msg_to_agent(self, agent_link, message):
        driver.get(agent_link)
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"form#for-sale-lead-form")))
            msg = driver.find_element_by_css_selector("textarea#message")
            msg.send_keys(message)
            captcha = driver.find_element_by_css_selector("div.g-recaptcha")
            if driver.find_elements_by_name("g-recaptcha-response"):
                sitekey = re.findall(r'sitekey=\"([a-zA-Z0-9-_]*)\"', driver.page_source)
                if sitekey:
                    sitekey = sitekey[0]
                    responsefield = driver.find_element_by_name("g-recaptcha-response")
                    self.solve_captcha(driver, sitekey, responsefield)
                    submit = driver.find_element_by_css_selector("input.ui-button-primary")
                    submit.click()
                    WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.lf-confirmation-heading__email-sent")))
                    print("Msg sent successfully")
        except Exception as ex:
            print("error msg not sent   ", ex)

    def main(self, loc, min_price, max_price, message):
        status = self.property_search(loc, min_price, max_price)
        if status:
            all_agents = self.get_all_properties()
            if all_agents:
                import pdb; pdb.set_trace()
                for link in all_agents:
                    self.send_msg_to_agent(link, message)
        else:
            print("error in criteria retry..")

if __name__ == "__main__":
    DataCrawler().main("London","2100000","2200000", "details")