#!/usr/bin/python3

#usage
#./circuit_score.py proxy proxy 10.0.100.50 3306 dfa_msdb 60

# VERSION 2 - Modified on  2021/10/11, Adds LOGGING

import sys, traceback, os, time, datetime, json
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
import pymysql
import logging
from logging.handlers import RotatingFileHandler


VERSION = '2'

# create logger
# initialize logger
PROCESS_NAME = 'circuit-score'
SERVER_ID = '60'

# LOGGING OPTIONS
LOG_LEVEL = logging.INFO
LOG_SIZE = 1048576
LOG_BACKUPS = 10
LOG_EXTRA_INFO = False

#G_LOOK_BACK = 2*365*24*3600  #Two years
G_LOOK_BACK = 2*30*24*3600  #Two months
G_DAY = 24*3600 # One day

# Score thresholds
G_LOW_THRESH = 10 
G_HIGH_THRESH = 59

# configure logger
logger = logging.getLogger(PROCESS_NAME)
logger.setLevel(LOG_LEVEL)

# configure logfile handler
if not os.path.isdir('/var/log'):
    raise ImportError('Cannot initialize circuit-score.log, /var/log permission denied')
handler = RotatingFileHandler('/var/log/circuit-score.log', maxBytes=LOG_SIZE, backupCount=LOG_BACKUPS)
logger.addHandler(handler)

def convert_tuple(tup):
    str = ''.join(tup)
    return str

def logger_info(msg):
    print(msg)
    msg_t = '['+ str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '] ' + msg
    logger.info(msg_t)

def logger_error(msg):
    print(msg)
    msg_t = '[' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '] ' + msg
    logger.error(msg_t)

def logger_warn(msg):
    print(msg)
    msg_t = '[' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '] ' + msg
    logger.warning(msg_t)

def logger_critical(msg):
    print(msg)
    msg_t = '[' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '] ' + msg
    logger.critical(msg_t)

def logger_debug(msg):
    print(msg)
    msg_t = '[' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ']' + msg
    logger.info(msg_t)



logger_info('Starting grid-alert-sendmail V' + str(VERSION))




def str_time_from_int(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(t)))

def int_time_from_str(strTime):
    if len(strTime) == 19:
        return time.mktime(time.strptime(strTime, '%Y-%m-%d %H:%M:%S'))
    elif len(strTime) == 10:
        return time.mktime(time.strptime(strTime, '%Y-%m-%d'))
    return time.mktime(time.gmtime())

#Connect and get a session object
def connect_db(uanme='', password='', ipaddr='', port='', db=''):
    login_str = 'mysql+pymysql://' + uanme + ":" + password + "@" + ipaddr + ":" + port + "/" + db + "?charset=utf8"
    engine = create_engine(login_str, pool_recycle=3600, echo=False)
    base = declarative_base()
    metadata = MetaData()

    # create the whole object
    metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    return engine, Session

#Execute and return select query
def query_text(Session, tsql, param=None):
    session = scoped_session(Session)
    if param != None:
        ret = session.execute(tsql, param).fetchall()
    else:
        ret = session.execute(tsql).fetchall()
    session.close()
    return ret

#Get all circuits that don't have any entry in the circuit_score table
def get_new_circuits(Session):
    param = {}
    look_back = int_time_from_str('') - G_LOOK_BACK
    tsql = """ SELECT monitor_id from monitor WHERE 
            monitor_id NOT IN (select DISTINCT monitor_id from circuit_score_last_update) AND
            last_interval > FROM_UNIXTIME(:lookback)
    """
    param['lookback'] = look_back
    return query_text(Session, tsql, param)

#Get all circuits that have new reportable records
def get_circuits_with_activity(Session):
    tsql = """ SELECT 
    MAX(waveform_records.monitor_id) AS mid,
    UNIX_TIMESTAMP(circuit_score_last_update.last_update) AS unix_time
    FROM
        waveform_records,
        waveform_classifications,
        circuit_score_last_update
    WHERE
        waveform_records.monitor_id = circuit_score_last_update.monitor_id
            AND waveform_records.record_time > circuit_score_last_update.last_update
            AND waveform_classifications.monitor_id = waveform_records.monitor_id
            AND waveform_classifications.waveform_id = waveform_records.waveform_id
            AND waveform_classifications.classification_code IN (15110 , 15220, 23100, 23104, 23102, 23180, 23190)
            AND waveform_classifications.position_code = 0
    GROUP BY waveform_records.monitor_id
    """
    return query_text(Session, tsql)

