# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

MAX_DATE_STR = dt.date(dt.MAXYEAR,12,31).isoformat()

#################################################
# Database Setup 
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Retrieve the table names

table_names = Base.metadata.tables.keys()

print("Table names in the database:")
for table_name in table_names:
    print(table_name)

# Save references to each table

Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# HTML Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


#################################################
# API Routes
#################################################

# Convert the query results from your precipitation analysis 
#(i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    
    # Query to find most recent data point in the database. 
    max_date = session.query(func.max(Measurement.date)).first()
    latest_date = max_date[0]

    # Convert the string to a date object
    last_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()

    # Subtract a year using timedelta
    one_year_ago = last_date_obj - dt.timedelta(days=365)

    # Query from precipitation analysis to retrieve only the last 12 months of data
    analysis_data = session.query( Measurement.date,Measurement.prcp
                    ).filter( Measurement.date<=MAX_DATE_STR
                            ).filter(Measurement.date >= one_year_ago).all()
    
    prcp_data = []
    for date, prcp in analysis_data:
        prcp_data_dict = {}
        prcp_data_dict["date"] = date
        prcp_data_dict["prcp"] = prcp
        prcp_data.append(prcp_data_dict)

    return jsonify(prcp_data)

    #Closing Session
    session.close()


# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    
    # Create  session (link) from Python to the DB
    session = Session(engine)
    
    #Query to get the station names
    station_name = session.query(Station.station).all()
    
    # Convert list of tuples into normal list
    station_name_list = list(np.ravel(station_name))
    
    #Closing Session 
    session.close()
    return jsonify(station_name_list)


# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    #Query to find the most active station
    most_active_station=session.query(Measurement.station,func.count(Measurement.station))\
                        .group_by(Measurement.station)\
                        .order_by(func.count(Measurement.station).desc()).first()
    
    # Get the most active station's ID
    most_active_station_id = most_active_station.station
    
    # Query to find most recent data point in the database. 
    max_date = session.query(func.max(Measurement.date)).first()
    latest_date = max_date[0]

    # Convert the string to a date object
    last_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()

    # Subtract a year using timedelta
    one_year_ago = last_date_obj - dt.timedelta(days=365)
    
    #Query the dates and temperature observations of the most-active station for the previous year of data.
   
    temp_observation = session.query(Measurement.date, Measurement.tobs)\
                        .filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago).all()
    
    #Session Closed
    session.close()
    
    #Convert the results to a JSON list
    tobs_data = [{"Date": temp[0], "Temperature": temp[1]} for temp in temp_observation]
    
    return jsonify(tobs_data)
   

@app.route("/api/v1.0/<start>")
def tstats_start(start):
    
    #Create  session (link) from Python to the DB
    session = Session(engine)
    start = '2016-08-23'
    
    #Query to get temprature data for a specified start date 
    tstats_data = session.query(func.min(Measurement.tobs),\
                                func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs))\
                                .group_by(Measurement.station)\
                                .filter(Measurement.date>start).all()
    
    #Convert the results to a JSON list
    tobs_data_list = [{"TMIN": tdata[0], "TMAX": tdata[1], "TAVG": tdata[2]} for tdata in tstats_data]
    
    #Session Closed
    session.close()
    return jsonify(tobs_data_list)


@app.route("/api/v1.0/<start>/<end>")
def tstats_end(start,  end=MAX_DATE_STR):
    
    # Create session (link) from Python to the DB
    session = Session(engine)
    start = '2015-08-23'
    
    #Query to get temprature data for a specified start date and end date
    tstats_data = session.query(func.min(Measurement.tobs),\
                                func.max(Measurement.tobs),\
                                func.avg(Measurement.tobs))\
                                .group_by(Measurement.station
                                      ).filter(Measurement.date>start
                                              ).filter(Measurement.date<end).all()
    
    #Convert the results to a JSON list
    tobs_data_list = [{"TMIN": tdata[0], "TMAX": tdata[1], "TAVG": tdata[2]} for tdata in tstats_data]
    
    #Session Closed
    session.close()
    return jsonify(tobs_data_list)

   
if __name__ == '__main__':
    app.run(debug=True)


    









