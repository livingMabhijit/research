#!/usr/bin/python3

#usage
#./circuit_score.py proxy proxy 10.0.100.50 3306 dfa_msdb 60

import sys, traceback, os, time, datetime, json
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
import pymysql

#g_lookback = 2*365*24*3600  #Two years
g_lookback = 2*30*24*3600  #Two months




def str_time_from_int(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(t)))

def int_time_from_str(strTime):
    if len(strTime) == 19:
        return time.mktime(time.strptime(strTime, '%Y-%m-%d %H:%M:%S'))
    elif len(strTime) == 10:
        return time.mktime(time.strptime(strTime, '%Y-%m-%d'))
    return time.mktime(time.gmtime())


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

def query_text(Session, tsql, param=None):
    session = scoped_session(Session)
    if param != None:
        ret = session.execute(tsql, param).fetchall()
    else:
        ret = session.execute(tsql).fetchall()
    session.close()
    return ret

def get_new_circuits(Session):
    param = {}
    look_back = int_time_from_str('') - g_lookback
    tsql = """ SELECT monitor_id from monitor WHERE 
            monitor_id NOT IN (select DISTINCT monitor_id from circuit_score_last_update) AND
            last_interval > FROM_UNIXTIME(:lookback)
    """
    param['lookback'] = look_back
    return query_text(Session, tsql, param)

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

def get_prev_hrs(Session, mid, unix_hr):
    param = {}
    param['monitor_id'] = mid
    param['time1'] = unix_hr - 3600
    param['time2'] = unix_hr - 3600*2
    tsql = """SELECT MAX(unix_time_hr) AS unix_time, MAX(score)
    FROM circuit_score
    WHERE monitor_id = :monitor_id
    AND (unix_time_hr = :time1 OR unix_time_hr = :time2)
    GROUP BY unix_time_hr
    ORDER BY unix_time DESC
    """
    return query_text(Session, tsql, param)

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


def get_base_circuit_scores(Session, monitor_id, lookback):
    param = {}
    if lookback is None:
        param['etime'] = int_time_from_str('') 
        param['stime'] = param['etime'] - g_lookback
    else:
        param['etime'] = int_time_from_str('') 
        param['stime'] = param['etime'] + 1

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
        HAVING value > 4
        ORDER BY score.rec_time"""
    ret = query_text(Session, tsql, param)
    return ret


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

def insert_in_to_scores(final_scores, Session):
    insert_sql = """INSERT INTO circuit_score 
     (monitor_id, score, score_time, unix_time_hr)
     VALUES(:monitor_id, :score, :score_time, :unix_time_hr)
    """ 
    first = True
    for score in final_scores:
        session = scoped_session(Session)
        session.execute(insert_sql, score)
        session.execute(get_insert_into_scores_update(score, first), score)
        session.commit()
        session.close()
        first = False

def pre_populate_scores(engine, Session, first):
    try:
        if first:
            circuits = get_new_circuits(Session)
        else:
            circuits = get_circuits_with_activity(Session)
        circ_count = 1
        for circuit in circuits:
            print('In circuit: ', circuit[0], ' Circuit ', circ_count, ' of ', len(circuits) )
            base_scores = get_base_circuit_scores(Session, circuit[0], None if first  else circuit[1])
            print('Rows: ', len(base_scores))
            final_scores = []
            count = 1
            score_n_1 = 0
            score_n_2 = 0        
            time_1 = 0
            time_2 = 0    
            if len(base_scores) and not first:
                prev_hrs = get_prev_hrs(Session, circuit[0], base_scores[0][2]) 
                if len(prev_hrs) == 2:
                    score_n_1 = prev_hrs[0][1]
                    score_n_2 = prev_hrs[1][1]
                    time_1 = prev_hrs[0][1]
                    time_2 = prev_hrs[1][1]
                elif len(prev_hrs) == 1:
                    if prev_hrs[0][0] == (base_scores[0][2] - 3600):
                        score_n_1 = prev_hrs[0][1]
                        time_1 = prev_hrs[0][1]
                    else:
                        score_n_2 = prev_hrs[0][1]
                        time_2 = prev_hrs[1][1]
            final_scores = []
            for score in base_scores:
                if time_1 != (score[2] - 3600):
                    score_n_1 = 0
                if time_2 != (score[2] - 2*3600):
                    score_n_2 = 0                    
                score_n = score[3] + 0.5*score_n_1 + 0.25*score_n_2
                score_n = score_n if score_n > 10 else 0
                score_n_2 = score_n_1
                score_n_1 = score_n

                time_2 = time_1                
                time_1 = score[2]

                if score_n > 0:
                    final_scores.append(
                        {
                            'monitor_id':circuit[0],
                            'score': score_n,
                            'score_time': score[0],
                            'unix_time_hr': score[2]
                        }
                    )
            if len(base_scores) < 1:
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
            else:
                print('Inserting scores for circuit: ', circuit[0], ' Rows: ', len(final_scores))
                insert_in_to_scores(final_scores, Session)                   
            circ_count = circ_count + 1    
    except:
        print(sys.exc_info())
        print(traceback.print_exc())
        engine.dispose()

def main(): 
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

    # protect from error input
    if overall_check_time < 60:
        overall_check_time = 60

    
    try:
        engine, Session = connect_db(uname, password, ipaddr, port, db)
        pre_populate_scores(engine, Session, first = True)


    except:
        print("Failed to connect to database, please check your input parameters")
        print(traceback.print_exc()) 
        
        return

    print(ipaddr, port, db)


    while True:
        pre_populate_scores(engine, Session, first = False)
        time.sleep(overall_check_time)
 

    print("--------")


if __name__ == "__main__":
    main()
    print("----end execution----")