#Retrurn circuit_score records for the previous two hours from a given hour for a circuit
def get_prev_hrs(Session, mid, unix_hr):
    param = {}
    param['monitor_id'] = mid
    param['time1'] = unix_hr - 3600
    param['time2'] = unix_hr - 3600*2
    tsql = """SELECT MAX(unix_time_hr) AS unix_time, MAX(score), run_id, dash_id
    FROM circuit_score
    WHERE monitor_id = :monitor_id
    AND (unix_time_hr = :time1 OR unix_time_hr = :time2)
    GROUP BY unix_time_hr
    ORDER BY unix_time DESC
    """
    return query_text(Session, tsql, param)

#Get the latest waveofrm record time for a given circuit
def get_latest_waveform_record_time(Session, monitor_id):
    param = {}
    tsql = """ SELECT record_time,
     UNIX_TIMESTAMP(DATE_FORMAT(record_time,'%Y-%m-%d %H:00:00')) as unix_time_hr
     FROM waveform_records
     WHERE 
     monitor_id = :monitor_id
     ORDER by record_time DESC LIMIT 1
    """
    param['monitor_id'] = monitor_id
    return query_text(Session, tsql, param)

#Compute the base circuit scores for a given time window
def get_base_circuit_scores(Session, monitor_id, lookback):
    param = {}
    if lookback is None:
        param['etime'] = int_time_from_str('')  + G_DAY
        param['stime'] = param['etime'] - G_LOOK_BACK
    else:
        param['etime'] = int_time_from_str('') + G_DAY
        param['stime'] =  lookback + 1

    param['mid'] = monitor_id

    tsql = """ SELECT 
        MAX(score.rec_time) as orig_time,
        TIMESTAMP(DATE_FORMAT(score.rec_time,'%Y-%m-%d %H:00:00'))  as time_hr,
        UNIX_TIMESTAMP(DATE_FORMAT(score.rec_time,'%Y-%m-%d %H:00:00')) as unix_time_hr,
        LEAST( MAX((CASE
            WHEN arc_score < 2 THEN 0
            WHEN arc_score < 4 THEN 5
            WHEN arc_score < 6 THEN 10
            ELSE 30
        END) + (CASE
            WHEN fault_score = 0 THEN 0
            WHEN fault_score < 4 THEN fault_score * 10
            ELSE 60
        END) + (CASE
            WHEN slap_score = 0 THEN 0
            WHEN slap_score > 0 THEN 20
            ELSE 0
        END) + (CASE
            WHEN broken_score = 0 THEN 0
            WHEN broken_score > 0 THEN 70
            ELSE 0
        END)), 100) AS value
        FROM
            (SELECT  
                    record_time AS rec_time,
                    SUM(IF(classification_code IN (23100 , 23104, 23102, 23180, 23190), 1, 0)) AS arc_score,
                    SUM(IF(classification_code IN (15110 , 20410, 15220) and waveform_features.feature_code =151002, 
                    GREATEST(feature_value_a,feature_value_b, feature_value_c), 0)) AS fault_score,
                    SUM(IF(waveform_features.feature_code = 151017, 1, 0)) AS slap_score,
                    SUM(IF(waveform_features.feature_code = 151012, 1, 0)) AS broken_score
            FROM
                waveform_records, waveform_classifications, waveform_features
            WHERE
                    waveform_records.monitor_id = :mid AND
                    record_time  BETWEEN  FROM_UNIXTIME(:stime) AND FROM_UNIXTIME(:etime)
                    AND waveform_classifications.monitor_id = waveform_records.monitor_id
                    AND waveform_classifications.waveform_id = waveform_records.waveform_id
                    AND waveform_features.monitor_id = waveform_records.monitor_id
                    AND waveform_features.waveform_id = waveform_records.waveform_id
                    AND ((waveform_classifications.classification_code IN (15110 , 15220)
                    AND ((waveform_features.feature_code = 151017
                    AND waveform_features.feature_value_a > 0)
                    OR (waveform_features.feature_code = 151012
                    AND waveform_features.feature_info LIKE '%Broken%')
                    OR waveform_features.feature_code = 151002))
                    OR (waveform_classifications.classification_code IN (23100 , 23104, 23102, 23180, 23190)
                    AND waveform_features.feature_code = 231001))
                    AND waveform_classifications.position_code = 0
            GROUP BY TIMESTAMP(DATE_FORMAT(record_time,'%Y-%m-%d %H:00:00'))) AS score
        WHERE
                score.rec_time BETWEEN  FROM_UNIXTIME(:stime) AND FROM_UNIXTIME(:etime)
        GROUP BY time_hr
        HAVING value > 0
        ORDER BY score.rec_time"""
    ret = query_text(Session, tsql, param)
    return ret

