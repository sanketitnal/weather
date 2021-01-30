import sqlite3, requests, json, datetime

month_string = ["#", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
week_string = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def connect(filepath):
	conn = None
	try:
		conn = sqlite3.connect(filepath)
	except:
		print("Error connecting to database")
	return conn

def get_location(city, country):
	conn = connect("database/weatherdb.db")
	assert(conn != None)
	cur = conn.cursor()
	code = cur.execute("SELECT code from countrycodes WHERE lower(country)=\"{}\"".format(country.lower()))
	code = code.fetchone()
	
	response = None

	if code != None:
		#print(code[0])
		res = cur.execute("SELECT lat, long FROM latlong WHERE lower(city)=\"{}\" AND code=\"{}\"".format(city.lower(), code[0]))
		res = res.fetchone()
		if res != None:
			response = {
			"lat": res[0],
			"long": res[1]
			}

	return response

def get_date_month(full_date):
	day = full_date.day
	month = full_date.month
	return str(day) + " " + month_string[month]

def get_direction(deg):
	directions = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
	deg = deg % 360
	index = int(deg/45)%8
	return directions[index]

def get_weather(pos):
	assert(pos != None)
	API_KEY = "1a51b89680100f4d0fe696c190b3ad98"
	url = "http://api.openweathermap.org/data/2.5/onecall?lat=" + str(pos["lat"]) +"&lon=" + str(pos["long"]) + "&exclude=hourly,minutely,alerts&appid=" + API_KEY
	response = requests.get(url)
	weather = dict()
	if response:
		# convert response content to utf-8 format
		httpscontent = response.content.decode("utf-8")
		#convert the httpscontent into json object or dict() in this case
		jsonobj = json.loads(httpscontent)

		weather["current"] = dict()

		#get complete date information -> (year, month, date, hours, minutes, second)
		full_date = datetime.datetime.utcfromtimestamp(jsonobj["current"]["dt"]+jsonobj["timezone_offset"])
		# get integer representing day of the week i.e. Sunday=0 Monday=1 ...
		day = full_date.weekday()
		weather["current"]["date_summary"] = get_date_month(full_date)
		weather["current"]["day_of_week"] = week_string[day]
		weather["current"]["temp"] = jsonobj["current"]["temp"] - 273.15
		weather["current"]["temp"] = float("{:.2f}".format(weather["current"]["temp"]))
		weather["current"]["icon"] = jsonobj["current"]["weather"][0]["icon"]
		weather["current"]["wind_speed"] = jsonobj["current"]["wind_speed"]*18/5
		weather["current"]["wind_speed"] = float("{:.2f}".format(weather["current"]["wind_speed"]))
		weather["current"]["wind_direction"] = get_direction(jsonobj["current"]["wind_deg"])
		weather["current"]["humidity"] = jsonobj["current"]["humidity"]

		for i in range(0, 6):
			index = str(i)
			weather[index] = dict()
			weather[index]["day"] = week_string[(day+i+1)%7]
			weather[index]["temp_min"] = jsonobj["daily"][i]["temp"]["min"] - 273.15
			weather[index]["temp_min"] = float("{:.2f}".format(weather[index]["temp_min"]))
			weather[index]["temp_max"] = jsonobj["daily"][i]["temp"]["max"] - 273.15
			weather[index]["temp_max"] = float("{:.2f}".format(weather[index]["temp_max"]))
			weather[index]["icon"] = jsonobj["daily"][i]["weather"][0]["icon"]

	else:
		weather = None

	return weather

if __name__ == "__main__":
	weather = get_weather(get_location("Delhi", "India"))
	if weather != None:
		print(weather)
