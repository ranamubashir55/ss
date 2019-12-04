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
from lxml import etree as xml
from urllib.parse import unquote
from bs4 import BeautifulSoup
import urllib.request
import httplib2
import requests
import json
from collections import OrderedDict
import csv, json


class DataCrawler:
    def __init__(self):
        self.login = "gofund@reborn.com"
        self.password = "ghostempire"
        self.loginURL = "https://app.snov.io/login?lang=en"
        self.do_login()
        self.list_name=''
        self.country = "United Arab Emirates"
        self.industry = "Airlines/Aviation"
        self.range = "G"

    def do_login(self):
        global driver, timeout
        timeout= 7
        driver = webdriver.Chrome("chromedriver.exe")
        driver.get(self.loginURL)
        driver.maximize_window()
        #driver.find_element_by_id("Email").clear()
        driver.find_element_by_id("email").send_keys(self.login)
        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_id("buttonFormLogin").click()
        driver.get("https://app.snov.io/company-profile-search")
        print("logged in successfully")

    def company_profile_search(self):
        while True:
            try:
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID,"company-block")))
                feilds = driver.find_elements_by_css_selector("span.select2-selection--single")
                if feilds:
                    feilds[0].click()
                    time.sleep(2)
                    cntry = driver.find_element_by_css_selector("input.select2-search__field")
                    ActionChains(driver).move_to_element(cntry).perform()
                    ActionChains(driver).send_keys(self.country).perform()
                    option = driver.find_elements_by_css_selector("li.select2-results__option")
                    time.sleep(1)
                    if option:option[0].click()
                    time.sleep(2)
                    feilds[1].click()
                    industry = driver.find_element_by_css_selector("input.select2-search__field")
                    ActionChains(driver).move_to_element(industry).perform()
                    ActionChains(driver).send_keys(self.industry).perform()
                    option = driver.find_elements_by_css_selector("li.select2-results__option")
                    time.sleep(1)
                    if option:option[0].click()
                    time.sleep(2)
                    feilds[2].click()
                    company_size = driver.find_element_by_css_selector("input.select2-search__field")
                    ActionChains(driver).move_to_element(company_size).perform()
                    ActionChains(driver).send_keys(self.range).perform()
                    option = driver.find_elements_by_css_selector("li.select2-results__option")
                    time.sleep(1)
                    if option:option[0].click()
                    driver.find_element_by_css_selector("button.btn-primary").click()
                    break
            except Exception as ex:
                print(ex)

    def get_all_compaines(self):
        companies= []
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"label.styled-checkbox")))
            all_comp = driver.find_elements_by_css_selector("div.table-flex__row")
            for x in all_comp:
                try:
                    table_cell = x.find_elements_by_css_selector("div.table-flex__cell")
                    get_tag = table_cell[1].find_element_by_css_selector("span.data-value.prospect")
                    element = get_tag.find_element_by_tag_name("a")
                    name = element.text
                    link = element.get_attribute("href")
                    companies.append({"company_name":name,"company_link":link})
                except:
                    pass

            print(f"Total companies found: {len(companies)}")
            return companies
        except Exception as ex:
            print(ex)

    def records_on_page(self):
        try:
            paging = driver.find_elements_by_css_selector("div.pagination")
            per_page = paging[-1].find_element_by_css_selector("div.pagination__per-page")
            pages = per_page.find_elements_by_tag_name("label")
            if pages:pages[-1].click()
            time.sleep(4)
        except Exception:
            pass

    def pagination(self, l_page=None):
        try:
            paging = driver.find_elements_by_css_selector("div.pagination")
            page = paging[-1].find_element_by_css_selector("div.pagination__links")
            active_page = page.find_element_by_css_selector("a.active")
            if not l_page:
                last_page = page.find_element_by_css_selector("a.last")
                driver.execute_script("arguments[0].setAttribute('class','last active')", last_page)
                l_page = last_page.text
                driver.execute_script("arguments[0].setAttribute('class','last')", last_page)
            next_sibling = driver.execute_script("return arguments[0].nextElementSibling", active_page)
            next_sibling.click()
            active_page=active_page.text
            print(f"page no {active_page} of {l_page}")
            time.sleep(3)
        except Exception:
            print("No pagination")
            active_page=''
            l_page=''
        return active_page, l_page

    def add_to_list(self, company):
        people= []
        print(f"opening compmany: {company['company_name']}")
        driver.get(company['company_link'])
        time.sleep(4)
        status=False
        l_page=''
        roles=["cfo","controller","ceo","chief executive officer","chief financial officer"]
        while True:
            try:
                table = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.table-flex.columns_4")))
                self.records_on_page()
                all_people = table.find_elements_by_css_selector("div.table-flex__row")
                for x in all_people:
                    try:
                        table_cell = x.find_elements_by_css_selector("div.table-flex__cell")
                        get_tag = table_cell[1].find_element_by_css_selector("span.data-value.prospect")
                        element = get_tag.find_element_by_tag_name("a")
                        person_name = element.text
                        person_link = element.get_attribute("href")
                        role = table_cell[3].find_element_by_css_selector("span.data-value").text
                        is_role = [x for x in roles if x in role.lower()]
                        if  is_role:
                            driver.execute_script("arguments[0].scrollIntoView();", table_cell[0].find_element_by_tag_name("span"))
                            driver.execute_script("window.scrollTo(window.pageYOffset, window.pageYOffset-100);")
                            table_cell[0].click()
                            print(f"name of person is {person_name} and role is {role}")
                            status=True
                    except:
                        pass

                if status:
                    try:
                        add_t0 = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.app-dropdown")))
                        driver.execute_script("arguments[0].scrollIntoView();", add_t0)
                        add_t0.click()
                        add_to_list = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"ul.style-scroll")))
                        lists = add_to_list.find_elements_by_tag_name("li")
                        if lists:
                            self.list_name= lists[-1].find_element_by_tag_name("a").text
                            lists[-1].click()
                            time.sleep(4)
                    except:
                        pass
            except Exception as ex:
                print(ex)

            f_page, l_page = self.pagination(l_page=l_page)
            if f_page==l_page: 
                break

    def create_csv(self, data):
        if os.path.exists("data.csv"): os.remove("data.csv")
        with open("data.csv",mode='a',newline='') as output_file:
            output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            output_writer.writerow(["Name","Email", "Role","Company","Industry","Country"])
            for each in data:
                try:
                    output_writer.writerow([each['name'], each['email'], each['role'], each['company'], each['industry'], each['country'] ])
                except:
                    pass

    def get_person_info(self):
        try:
            body = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.panel-body")))
            name = body.find_element_by_css_selector("h1.content-title")
            next_sibling = driver.execute_script("return arguments[0].nextElementSibling", name)
            name = name.text
            desc = next_sibling.text
            split = desc.split("•")
            role = split[0]
            company = split[1]
            tbl = driver.find_element_by_css_selector("table.table-text-info")
            rows = tbl.find_elements_by_tag_name("tr")
            email= ''
            for x in rows:
                col = x.find_elements_by_tag_name("td")
                if col:
                    if "emails" in col[0].text.lower():
                        email = col[1].find_element_by_css_selector("span.email-item").text
            return {"name":name,"role":role,"company":company, "industry":self.industry,"country":self.country,"email":email}
        except:
            pass
            return {}

    def get_people(self, lst_link):
        print("getting profile link..")
        driver.get(lst_link)
        time.sleep(2)
        all_persons = []
        while True:
            try:
                contact_table = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"table.contacts-table")))
                t_body =  contact_table.find_element_by_tag_name("tbody")
                all_rows= t_body.find_elements_by_tag_name("tr")
                for x in all_rows:
                    try:
                        cell = x.find_element_by_css_selector("td.cell-contact")
                        person_link  = cell.find_element_by_tag_name("a").get_attribute("href")
                        all_persons.append(person_link)
                    except Exception:
                        pass

                try:
                    # pagination
                    pag = driver.find_element_by_css_selector("div.paginator")
                    ul = pag.find_element_by_css_selector("ul.list-inline")
                    li = ul.find_elements_by_css_selector("li")
                    if li:
                        if "next" in li[-1].find_element_by_tag_name("small").text.lower():
                            li[-1].click()
                            time.sleep(4)
                except:
                    break
                    pass
                
            except Exception:
                break
                pass

        return all_persons

    def go_to_list(self):
        driver.get("https://app.snov.io/prospects")
        try:
            lists_ul = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR,"ul.list-unstyled")))
            lists = lists_ul.find_elements_by_tag_name("li")
            if lists:
                for x in lists:
                    item_name = x.find_element_by_css_selector("span.sidebar-item-name").text
                    if item_name==self.list_name:
                        item_link=x.find_element_by_tag_name("a").get_attribute("href")
            return item_link
        except Exception:
            print("error while getting list link")
            return ''

    def main(self):
        data=[]
        with open("config.json","rb") as config_file:
            input_data = json.loads(config_file.read())
        for x in input_data['criteria']:
            self.country = x['country']
            self.industry = x['industry']
            self.range = x['company_size']
            print(f"\nSearching Criteria is::\n\nCountry:::::: {self.country}\nIndustry::::::::: {self.industry}\nCompany_Size::::::: {self.range}")
            print("\nAdding criteria")
            self.company_profile_search()
            print("Searching criteria....")
            all_companies = self.get_all_compaines()
            print("opening companies..")
            for company in all_companies:
                self.add_to_list(company)

            lst_link =self.go_to_list() 

            if lst_link:
                pipl_list =  self.get_people(lst_link)
                print(f"Total people is {len(pipl_list)}")
                for index, link in enumerate(pipl_list):
                    driver.get(link)
                    print(f"getting user info {index} of {len(pipl_list)}")
                    info = self.get_person_info()
                    data.append(info)
                print("Creating Csv file....")
                self.create_csv(data)
                print("Csv file created successfully....")

if __name__ == "__main__":
    DataCrawler().main()