#insert or update circuit_score_last_update table with high watermark for a given circuit
def get_insert_into_scores_update(score, first):
    if first:
        insert_sql = """INSERT INTO circuit_score_last_update 
         (monitor_id, last_update)
         VALUES(:monitor_id, :score_time)
         ON DUPLICATE KEY UPDATE 
         last_update = :score_time,
         mod_time = NOW()
        """ 
    else:
        insert_sql = """UPDATE circuit_score_last_update SET 
         last_update = :score_time,
         mod_time = NOW()
         WHERE
         monitor_id = :monitor_id
        """
    return insert_sql

#Insert newly computed circuit socres for a circuit (accepts a list)
def insert_in_to_scores(final_scores, Session):
    insert_sql = """INSERT INTO circuit_score 
     (monitor_id, score, score_time, unix_time_hr, dash_id, run_id)
     VALUES(:monitor_id, :score, :score_time, :unix_time_hr, :dash_id, :run_id)
    """ 
    first = True
    for score in final_scores:
        session = scoped_session(Session)
        session.execute(insert_sql, score)
        session.execute(get_insert_into_scores_update(score, first), score)
        session.commit()
        session.close()
        first = False

#Based on teh circuit_Score update the dash_id to elevate the score to high score dashboard
def mark_as_high_dash(mid, run_ids, did, Session):
    param = {}
    param['mid'] = mid
    param['did'] = did

    tsql = """UPDATE circuit_score SET dash_id = :did 
    WHERE monitor_id = :mid 
    AND run_id = :run_id
    """
    for run_id in run_ids:       
        param['run_id'] = run_id
        session = scoped_session(Session)
        session.execute(tsql, param) 
        session.commit()
        session.close()    

