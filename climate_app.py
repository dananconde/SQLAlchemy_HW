import numpy as np
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# Date Database

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

Base = automap_base()

Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Link

session = Session(engine)

# Flask Setup

app = Flask(__name__)

##############################
# Flask Routes
##############################

# Homepage that lists all available routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return"""<html>
    <h1>Climate in Hawaii</h1>
    <ul>
    <li>
    Precipitations:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>

    <li>
    List of Stations: 
    <br>
    <a href="/api/v1.0/stations">/api/v1.0/stations</a>
    </li>
    <br>

    <li>
    List of Temperature Observations:
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>

    <li>
    Minimum, maximum and average temperatures for the dates greater than or equal to the date provided:
    <br>
    <a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a>
    </li>
    <br>

    <li>
    Minimum, maximum and average temperatures for dates in range: 
    <br>
    <a href="/api/v1.0/2017-01-01/2017-01-07">/api/v1.0/2017-01-01/2017-01-07</a>
    </li>
    <br>
    
    </ul>
    </html>
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """Return a list of precipitations from last year"""
    
    maximum_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    maximum_date = maximum_date[0]

    date_year_ago = dt.datetime.strptime(maximum_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_year_ago).all()

    precipitation_dict = dict(results_precipitation)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    """Return a JSON list of stations from the dataset."""

    stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    maximum_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    maximum_date = maximum_date[0]

    date_year_ago = dt.datetime.strptime(maximum_date, "%Y-%m-%d") - dt.timedelta(days=366)
   
    temp_observations = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= date_year_ago).all()

    tobs_list = list(temp_observations)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start=None):
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_list=list(start)
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)

if __name__ == '__main__':
    app.run(debug=True)
