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
import sqlite3



class DataCrawler:
    def __init__(self):
        self.username = "fixisib161@xhyemail.com"
        self.password = "mnbvcxz123"
        self.loginURL = "https://www.rightmove.co.uk/login.html?from=%2F&hideFromParameterOnRegisterURI=true"
        self.API_KEY = "9d0836c76aa45f9407ed8fe446cc0d94"
        self.proxy={}
        

    def do_login(self, username, password):
        global driver, timeout
        timeout= 7
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
        driver.get(self.loginURL)
        driver.maximize_window()
        try:
            u = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID,"email")))
            u.send_keys(username)
            driver.find_element_by_id("password").send_keys(password)
            driver.find_element_by_css_selector("button.mrm-button").click()
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a#my-rightmove")))
            print("logged in successfully")
            return True
        except Exception:
            print("Login error")
            return False
    
    def insert_data(self, username, password ,location, minPrice, maxPrice, status, fail_msg):
        global conn
        conn = sqlite3.connect('job_logs.db')
        conn.execute('''CREATE TABLE if not exists job_status 
                (ID INTEGER PRIMARY KEY    AUTOINCREMENT,
                username           CHAR(50),
                password            CHAR(50),
                status        CHAR(50),
                fail            CHAR(50),
                location         CHAR(50),
                min_price            CHAR(50),
                max_price     CHAR(50) );''')
        print("table created successfully")
        conn.execute("INSERT INTO job_status (username, password, status, fail, location, min_price, max_price) VALUES ( '"+username+"', '"+password+"', '"+status+"', '"+fail_msg+"', '"+location+"', '"+minPrice+"', '"+maxPrice+"')")
        conn.commit()
        print("data inserted successfully...")

    def update_data(self, status, username, location, minprice, maxprice):
        conn.execute("UPDATE job_status SET  status = '"+status+"' where username = '"+username+"' and location='"+location+"' and min_price='"+minprice+"' and max_price='"+maxprice+"'")
        conn.commit()
    
    def update_unsuccess_msg(self, fail_msg, username, location, minprice, maxprice):
        conn.execute("UPDATE job_status SET  fail = '"+fail_msg+"' where username = '"+username+"' and location='"+location+"' and min_price='"+minprice+"' and max_price='"+maxprice+"'")
        conn.commit()

    def property_search(self, location, minPrice, maxPrice):
        print("Adding Search criteria...")
        try:
            loc_feild = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#searchLocation")))
            loc_feild.send_keys(location)
            loc_feild.send_keys(Keys.ENTER)
            min_price = driver.find_element_by_css_selector("select#minPrice")
            min_price.click()
            option = min_price.find_elements_by_tag_name("option")
            for x in option:
                if minPrice in x.get_attribute("value"):
                    x.click()
                    break
            max_price = driver.find_element_by_css_selector("select#maxPrice")
            max_price.click()
            option = max_price.find_elements_by_tag_name("option")
            for x in option:
                if maxPrice in x.get_attribute("value"):
                    x.click()
                    break
            loc_feild = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"button#submit")))
            loc_feild.click()
            print("Criteria added successfully....")
            status = True
        except Exception as ex:
            print("error while adding criteria",ex)
            status = False

        return status
    
    def solve_captcha(self, _dr, _sitekey, _input_field):
        _unresolved = True
        c_not_ready = 1
        while _unresolved:
            _session = requests.Session()
            _captcha_id = _session.post(f"http://2captcha.com/in.php?key={self.API_KEY}&method=userrecaptcha&lang=zh&googlekey={_sitekey}&pageurl={_dr.current_url}",proxies=self.proxy).text
            _captcha_id = _captcha_id.split('|')[1]
            time.sleep(15)
            _recaptcha_answer = _session.get(f"http://2captcha.com/res.php?key={self.API_KEY}&action=get&id={_captcha_id}",proxies=self.proxy).text

            while 'CAPCHA_NOT_READY' in _recaptcha_answer:
                print("CAPCHA_NOT_READY", c_not_ready)
                try:
                    time.sleep(5)
                    if c_not_ready==13:
                        print("captcha not resolved in 13 attempts")
                        return False
                    _recaptcha_answer = _session.get(f"http://2captcha.com/res.php?key={self.API_KEY}&action=get&id={_captcha_id}",proxies=self.proxy).text
                    c_not_ready = c_not_ready + 1
                except Exception as e:
                    c_not_ready = c_not_ready + 1
                    print(e)
                    _recaptcha_answer = 'CAPCHA_NOT_READY'
                    

            if 'ERROR' in _recaptcha_answer:
                print('2captcha unsucceded in solving...')
                return False
            _answer = _recaptcha_answer.split('|')[1]
            # _response = _input_field
            try:
                _dr.execute_script("document.getElementsByClassName('g-recaptcha-response')[0].value = '"+_answer+"'")
                _dr.execute_script("onCaptchaSubmit();")
                _unresolved = False
            except Exception as _error:
                print(_error)
        return True

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

    def get_agents(self):
        agents_link = []
        try:
            while True:
                list_results = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"a.propertyCard-contacItem--email")))
                for x in list_results:
                    agents_link.append(x.get_attribute("href"))
                nxt = driver.find_element_by_css_selector("button.pagination-direction--next")
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", nxt)
                nxt.click()
                time.sleep(2)
                next_page = driver.find_elements_by_css_selector("div.pagination-controls--disabled")
                if next_page:
                    if "Next" in next_page[0].text:
                        raise Exception
                print("Agents found yet::",len(agents_link))
        except Exception as ex:
            pass
        return agents_link

    def send_msg_to_agent(self, agent_link, message):
        captcha_status = False
        msg_status = False
        c=1
        while not captcha_status and c<=2:
            driver.get(agent_link)
            msg_status = ''
            try:
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#pageheader")))
                msg = driver.find_element_by_css_selector("textarea#comments")
                msg.send_keys(message)
                msg = driver.find_element_by_css_selector("input#telephone")
                msg.send_keys("21225458525")
                msg = driver.find_element_by_css_selector("input#postcode")
                msg.send_keys("MK6 1AJ")
                sell_type = driver.find_element_by_css_selector("select#emailAnswerSellSituationType")
                options = sell_type.find_elements_by_tag_name("option")
                if options:options[1].click()

                sell_type = driver.find_element_by_css_selector("select#emailAnswerRentSituationType")
                options = sell_type.find_elements_by_tag_name("option")
                if options:options[1].click()

                captcha = driver.find_element_by_css_selector("div.g-recaptcha")
                if driver.find_elements_by_name("g-recaptcha-response"):
                    sitekey = re.findall(r'sitekey=\"([a-zA-Z0-9-_]*)\"', driver.page_source)
                    if sitekey:
                        sitekey = sitekey[0]
                        responsefield = driver.find_element_by_name("g-recaptcha-response")
                        print("Resolving Captcha...")
                        captcha_status = self.solve_captcha(driver, sitekey, responsefield)
                        if not captcha_status:
                            c+=1
                            print("Captche fail..retry",c)
                            continue
                        print("Captcha Resolved successfully..")
                        submit = driver.find_element_by_css_selector("input.touchcontactagent-button-submit")
                        submit.click()
                        WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#lvaEmailSentConfirmation")))
                        print("Msg sent successfully")
                        msg_status = True
            except Exception as ex:
                print("error msg not sent   ", ex)
                msg_status = False
                break
                
        return msg_status

    def main(self, input_data):
        import pdb; pdb.set_trace()
        for x in input_data:
            # location = x['location']
            # minPrice = x['minPrice']
            # maxPrice = x['maxPrice']
            # message = x['message']
            # username = x['username']
            # password = x['password']
            # self.insert_data(username, password ,location, minPrice, maxPrice, "Starting process","0")
            login = self.do_login("fixisib161@xhyemail.com", "mnbvcxz123")
            if login:
                status = self.property_search("london","50000","60000")
                # status = self.property_search(location, minPrice, maxPrice)
                if status:
                    # self.update_data('Getting properties...', username, location, minPrice, maxPrice)
                    all_agents = self.get_agents()
                    if all_agents:
                        # self.update_data('Total properties found '+str(len(all_agents)), username, location, minPrice, maxPrice)
                        print ('Total properties found '+str(len(all_agents)))
                        msg_fail = 1
                        for index, link in enumerate(all_agents):
                            msg_status = self.send_msg_to_agent(link, "more details")
                            if msg_status:
                                # self.update_data(str(index+1)+" of "+str(len(all_agents))+" messages sent", username, location, minPrice, maxPrice)
                                print (str(index+1)+" of "+str(len(all_agents))+" messages sent")
                            else:
                                self.update_unsuccess_msg("unsuccessfull messages is "+str(msg_fail), username, location, minPrice, maxPrice)
                                msg_fail = msg_fail + 1
                        driver.close()
                        print ('done')
                        # yield 'done'
                else:
                    driver.close()
                    self.update_data("error while adding criteria retry..", username, location, minPrice, maxPrice)
                    print("error while adding criteria retry..")
            else:
                driver.close()
                self.update_data("error in login retry..", username, location, minPrice, maxPrice)
                print("error in login retry..")

if __name__ == "__main__":
    arr= [{"daata":""}]
    DataCrawler().main(arr)