#The main work horse of this script.
#Computes the final circuit score based on the base score using Jeff's logic
# he recursion is S(n) = Base + 0.5*S(n-1)+ 0.25*S(n-2)
def pre_populate_scores(engine, Session, first):
    try:
        #The very first time the script looks for new circuits and 
        #looks back a fixed time window to preopulate historical scores
        if first:
            circuits = get_new_circuits(Session)
        else:
            #Subsequent pases, only looks for newer records
            circuits = get_circuits_with_activity(Session)
        circ_count = 1
        if len(circuits) > 0:
            logger_info('Found new records')

        for circuit in circuits:
            if first:
                health_check_in(Session)
            print('In circuit: ', circuit[0], ' Circuit ', circ_count, ' of ', len(circuits) )
            #Get base scores to be able to do recursion
            base_scores = get_base_circuit_scores(Session, circuit[0], None if first  else circuit[1])
            print('Rows: ', len(base_scores))
            final_scores = []
            score_n_1 = 0
            score_n_2 = 0        
            time_1 = 0
            time_2 = 0    
            score_cnt = 1
            run_start = False
            run_stime = 0
            run_thresh = False            
            if len(base_scores) and not first:
                #Since the final scores needs the past two scores S(n-1) and S(n-2)
                #we get last two hours
                prev_hrs = get_prev_hrs(Session, circuit[0], base_scores[0][2]) 
                #When two records are fetched
                if len(prev_hrs) == 2:
                    score_n_1 = prev_hrs[0][1]  #S(n-1), Row 1, column 2
                    score_n_2 = prev_hrs[1][1]  #S(n-2), Row 2, column 2
                    time_1 = prev_hrs[0][0]     #unix timestamps rounded to hour     
                    time_2 = prev_hrs[1][0]
                #When only one record is fetched, match it to the right hour
                elif len(prev_hrs) == 1:
                    if prev_hrs[0][0] == (base_scores[0][2] - 3600):
                        score_n_1 = prev_hrs[0][1]
                        time_1 = prev_hrs[0][0]
                    else:
                        score_n_2 = prev_hrs[0][1]
                        time_2 = prev_hrs[0][0]
                if len(prev_hrs) > 0 and prev_hrs[0][2] > 0:
                    run_start = True
                    run_stime = prev_hrs[0][2]
                    run_etime = prev_hrs[0][0]
                    run_thresh = True if prev_hrs[0][3] > 0 else False

            final_scores = []
            mark_run =[]
            for score in base_scores:
                #Reset previous scores if the prevuius hours are not avialble
                if time_1 != (score[2] - 3600):
                    score_n_1 = 0
                if time_2 != (score[2] - 2*3600):
                    score_n_2 = 0         
                    score_n_1 = 0
                #Compute final score based on recursion
                score_n = score[3] + 0.5*score_n_1 + 0.25*score_n_2

                #We need to keep track of consecutive scores that exceed the low threshold (G_LOW)
                #the reson being, if even a single score in this run exceeds the high threshold (G_HIGH)
                #the scores will be eleivated to the high score dashboard
                if not run_start:
                    #Start a run by setting run_Stert to true and set the id (run_stime) to current hour
                    #the run_stime will serve as teh run_id that will uniquely identify all scores that belong 
                    #to the same run
                    if score_n >= G_LOW_THRESH:
                        if score_n_1 >= G_LOW_THRESH and score_n_2 >= G_LOW_THRESH:
                            run_stime = time_2
                            run_start = True
                        elif  score_n_1 >= G_LOW_THRESH:
                            run_stime = time_1
                            run_start = True
                        else:
                            run_stime = score[2]
                #When score falls below the thrshold
                #end the run
                elif score_n < G_LOW_THRESH:
                    if run_thresh:
                        mark_run.append(run_stime)
                    run_start = False
                    run_stime = score[2]
                    run_thresh = False                    

                if run_start and max(score_n, score_n_1, score_n_2) > G_HIGH_THRESH:
                    run_thresh = True

                score_n = score_n if score_n >= G_LOW_THRESH else 0
                score_n_2 = score_n_1
                score_n_1 = score_n

                time_2 = time_1                
                time_1 = score[2]

                #Every valid score is added to a list (to be latter inserted into the database)
                #on a per circuit basis
                if score_n > 0:
                    final_scores.append(
                        {
                            'monitor_id':circuit[0],
                            'score': score_n,
                            'score_time': score[0],
                            'unix_time_hr': score[2],
                            'dash_id': 1 if run_thresh else 0,
                            'run_id': run_stime
                        }
                    )
                    rec_cnt = 1
                    #Recurse into future!
                    #The scoring formula is esentially like a stable IIR filter, so any exitation will result
                    #in decaying scores over time till they fall below a threshold (typically up to 10 hrs)
                    #As a result, it is good to compute future scores
                    while True:  
                        #Continue the run as long as at least one of the past two values exceeds threshold
                        if score_n_1 >= G_LOW_THRESH or score_n_2 >= G_LOW_THRESH:
                            if ((score_cnt + 1) <= len(base_scores) and (score[2] + 3600*rec_cnt) != base_scores[score_cnt ][2])  or (score_cnt + 1) > len(base_scores):                            
                                #The same scoring formula
                                score_n_1 =  (score_n_1*0.5 if score_n_1 > G_LOW_THRESH else 0 ) + (score_n_2*0.25 if score_n_2 > G_LOW_THRESH else 0)
                                #Keep track of the scores and time for use in the future iterations
                                score_n_2 = score_n
                                score_n = score_n_1 
                                time_2 = score[2] + (rec_cnt - 1)*3600                
                                time_1 = score[2] + rec_cnt*3600                           
                                if score_n_1 >= G_LOW_THRESH:
                                    if not run_start:
                                        run_stime = time_2
                                        run_start = True
                                    if run_start and max(score_n_1, score_n_2) > G_HIGH_THRESH:
                                        run_thresh = True                            
                                    #Append the future score if it is largeer than threshold         
                                    final_scores.append(
                                        {
                                            'monitor_id':circuit[0],
                                            'score': score_n_1,
                                            'score_time': score[0].replace(minute=0, second=0) + datetime.timedelta(hours=rec_cnt),
                                            'unix_time_hr': score[2] + rec_cnt*3600,
                                            'dash_id': 1 if run_thresh else 0,
                                            'run_id': run_stime
                                        }
                                    )  
                                    #print((score[2] + 3600*rec_cnt), base_scores[score_cnt ][2], score[0].replace(minute=0, second=0) + datetime.timedelta(hours=rec_cnt)) 
                                else:
                                    #Discontuinue the run if the scores fall below threshold
                                    if run_start and run_thresh:
                                        mark_run.append(run_stime)
                                        
                                    run_start = False
                                    run_stime = time_1
                                    run_thresh = False                                                                                                             
                            else:
                                break    
                        else:
                            if run_start:
                                mark_as_high_dash(circuit[0], run_stime, 1, Session)
                            score_n_1 = 0
                            score_n_2 = 0
                            score_n = 0
                            run_start = False
                            run_stime = time_1
                            run_thresh = False                                
                            break
                        rec_cnt = rec_cnt + 1
                score_cnt = score_cnt + 1
            #If no new scores were added    
            if len(base_scores) < 1:
                #Update the high watermark table
                rec_time = get_latest_waveform_record_time(Session, circuit[0])
                if len(rec_time):
                    print('Updating watermark for circuit: ', circuit[0])
                    record_time = rec_time[0][0]
                    unix_time = rec_time[0][1]
                    score = {
                        'monitor_id':circuit[0],
                        'score': 0,
                        'score_time': record_time,
                        'unix_time_hr': unix_time
                    }
                    session = scoped_session(Session)
                    session.execute(get_insert_into_scores_update(score, True), score)
                    session.commit()
                    session.close() 
            #If there are new scores
            else:
                #Insert new scores and update high watermark
                print('Inserting scores for circuit: ', circuit[0], ' Rows: ', len(final_scores))
                insert_in_to_scores(final_scores, Session)
                print('Marking all runs: ', circuit[0], ' Runs: ', len(mark_run))
                #Also find all runs that exceed the high trheshold and mark them for high score dash board
                mark_as_high_dash(circuit[0], mark_run, 1, Session)                     
            circ_count = circ_count + 1    
    except:
        msg = sys.exc_info()
        if msg is not None:
            logger_error(convert_tuple(msg))         
        msg = traceback.print_exc()
        if msg is not None:
            logger_error(convert_tuple(msg))              
        engine.dispose()

