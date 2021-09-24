import wsj
from common import parse_to_int
from time import sleep
from random import randrange
import logging

def get_meaningful_data(company_data: wsj.CompanyData):
  output = {
    "market_value": None,
    "fair_value": None,
    "market_to_fair_value_margin": None,
  }

  output["fair_value"] = company_data.get_fair_value()
  if not output["fair_value"]:
    return output

  if company_data.market_value:
    output["market_value"] = company_data.market_value
    output["market_to_fair_value_margin"] = company_data.market_value / output["fair_value"]
  else:
      logging.warning("get_meaningful_data: Can't calculate market_to_fair_value_margin because company has no market_value, "
         + company_data.name)
    
  return output

def main():
  logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

  # company_data = wsj.get_company_data("stuff", "https://www.wsj.com/market-data/quotes/YQ")
  # print(company_data.to_str())

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
        logging.error("Could not get data of '" + (company_link["name"] if "name" in company_link else "unknown company") + "': " +  str(e))
        continue
      #print(company_data.to_str())
      meaningful_data = get_meaningful_data(company_data)
      if meaningful_data["market_value"] and meaningful_data["fair_value"] and meaningful_data["market_to_fair_value_margin"]:
        print(meaningful_data)
      else:
        logging.warning("FAILED getting meaningful data for " + company_link["name"])
        


      sleep(randrange(5))

if __name__ == "__main__":
  main()