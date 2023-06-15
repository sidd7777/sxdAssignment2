import pyodbc
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
from geopy.distance import geodesic

app = Flask(__name__)
app.config["SECRET_KEY"] = "SecureSecretKey"


def connection():
    server = "azure-ccbd.database.windows.net"
    database = "azure-ccbd_2023-06-13T01-27Z"
    username = "admin123"
    password = "S150600h*"
    driver = "{ODBC Driver 18 for SQL Server}"
    conn = pyodbc.connect(
        "DRIVER="
        + driver
        + ";SERVER="
        + server
        + ";PORT=1433;DATABASE="
        + database
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    return conn


@app.route("/", methods=["GET", "POST"])
def main():
    try:
        connectionNew = connection()
        sxdcursor = connectionNew.cursor()
        return render_template("index.html")
    except Exception as e:
        return render_template("index.html", error=e)


# Search by Magnitude


class Form1(FlaskForm):
    mag = StringField(label="Enter Magnitude: ", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


@app.route("/form1", methods=["GET", "POST"])
def form1():
    form = Form1()
    count = 0
    if form.validate_on_submit():
        try:
            connectionNew = connection()
            sxdcursor = connectionNew.cursor()
            magnitude = float(form.mag.data)
            sxdcursor.execute(
                "SELECT * FROM [dbo].[earthquake] where mag > ?;", magnitude
            )
            results = []
            while True:
                input_row = sxdcursor.fetchone()
                if not input_row:
                    break
                results.append(input_row)
                count += 1
            return render_template(
                "form1.html",
                result=results,
                cnt=count,
                mag=magnitude,
                form=form,
                data=1,
            )

        except Exception as e:
            print(e)
            return render_template(
                "form1.html", form=form, error="Magnitude must be numeric.", data=0
            )
    return render_template("form1.html", form=form)


# Search by Range & Days


class Form2(FlaskForm):
    r1 = StringField(label="Enter Magnitude Range 1: ", validators=[DataRequired()])
    r2 = StringField(label="Enter Magnitude Range 2: ", validators=[DataRequired()])
    start = DateField(
        label="Start Date: ", format="%Y-%m-%d", validators=[DataRequired()]
    )
    end = DateField(label="End Date: ", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


@app.route("/form2", methods=["GET", "POST"])
def form2():
    form = Form2()
    if form.validate_on_submit():
        try:
            connectionNew = connection()
            sxdcursor = connectionNew.cursor()
            r1 = float(form.r1.data)
            r2 = float(form.r2.data)
            start_date = form.start.data
            end_date = form.end.data
            count = 0

            # if days > 30 or r1 > r2:
            #     raise Exception()
            # today = date.today()
            # days_ago = today - timedelta(days=days)
            # print(days_ago)

            sxdcursor.execute(
                "SELECT * FROM [dbo].[earthquake] WHERE time BETWEEN CAST(? AS datetime) AND CAST(? AS datetime) AND mag BETWEEN ? AND ?",
                start_date,
                end_date,
                r1,
                r2,
            )

            results = []
            while True:
                input_row = sxdcursor.fetchone()
                if not input_row:
                    break
                results.append(input_row)
                count += 1
                
            return render_template(
                "form2.html",
                result=results,
                cnt=count,
                r1=r1,
                r2=r2,
                start=start_date,
                end=end_date,
                form=form,
                data=1,
            )

        except Exception as e:
            print(e)
            return render_template(
                "form2.html",
                form=form,
                error="Range 1 and Range 2 must be numeric, Range 1 > Range 2 and Days must be integer and less then 31.",
                data=0,
            )

    return render_template("form2.html", form=form, data=0)


# Search by Location


class Form3(FlaskForm):
    lat = StringField(label="Enter Latitude: ", validators=[DataRequired()])
    lon = StringField(label="Enter Longitude: ", validators=[DataRequired()])
    km = StringField(label="Enter Kilometers: ", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


@app.route("/form3", methods=["GET", "POST"])
def form3():
    form = Form3()
    if form.validate_on_submit():
        try:
            connectionNew = connection()
            sxdcursor = connectionNew.cursor()
            lat = float(form.lat.data)
            lon = float(form.lon.data)
            km = float(form.km.data)
            count = 0

            sxdcursor.execute(
                "SELECT time, latitude, longitude, mag, id, place, type FROM [dbo].[earthquake]"
            )
            results = []
            while True:
                input_row = sxdcursor.fetchone()
                if not input_row:
                    break
                if (
                    geodesic((float(input_row[1]), float(input_row[2])), (lat, lon)).km
                    <= km
                ):
                    results.append(input_row)
                    count += 1
            return render_template(
                "form3.html",
                result=results,
                cnt=count,
                lat=lat,
                lon=lon,
                km=km,
                form=form,
                data=1,
            )

        except Exception as e:
            print(e)
            return render_template(
                "form3.html",
                form=form,
                error="Latitude must be in the [-90; 90] range, Latitude must be in [-180; 180] and all input must be numeric.",
            )
    return render_template("form3.html", form=form, data=0)


# Search by Clusters


@app.route("/form4", methods=["GET", "POST"])
def form4():
    if request.method == "POST":
        try:
            connectionNew = connection()
            sxdcursor = connectionNew.cursor()
            cluster = request.form["clus"]
            count = 0

            sxdcursor.execute(
                "SELECT * FROM [dbo].[earthquake] where type = ?", cluster
            )
            results = []
            while True:
                input_row = sxdcursor.fetchone()
                if not input_row:
                    break
                results.append(input_row)
                count += 1
            return render_template(
                "form4.html", result=results, cnt=count, clus=cluster, data=1
            )

        except Exception as e:
            print(e)
            return render_template(
                "form4.html",
                error="Range 1 and Range 2 must be numeric, Range 1 > Range 2 and Days must be integer and less then 31.",
                data=0,
            )

    return render_template("form4.html", data=0)


# Does given Magnitude occur more often at night?


@app.route("/form5", methods=["GET", "POST"])
def form5():
    count = 0
    tot_cnt = 0
    try:
        connectionNew = connection()
        sxdcursor = connectionNew.cursor()

        sxdcursor.execute("select * from dbo.earthquake where mag > 4.0")
        results = []
        while True:
            input_row = sxdcursor.fetchone()
            if not input_row:
                break
            hour = dt.strptime(input_row[0], "%Y-%m-%dT%H:%M:%S.%fZ").hour
            if hour > 18 or hour < 7:
                results.append(input_row)
                count += 1
            tot_cnt += 1
        return render_template(
            "form5.html", result=results, cnt=count, tot_cnt=tot_cnt, data=1
        )

    except Exception as e:
        print(e)
        return render_template("form5.html", error="Magnitude must be numeric.", data=0)


if __name__ == "__main__":
    app.run(debug=True)
