import sys
from flask import Flask, render_template,jsonify,request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sqlalchemy import text


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db/inpatient.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Base = automap_base(metadata=db.metadata)
engine = db.get_engine()
Base.prepare(engine, reflect=True)
Inpatient = Base.classes.inpatient
Drg = Base.classes.drg
Hrr = Base.classes.hrr
Provider = Base.classes.provider


@app.route("/")
def index():
    r"""Display the intro page"""
    return render_template("index.html")

@app.route("/explore")
def explore():
    return render_template("explore.html")

@app.route("/predict", methods=['POST', 'GET'])
def predict():
	if request.method == 'GET':
		print('GET GET GET')
		return render_template('predict.html')
	if request.method == 'POST':
		print('POST POST POST')
		selecteddrg = request.form.get("drgSel", None)
		print (selecteddrg)
		selectedhrr = request.form.get("hrrSel", None)
		print(selectedhrr)	
		drg = selecteddrg.split("|")
		print(drg)
		
		hrr = selectedhrr.split("|")
		print(hrr)
		
		selectedprovider = request.form.get("providerSel", None)
		print(selectedprovider)	
		provider = selectedprovider.split("|")
		
		X_test = []
		X_test.append(drg[0])
		X_test.append(provider[0])
		X_test.append(hrr[0])
		X_test.append(drg[1])
		X_test.append(drg[2])
		X_test.append(drg[3])
		
		X_test_df = pd.DataFrame(np.array(X_test).reshape(1, 6))
		print(X_test_df.head())
		print (X_test)
		
		drg_definition = drg[4]
		hrr_description = hrr[1]
		provider_name = provider[1]
		joblib_model = joblib.load('LinearRegression_model2.pkl')		
		#joblib_model = joblib.load('LinearRegression_model.pkl')
		Ypredict = joblib_model.predict(X_test_df)
		Ypredict = "${0:,.2f}".format(Ypredict[0][0])
		print(Ypredict)
			
		return render_template("predict.html", drg_definition=drg_definition, provider_name=provider_name, hrr_description=hrr_description, Ypredict=Ypredict)


@app.route("/question")
def question():
    return render_template("question.html")

@app.route("/data")
def data():
    r"""Display the data page"""
    return render_template("data.html")

@app.route("/inpatient_data")
def inpatient_data():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).all()
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)
	
	
@app.route("/drg_all")
def alldrg_data():
    r""" Returns a json of all drg data - this is used on predict page load """

    response = db.session.query(Drg).all()
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)
	
	
@app.route("/hrr_all")
def allhrr_data():
    r""" Returns a json of all hrr data - this is used on Predict page load"""

    response = db.session.query(Hrr).all()
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)	

	
@app.route("/hrr/<drg>")
def hrrwithdrg_data(drg):
    r""" Returns a json of hrr that has performed the selected drg data - """
    r""" this is used to refresh hrr dropdown once a drg is selected"""
	
    print("hrrwithdrg_data:")
    print(drg)
    sql = text ('select distinct i.hrr_description, h.hrr_id \
			     from   inpatient i \
			     join   hrr  h  \
				    on  i.hrr_description = h.hrr_description  \
			     where  i.drg_definition = :drg \
			     order by i.hrr_description ')
						  
    print (sql)
    response = db.engine.execute(sql, {'drg': drg}).fetchall()
    #print (response)
 		
    hrr_list = []
    for r in response:
        d_dictionary = {}
        d_dictionary['hrr_description'] = r[0]
        d_dictionary['hrr_id'] = r[1]
        hrr_list.append(d_dictionary)
    return jsonify(hrr_list)	

	
@app.route("/provider_all")
def allprovider_data():
    r""" Returns a json of all provider data - this is used on predict page load"""

    response = db.session.query(Provider).all()
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)


@app.route("/hrrprovider/<drghrr>")
def providerindrghrr_data(drghrr):
    r""" Returns a json of providers who's in the selected hrr and have performed the selected procdures data"""
    r""" this is used to refresh provider dropdown once selections were made on both drg and hrr dropdown boxes """
	
    print("provider with in region that had perform the procedure:")
    print(drghrr)
    drg_hrr = drghrr.split("|")
    drg = drg_hrr[0]
    hrr = drg_hrr[1]
    print (drg)
    print (hrr)
    sql = text ('select distinct p.provider_rowid, p.provider_name \
			     from   inpatient i \
                 join   provider  p \
                    on  i.provider_id = p.provider_id \
			     where  i.drg_definition = :drg \
                 and    i.hrr_description = :hrr \
			     order by p.provider_name ')
						  
    print (sql)
    response = db.engine.execute(sql, {'drg': drg, 'hrr': hrr}).fetchall()
    #print (response)
	
    provider_list = []
    for r in response:
        d_dictionary = {}
        d_dictionary['provider_rowid'] = r[0]
        d_dictionary['provider_name'] = r[1]
        provider_list.append(d_dictionary)
    return jsonify(provider_list)	
	
	
