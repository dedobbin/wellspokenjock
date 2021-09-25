import wsj
from common import parse_to_int
from time import sleep
from random import randrange
import logging
import os
import time

def meaningful_data_to_csv(company_data: wsj.CompanyData, filename: str, delimiter: str = ","):
  fair_value = company_data.get_fair_value()
  output = {
    "name": company_data.name,
    "market_value":  company_data.market_value,
    "fair_value": fair_value,
    "market_to_fair_value_margin": company_data.market_value /fair_value,
    "time": time.strftime("%Y-%m-%d %H:%M:%S")
  }
  
  set_header = not os.path.exists(filename)
  if set_header:
    logging.info("Creating new CSV file, " + filename)
  else:
    logging.info("Appending to CSV file, " + filename)

  with open(filename, "a+") as f:
    if set_header:
      logging.debug("Creating csv header")
      f.write(delimiter.join([str(e) for e in output.keys()]) + "\n")
    f.write(delimiter.join([str(e) for e in output.values()]) + "\n")

def main():
  logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

  # company_data = wsj.get_company_data("stuff", "https://www.wsj.com/market-data/quotes/FISB")
  # meaningful_data = get_meaningful_data(company_data)
  # if meaningful_data["market_value"] and meaningful_data["fair_value"] and meaningful_data["market_to_fair_value_margin"]:
  #   print(meaningful_data)
  # else:
  #   logging.warning("FAILED getting meaningful data for " + company_data.name)

  num_pages = wsj.get_company_list_page_count()
  wsj.get_links_from_company_list_page(1)
  for i in range(1, num_pages+1):
    logging.info("Getting companies of page " + str(i))
    company_links = wsj.get_links_from_company_list_page(i)
    for company_link in company_links:
      logging.info("Getting data for " + company_link["name"])
      
      try:
        company_data = wsj.get_company_data(company_link["name"], company_link["url"])
      except Exception as e:
        logging.error("Could not get data of " + (company_link["name"] if "name" in company_link else "unknown company") + ": " +  str(e))
        continue
        
      if not company_data:
        logging.info("Could not essential data of " + (company_link["name"] if "name" in company_link else "unknown company") + ", skipping")
        continue
      #print(company_data.to_str())
      meaningful_data_to_csv(company_data, "companies.csv")
      
      sleep(randrange(5))

if __name__ == "__main__":
  main()