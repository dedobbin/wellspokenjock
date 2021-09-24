import requests
import logging
from bs4 import BeautifulSoup
from common import BadResponse, parse_to_int

headers = {
  "Host" : "www.wsj.com",
  "Referer" : "https://www.wsj.com",
  "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0",
}

class CompanyData:
    url : str = ""
    name : str = ""

    company_value = None
    shares_outstanding = None
    public_float = None
    overview_currency = None #Will hold something like "$"

    assets_currency_type = None #Will hold something like "CAD"
    net_property_plant_and_equipment = None
    total_assets = None
    total_liabilities = None
    net_goodwill = None

    def __init__(self, name : str, url : str):
        self.name = name
        self.url = url

    def to_str(self):
        return str(self.__dict__)

def get_company_data(name: str, url: str) -> CompanyData:
    """Creates a CompanyData object and tries to fill all its datapoints"""
    company_data = CompanyData(name, url)

    overview_data = get_overview_data(url)
    if (not overview_data["shares_outstanding"] and not overview_data["public_float"]):
        logging.info("Requested data not found on company overview " + url + ", aborting")
        return company_data
      
    company_data.company_value = overview_data["company_value"]
    company_data.overview_currency = overview_data["overview_currency"]
    company_data.shares_outstanding = overview_data["shares_outstanding"]
    company_data.public_float = overview_data["public_float"]

    #Perhaps not needed to explicitly delete, could just ignore later
    if company_data.shares_outstanding != None and company_data.public_float != None:
      company_data.public_float = None

    #Other datapoints
    balance_sheet_url = url + "/financials/annual/balance-sheet"
    balance_sheet_data = get_balance_sheet_data(balance_sheet_url)

    company_data.assets_currency_type = balance_sheet_data["assets_currency_type"]
    company_data.net_property_plant_and_equipment  = balance_sheet_data["net_property_plant_and_equipment"]
    company_data.total_assets  = balance_sheet_data["total_assets"]
    company_data.total_liabilities  = balance_sheet_data["total_liabilities"]
    company_data.net_goodwill  = balance_sheet_data["net_goodwill"]

    return company_data

def get_company_list_page(page: int=1):
    base = "https://www.wsj.com/market-data/quotes/company-list/country/united-states/"
    url = base + str(page)
    return __get_html(url)

def get_overview_data(url: str):
    """Returns dict with shares_outstanding and public_float"""
    html = __get_html(url)
    soup = BeautifulSoup(html, features="html.parser")

    output = {
        "shares_outstanding": None, 
        "public_float": None, 
        "company_value":None, 
        "overview_currency": None
    }

    market_value_elems = soup.select("[class*=WSJTheme--cr_num] *")
    if len(market_value_elems) < 2:
        logging.info("Failed to get overview_data from " + url)
        return output

    output["overview_currency"] = market_value_elems[0].decode_contents()
    output["company_value"] = parse_to_int(market_value_elems[1].decode_contents())

    key_stock_data = soup.select("[class*=cr_data_field]")

    for entry in key_stock_data:
        data_label =  entry.select_one("[class*=data_lbl]").decode_contents().strip()
        data_value_html = entry.select_one("[class*=data_data]")
        if not data_value_html:
            continue
        data_value = data_value_html.decode_contents()

        if data_label == "Shares Outstanding":
            output["shares_outstanding"] = parse_to_int(data_value)
        elif data_label == "Public Float":
            output["public_float"] = parse_to_int(data_value)
    
    return output

def get_balance_sheet_data(url : str):
    """Returns dict with assets_currency_type, net_property_plant_and_equipment, total_assets, total_liabilities and net_goodwill"""
    html = __get_html(url)
    soup = BeautifulSoup(html, features="html.parser")

    output = {
        "assets_currency_type": None,
        "net_property_plant_and_equipment": None,
        "total_assets" : None,
        "total_liabilities": None,
        "net_goodwill": None,
    }
    
    tables = soup.select(".cr_dataTable")
    if len(tables) == 0:
        logging.info("Failed to get balance_sheet_data from " + url)
        return output
    
    assets_table = tables[0]

    table_header = assets_table.find(class_="fiscalYr")
    
    #Something like "Fiscal year is November-October. All values CAD Thousands."
    table_header_str = table_header.decode_contents()
    dot_pos = table_header_str.find(".")
    currency_value_str = table_header_str[dot_pos+1 : len(table_header_str)-1]
    arr = currency_value_str.strip().split(" ")
    assets_amount_type = ""
    if len(arr) != 4:
        logging.info("Failed to get assets_currency_type and assets_amount_type from " + url)
        return output
    else:
        output["assets_currency_type"] = arr[2]
        assets_amount_type = arr[3]

    for row in assets_table.select(".cr_dataTable tr"):
        #@todo: process strings to numbers?
        table_data = row.find_all("td")
        if len(table_data) == 0:
            continue
        elif "Net Property, Plant" in table_data[0].decode_contents():
            output["net_property_plant_and_equipment"] = parse_to_int(table_data[1].decode_contents(), assets_amount_type)
        elif table_data[0].decode_contents().strip() == "Total Assets":
            output["total_assets"] = parse_to_int(table_data[1].decode_contents(), assets_amount_type)
        elif table_data[0].decode_contents().strip() == "Net Goodwill":
            net_goodwill = table_data[1].decode_contents().strip();
            output["net_goodwill"] = parse_to_int(net_goodwill, assets_amount_type) if net_goodwill != "-" else None
    
    liabilities_table = tables[1]
    for row in liabilities_table.select(".cr_dataTable tr"):
        #@todo: process strings to numbers?
        table_data = row.find_all("td")
        if len(table_data) == 0:
            continue
        elif "Total Liabilities" in table_data[0].decode_contents():
            output["total_liabilities"] = parse_to_int(table_data[1].decode_contents(), assets_amount_type)
            break

    return output

def get_links_from_company_list_page(page: int):
    """Returns list of dicts, containing a name and url."""
    html = get_company_list_page(page)
    soup = BeautifulSoup(html, features="html.parser")
    company_links = soup.select(".cl-table a")
    results = list(map(lambda a: {"name": a.find(class_="cl-name").decode_contents(),"url": a["href"]}, company_links))
    return results

def get_company_list_page_count():
    html = get_company_list_page()
    soup = BeautifulSoup(html, features="html.parser")
    pagination_list_items = soup.select(".cl-pagination li a")

    #@todo Check if final item content == next for sanity
    last_index = len(pagination_list_items)-2 # -2 because final entry will contain "next"
    return int(pagination_list_items[last_index].decode_contents().split("-")[-1])

def __get_html(url : str):
    res = requests.get(url, allow_redirects=True, headers=headers)
    if (res.status_code != 200):
        raise BadResponse(res.status_code, url)
    return res.text