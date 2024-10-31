import requests

def main():
    creds = open("bing.key").readlines()

    subscription_key = creds[0].strip()
    custom_config_id = creds[1].strip()

    prompt = """**Search Query for IP Cameras:**

- **Product Specifications:**
  - IP Camera with ingress protection of IP65
  - Resolution of 1080p
  - Frame rate of 30 fps
  - Supports protocols: HTTP, RTSP
  - Supports video encoding: H.264, H.265

- **Desired Results:**
  - Min results: 10
  - Max results: 20

- **Webshops to be Searched:**
  - Amazon (https://www.amazon.com)
  - eBay (https://www.ebay.com)
  - AliExpress (https://www.aliexpress.com)
  - Alza Hungary (alza.hu)

- **Data to be Extracted:**
  - Purchase link
  - Price
  - Manufacturer
  - Product name
  - Short description

- **Search Execution:**
  This query will be performed over the internet, using the specified webshops as sources to find the IP cameras that fit the specified criteria. The results will be formatted in a tabular layout showing the linkage to the product, price, manufacturer, product name, and a description.

After executing this search query:

- Visit the specified URLs to perform the search.
- Filter for IP cameras that meet the given technical specs.
- Extract the information required in the desired result format.
- Collect at least 10 and up to 20 camera listings for further consideration.

Please use this guidance as a basis to perform the search and collate the desired results from the mentioned online retailers."""
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": prompt,
                "customconfig": custom_config_id,
              "textDecorations": True,
              "textFormat": "HTML"}
    search_url = "https://api.bing.microsoft.com/v7.0/custom/search/"
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    print(search_results)

"https://api.bing.microsoft.com/v7.0/custom/search?q=fa&customconfig=5d9afe38-eec4-4924-9118-2a708cf5bda0&mkt=en-US"
if __name__ == "__main__":
    main()