@app.route("/drg119")
def drg119():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '190 - CHRONIC OBSTRUCTIVE PULMONARY DISEASE W MCC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg119summary")
def drg119summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 190 - CHRONIC OBSTRUCTIVE PULMONARY DISEASE W MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '190 - CHRONIC OBSTRUCTIVE PULMONARY DISEASE W MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg122")
def drg122():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition ='193 - SIMPLE PNEUMONIA & PLEURISY W MCC' )
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg122summary")
def drg122summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 193 - SIMPLE PNEUMONIA & PLEURISY W MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '193 - SIMPLE PNEUMONIA & PLEURISY W MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg123")
def drg123():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '194 - SIMPLE PNEUMONIA & PLEURISY W CC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg123summary")
def drg123summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 194 - SIMPLE PNEUMONIA & PLEURISY W CC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '194 - SIMPLE PNEUMONIA & PLEURISY W CC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg193")
def drg193():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '291 - HEART FAILURE & SHOCK W MCC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg193summary")
def drg193summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 291 - HEART FAILURE & SHOCK W MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '291 - HEART FAILURE & SHOCK W MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg194")
def drg194():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '292 - HEART FAILURE & SHOCK W CC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg194summary")
def drg194summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 292 - HEART FAILURE & SHOCK W CC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '292 - HEART FAILURE & SHOCK W CC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg261")
def drg261():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '392 - ESOPHAGITIS, GASTROENT & MISC DIGEST DISORDERS W/O MCC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg261summary")
def drg261summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 392 - ESOPHAGITIS, GASTROENT & MISC DIGEST DISORDERS W/O MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '392 - ESOPHAGITIS, GASTROENT & MISC DIGEST DISORDERS W/O MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg310")
def drg310():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '470 - MAJOR JOINT REPLACEMENT OR REATTACHMENT OF LOWER EXTREMITY W/O MCC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg310summary")
def drg310summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 470 - MAJOR JOINT REPLACEMENT OR REATTACHMENT OF LOWER EXTREMITY W/O MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '470 - MAJOR JOINT REPLACEMENT OR REATTACHMENT OF LOWER EXTREMITY W/O MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg440")
def drg440():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '690 - KIDNEY & URINARY TRACT INFECTIONS W/O MCC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg440summary")
def drg440summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 690 - KIDNEY & URINARY TRACT INFECTIONS W/O MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '690 - KIDNEY & URINARY TRACT INFECTIONS W/O MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg517")
def drg517():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '871 - SEPTICEMIA OR SEVERE SEPSIS W/O MV >96 HOURS W MCC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg517summary")
def drg517summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 690 - 871 - SEPTICEMIA OR SEVERE SEPSIS W/O MV >96 HOURS W MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '871 - SEPTICEMIA OR SEVERE SEPSIS W/O MV >96 HOURS W MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

@app.route("/drg518")
def drg518():
    r""" Returns a json of the inpatient data"""

    response = db.session.query(Inpatient).filter_by(drg_definition = '872 - SEPTICEMIA OR SEVERE SEPSIS W/O MV >96 HOURS W/O MCC')
    d_list = []
    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        d_list.append(rec)
    return jsonify(d_list)

@app.route("/drg518summary")
def drg518summary():
    r""" Returns a json summarizing medicare charges and patient discharges by hrr for 872 - SEPTICEMIA OR SEVERE SEPSIS W/O MV >96 HOURS W/O MCC'"""

    #query the database
    response = db.session.query(Inpatient).filter_by(drg_definition = '872 - SEPTICEMIA OR SEVERE SEPSIS W/O MV >96 HOURS W/O MCC')

    #iterate through the response to get a readable copy
    fils = []

    for r in response:
        rec = r.__dict__.copy()
        del rec['_sa_instance_state']
        fils.append(rec)
    
    #feed the response into a DataFrame
    df = pd.DataFrame(fils)

    #build a function that will scrub the data to make it a proper number
    def sanitize(data):
        if type(data).__name__ != 'float':
            return (float( data.replace(",","")))
        else:
            return data

    #scrub the discharges column
    df['total_discharges'] = df['total_discharges'].apply(sanitize)

    #pivot the raw data into a summarized table
    summary = pd.pivot_table(df, index='hrr_description', values=['average_covered_charges', 'total_discharges'])

    #save pivot table to json
    return summary.reset_index().to_json(orient="records")

if __name__ == "__main__":
    app.run(debug=False)