from flask import Flask, render_template, redirect, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from apis import get_location, get_weather

app = Flask(__name__)
app.config["SECRET_KEY"] = "I86Ghgvas^4n(kasbd{]asdhv#4?sba"

class BasicForm(FlaskForm):
	city = StringField("", validators=[DataRequired()], render_kw={"placeholder": "city"})
	country = StringField("", validators=[DataRequired()], render_kw={"placeholder": "country"})
	submit = SubmitField("Submit")

@app.route("/", methods=["GET", "POST"])
def index():
	form = BasicForm()
	weather = None
	if session.get("default_weather") == None:
		session["default_weather"] = get_weather(get_location("Delhi", "India"))
		session["default_city"] = "Delhi"

	if form.validate_on_submit():
		pos = get_location(form.city.data.strip(), form.country.data.strip())
		if pos == None:
			flash("Can\'t find data for entered city, country. Please check the data and retry")
			session["weather"] = None
			session["city"] = None
		else:
			weather = get_weather(pos)
			session["weather"] = weather
			session["city"] = form.city.data
		return redirect("/")

	if session.get("weather") == None:
		return render_template("index.html", form=form, weather=session["default_weather"], city=session["default_city"])
	else:
		return render_template("index.html", form=form, weather=session["weather"], city=session["city"])

if __name__ == "__main__":
	app.run(debug=True)



