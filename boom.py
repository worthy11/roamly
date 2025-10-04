import requests

url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/getFlightDetails"

querystring = {"legs":"[{\"destination\":\"LOND\",\"origin\":\"LAXA\",\"date\":\"2024-04-11\"}]","adults":"1","currency":"USD","locale":"en-US","market":"en-US","cabinClass":"economy","countryCode":"US"}

headers = {
	"x-rapidapi-key": "85c6a7a651msh405464ea822aaabp112bb8jsnd2eb93b77ba6",
	"x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())