# Database health check entry to let health process know the proces is alive
def health_check_in(Session):
    # get or create a process status row
    params = {}
    params['monitor_id'] = SERVER_ID
    params['version'] = VERSION
    params['process'] = 'circuit-score'
    params['last_check_in'] = datetime.datetime.now()
    params['check_in_interval'] = 300

    tsql = """SELECT * FROM monitor_process_status WHERE
    monitor_id = :monitor_id AND process = :process
    LIMIT 1
    """
    STATUS_RECORD = False
    ret = query_text(Session, tsql, params)
    if len(ret) > 0:
        STATUS_RECORD = True


    insert_sql = """INSERT INTO monitor_process_status 
        (monitor_id, version, process, last_check_in, check_in_interval)
        VALUES(:monitor_id, :version, :process, :last_check_in, :check_in_interval)
    """     
    update_sql = """UPDATE monitor_process_status 
        SET version = :version, last_check_in = :last_check_in
        WHERE
        monitor_id = :monitor_id AND process = :process        
    """     
    session = scoped_session(Session)
    session.execute(update_sql if STATUS_RECORD else insert_sql, params)
    session.commit()
    session.close()

logger_info('Starting circuit-score V' + str(VERSION))

def main(): 
    #Default arguements
    uname = 'root'
    password = 'root'
    ipaddr = '127.0.0.1'
    port = "3306"
    db = "dfa_msdb_jun10"
    overall_check_time = 60    

    if len(sys.argv) == 7:
        uname = sys.argv[1] 
        password = sys.argv[2] 
        ipaddr = sys.argv[3] 
        port = sys.argv[4] 
        db = sys.argv[5] 
        overall_check_time = int(sys.argv[6]) 

    #For now, do not alow poll frequency greater than a minute
    if overall_check_time < 60:
        overall_check_time = 60

    
    try:
        #Get teh db connection
        engine, Session = connect_db(uname, password, ipaddr, port, db)
        health_check_in(Session)
        logger_info('Start pre-populating scores')
        #intial population of scores
        pre_populate_scores(engine, Session, first = True)
        logger_info('Done pre-populating scores')
    except:
        logger_error("Failed to connect to database, please check your input parameters")
        msg = traceback.print_exc()
        if msg is not None:
            logger_error(convert_tuple(msg))           
        return
    print(ipaddr, port, db)

    #Loop forever
    while True:
        logger_info('Polling for new records')
        #Populate with new scores
        pre_populate_scores(engine, Session, first = False)
        time.sleep(overall_check_time)
 
    logger_info("--------")


if __name__ == "__main__":
    main()
    logger_info("----end execution----")
