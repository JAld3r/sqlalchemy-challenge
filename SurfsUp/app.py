# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import json

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy import text

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measure = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# /
# Start at the homepage.
# List all the available routes.

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


# /api/v1.0/precipitation
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)

    yr1_data_prec = engine.execute(text("""SELECT date, prcp FROM measurement WHERE date BETWEEN '2016-08-23' AND '2017-08-23' ORDER BY date DESC"""))

    session.close()

    data = {date:prcp for date, prcp in yr1_data_prec}
    # json_data = json.dumps(data)
    return jsonify(data)





# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    station_list = engine.execute(text("""SELECT DISTINCT station FROM measurement"""))

    session.close()

    station_data = {station[0]: None for station in station_list}

    return jsonify(station_data)


# /api/v1.0/tobs
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def active_station():

    session = Session(engine)

    station1 = engine.execute(text("""SELECT date, tobs FROM measurement WHERE date BETWEEN '2016-08-23' AND '2017-08-23' AND station = 'USC00519281' """))

    session.close()

    station1_data = {date:tobs for date, tobs in station1}

    return jsonify(station1_data)



# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temps(start=None, end=None):

    session = Session(engine)
    """Return TMIN, TAVG, and TMAX"""
    sel = [func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs)]

    if not end:
        # calculate the TMIN, TAVG, and TMAX for dates greater than and equal to the start date
        results = session.query(*sel).\
            filter(measure.date >= start).all()
        # unpack the results as a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    results = session.query(*sel).\
        filter(measure.date >= start).\
        filter(measure.date <= end).all()
    # unpack the results as a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)