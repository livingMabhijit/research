import mysql.connector
import numpy as np

import tensorflow as tf
from tensorflow import keras
import sqlite3
import sys
import os
import shutil
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import time

from enum import IntEnum


class Indx(IntEnum):
    ID = 0
    MONITOR = 1
    RECORD = 2
    FILE = 3
    CLASS = 4
    POSITION = 5
    PHASE = 6
    GROUND = 7
    FREQ = 8
    SECONDS = 9
    BLOB = 10

class SIndx(IntEnum):
    ID = 0
    NAME = 1
    PT_S_A = 2
    PT_S_B = 3
    PT_S_C = 4
    PT_P_A = 5
    PT_P_B = 6
    PT_P_C = 7
    CT_S_A = 8
    CT_S_B = 9
    CT_S_C = 10
    CT_P_A = 11
    CT_P_B = 12
    CT_P_C = 13
    VA_SCALE = 14
    VB_SCALE = 15
    VC_SCALE = 16
    IA_SCALE = 17
    IB_SCALE = 18
    IC_SCALE = 19
    PQ_SCALE = 99
    NO_SCALE = 100

class Channels(IntEnum):
    VA    =    0
    VB    =    1
    VC    =    2
    IA    =    3
    IB    =    4
    IC    =    5
    IN    =    6
    VA_PD =    7
    VB_PD =    8
    VC_PD =    9
    IA_PD =    10
    IB_PD =    11
    IC_PD =    12
    IN_PD =    13
    PA =       14
    PB =       15
    PC =       16
    QA =       17
    QB =       18
    QC =       19
    VA_SD =    20
    VB_SD =    21
    VC_SD =    22
    IA_SD =    23
    IB_SD =    24
    IC_SD =    25
    IN_SD =    26
    VA_EVENS = 27
    VB_EVENS = 28
    VC_EVENS = 29
    IA_EVENS = 30
    IB_EVENS = 31
    IC_EVENS = 32
    IN_EVENS = 33
    VA_ODDS =  34
    VB_ODDS =  35
    VC_ODDS =  36
    IA_ODDS =  37
    IB_ODDS =  38
    IC_ODDS =  39
    IN_ODDS =  40

def get_scale_lookup(filename = 'D:\\Downloads\\dfa_ml_scaling.csv'):
    return dict((rows[0], rows) for rows in [tuple(x) for x in pd.read_csv(filename, delimiter=',').values])

def get_scaled_vector(records_in, record_indx = 0, channel=Channels.IA, scale_indx = SIndx.IA_SCALE):
    arr = np.frombuffer(records_in[record_indx][-1], dtype=np.float32)
    if scale_indx == SIndx.NO_SCALE:
        scale = 1
    elif scale_indx == SIndx.PQ_SCALE:
        scale = scale_look_up[records_in[record_indx][1]][SIndx.IA_SCALE]*\
                scale_look_up[records_in[record_indx][1]][SIndx.VA_SCALE]
    else:
        scale = scale_look_up[records_in[record_indx][1]][scale_indx]
    len = records_in[record_indx][Indx.SECONDS] * records_in[record_indx][Indx.FREQ]
    vect = scale*arr[(len*channel):(len*(channel + 1))]
    return vect


def get_records(limit=1000, clause = ""):
    connection = mysql.connector.connect(host='10.72.1.100',
                                         database='dfa_ml',
                                         user='proxy',
                                         password='proxy',
                                         use_pure=True)
    cursor = connection.cursor()
    sql_fetch_blob_query = "SELECT * FROM dfa_ml.dfa_ml_data_records " + \
                           "where monitor_id  NOT IN (110003001002, 100001001001, 100002001001, 100002002001, 100002002002, 101001001001, 101002001001, 101002001002, 101002001003, 110002001002) and " +\
                           "monitor_id > 100000000000  and " + \
                           "monitor_id NOT IN (110001001001) and " +\
                           "duration_seconds >9 and duration_seconds < 30 " +\
                            clause +\
                           " limit  " \
                           + str(limit)
    cursor.execute(sql_fetch_blob_query)
    records = cursor.fetchall()
    #arr = np.frombuffer(records[0][0], dtype=np.float32)
    return records

def get_sqlite_records_generic(file_name,clause = ""):
    connection =  sqlite3.connect(file_name)
    rows = connection.execute(clause)
    records = rows.fetchall()
    connection.close()
    return records

def get_sqlite_records(file_name="main", limit=1000, clause = ""):
    connection =  sqlite3.connect("D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_4.sqlite")
    cur = connection.cursor()
    # cur.execute("ATTACH DATABASE 'D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_5.sqlite' AS dfa_ml_5")
    # cur.execute("ATTACH DATABASE 'D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_6.sqlite' AS dfa_ml_6")
    #Column order is different than mysql, so need to enumerate field in crrect order
    sql_fetch_blob_query_old = "SELECT id, monitor_id, waveform_id, file_name, classification_code, position_code, phase_code, ground_code, powerline_frequency, duration_seconds, rms_data FROM dfa_ml_data_records " + \
                           "where monitor_id  NOT IN (110003001002, 100001001001, 100002001001, 100002002001, 100002002002, 101001001001, 101002001001, 101002001002, 101002001003, 110002001002) and " +\
                           "monitor_id > 100000000000  and " + \
                           "monitor_id NOT IN (110001001001) and " +\
                           "duration_seconds >9 and duration_seconds < 30 " +\
                            clause +\
                           " limit  " \
                           + str(limit)

    sql_fetch_blob_query = "SELECT id, monitor_id, waveform_id, file_name, classification_code, position_code, phase_code, ground_code, powerline_frequency, duration_seconds, rms_data FROM dfa_ml_data_records, " + \
                           "(select max(waveform_id) as wav, max(monitor_id) as mon  FROM dfa_ml_data_records " + \
                           "where monitor_id  NOT IN (110003001002, 100001001001, 100002001001, 100002002001, 100002002002, 101001001001, 101002001001, 101002001002, 101002001003, 110002001002) and " + \
                           "monitor_id > 100000000000  and " + \
                           "monitor_id NOT IN (110001001001) and " + \
                           "duration_seconds >9 and duration_seconds < 30 " + \
                           "group by waveform_id, monitor_id " + \
                           "having count(waveform_id) = 1 " +\
                            clause + ") as der " + \
                           "where waveform_id = wav and monitor_id = mon limit " +\
                            str(limit)
    common_select = "select waveform_id, monitor_id, classification_code, position_code "
    common_where = """where monitor_id  NOT IN (110003001002, 100001001001, 100002001001, 100002002001, 100002002002, 101001001001, 101002001001, 101002001002, 101002001003, 110002001002) and 
                       monitor_id > 100000000000  and
                       monitor_id NOT IN (110001001001) and
                       duration_seconds >9 and duration_seconds < 30 """
    sql_fetch_blob_query = """SELECT id, monitor_id, waveform_id, file_name, classification_code, position_code, phase_code, ground_code, powerline_frequency, duration_seconds, rms_data  
                            from """ + file_name + """.dfa_ml_data_records,
                            (select  max(waveform_id) as wav, max(monitor_id) as mon from
                            (""" + \
                             common_select + \
                             "FROM dfa_ml_data_records " +\
                             common_where + \
                               "UNION " + \
                             common_select + \
                             "FROM dfa_ml_5.dfa_ml_data_records " +\
                             common_where + \
                               "UNION " + \
                             common_select + \
                             "FROM dfa_ml_6.dfa_ml_data_records " + \
                            """)
                            group  by waveform_id, monitor_id
                            having count(waveform_id) = 1 """ + \
                            clause + ") as der " + \
                           "where waveform_id = wav and monitor_id = mon limit " +\
                            str(limit)


    rows = cur.execute(sql_fetch_blob_query)
    records = rows.fetchall()
    cur.execute("DETACH DATABASE dfa_ml_5")
    cur.execute("DETACH DATABASE dfa_ml_6")
    connection.close()
    return records

def get_sqlite_records_ce5(file_name="main", limit=1000, clause = ""):
    connection =  sqlite3.connect("D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_1.sqlite")
    cur = connection.cursor()
    cur.execute("ATTACH DATABASE 'D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_2.sqlite' AS dfa_ml_2")
    cur.execute("ATTACH DATABASE 'D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_3.sqlite' AS dfa_ml_3")
    #Column order is different than mysql, so need to enumerate field in crrect order
    sql_fetch_blob_query_old = "SELECT id, monitor_id, waveform_id, file_name, classification_code, position_code, phase_code, ground_code, powerline_frequency, duration_seconds, rms_data FROM dfa_ml_data_records " + \
                           "where monitor_id  NOT IN (110003001002, 100001001001, 100002001001, 100002002001, 100002002002, 101001001001, 101002001001, 101002001002, 101002001003, 110002001002) and " +\
                           "monitor_id > 100000000000  and " + \
                           "monitor_id NOT IN (110001001001) and " +\
                           "duration_seconds >9 and duration_seconds < 30 " +\
                            clause +\
                           " limit  " \
                           + str(limit)

    sql_fetch_blob_query = "SELECT id, monitor_id, waveform_id, file_name, classification_code, position_code, phase_code, ground_code, powerline_frequency, duration_seconds, rms_data FROM dfa_ml_data_records, " + \
                           "(select max(waveform_id) as wav, max(monitor_id) as mon  FROM dfa_ml_data_records " + \
                           "where monitor_id  NOT IN (110003001002, 100001001001, 100002001001, 100002002001, 100002002002, 101001001001, 101002001001, 101002001002, 101002001003, 110002001002) and " + \
                           "monitor_id > 100000000000  and " + \
                           "monitor_id NOT IN (110001001001) and " + \
                           "duration_seconds >9 and duration_seconds < 30 " + \
                           "group by waveform_id, monitor_id " + \
                           "having count(waveform_id) = 1 " +\
                            clause + ") as der " + \
                           "where waveform_id = wav and monitor_id = mon limit " +\
                            str(limit)
    common_select = "select waveform_id, monitor_id, classification_code, position_code "
    common_where = """where
                       duration_seconds >9 and duration_seconds < 30 """
    sql_fetch_blob_query = """SELECT id, monitor_id, waveform_id, file_name, classification_code, position_code, phase_code, ground_code, powerline_frequency, duration_seconds, rms_data  
                            from """ + file_name + """.dfa_ml_data_records,
                            (select  max(waveform_id) as wav, max(monitor_id) as mon from
                            (""" + \
                             common_select + \
                             "FROM dfa_ml_data_records " +\
                             common_where + \
                               "UNION " + \
                             common_select + \
                             "FROM dfa_ml_2.dfa_ml_data_records " +\
                             common_where + \
                               "UNION " + \
                             common_select + \
                             "FROM dfa_ml_3.dfa_ml_data_records " + \
                            """)
                            group  by waveform_id, monitor_id
                            having count(waveform_id) = 1 """ + \
                            clause + ") as der " + \
                           "where waveform_id = wav and monitor_id = mon limit " +\
                            str(limit)


    rows = cur.execute(sql_fetch_blob_query)
    records = rows.fetchall()
    cur.execute("DETACH DATABASE dfa_ml_2")
    cur.execute("DETACH DATABASE dfa_ml_3")
    connection.close()
    return records

def fetch_and_plot_PQ(in_records, in_indx=0, is_scale=True):
    if is_scale:
        scale= SIndx.PQ_SCALE
    else:
        scale = SIndx.NO_SCALE
    ia = get_scaled_vector(in_records, in_indx, channel=Channels.QA, scale_indx=scale)
    ib = get_scaled_vector(in_records, in_indx, channel=Channels.QB, scale_indx=scale)
    ic = get_scaled_vector(in_records, in_indx, channel=Channels.QC, scale_indx=scale)
    plt.plot(ia), plt.plot(ib), plt.plot(ic), plt.show()
    ia = get_scaled_vector(in_records, in_indx, channel=Channels.PA, scale_indx=scale)
    ib = get_scaled_vector(in_records, in_indx, channel=Channels.PB, scale_indx=scale)
    ic = get_scaled_vector(in_records, in_indx, channel=Channels.PC, scale_indx=scale)
    plt.plot(ia), plt.plot(ib), plt.plot(ic), plt.show()

def fetch_and_plot_VI(in_records, in_indx=0, is_scale=True):
    if is_scale:
        scale_i= SIndx.IA_SCALE
        scale_v = SIndx.VA_SCALE
    else:
        scale_i = SIndx.NO_SCALE
        scale_v = SIndx.NO_SCALE
    ia = get_scaled_vector(in_records, in_indx, channel=Channels.VA, scale_indx=scale_v)
    ib = get_scaled_vector(in_records, in_indx, channel=Channels.VB, scale_indx=scale_v)
    ic = get_scaled_vector(in_records, in_indx, channel=Channels.VC, scale_indx=scale_v)
    plt.plot(ia), plt.plot(ib), plt.plot(ic), plt.show()
    ia = get_scaled_vector(in_records, in_indx, channel=Channels.IA, scale_indx=scale_i)
    ib = get_scaled_vector(in_records, in_indx, channel=Channels.IB, scale_indx=scale_i)
    ic = get_scaled_vector(in_records, in_indx, channel=Channels.IC, scale_indx=scale_i)
    plt.plot(ia), plt.plot(ib), plt.plot(ic), plt.show()

def print_progress(count, total):
    # Percentage completion.
    pct_complete = float(count) / total

    # Status-message.
    # Note the \r which means the line should overwrite itself.
    msg = "\r- Progress: {0:.1%}".format(pct_complete)

    # Print it.
    sys.stdout.write(msg)
    sys.stdout.flush()

# Helper-function for wrapping an integer so it can be saved to the TFRecord file.
def wrap_int64(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

# Helper-function for wrapping raw bytes so they can be saved to the TFRecord file.
def wrap_blob(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[bytes(value)]))

# Helper-function for wrapping raw bytes so they can be saved to the TFRecord file.
def wrap_string(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value.encode('utf-8')]))

def convert(dfa_records, out_path, duration=6):
    # Args:
    # image_paths   List of file-paths for the images.
    # labels        Class-labels for the images.
    # out_path      File-path for the TFRecords output file.
    print("Converting: " + out_path)
    # Number of images. Used when printing the progress.
    num_records = len(dfa_records)
    # Open a TFRecordWriter for the output-file.
    with tf.python_io.TFRecordWriter(out_path) as writer:
        # Iterate over all the image-paths and class-labels.
        for ii, rec in enumerate(dfa_records):
            # Print the percentage-progress.
            print_progress(count=ii, total=num_records-1)
            data = \
                {
                    'waveform': wrap_blob(rec[Indx.BLOB]),
                    'class': wrap_int64(rec[Indx.CLASS]),
                    'position': wrap_int64(rec[Indx.POSITON]),
                    'phase': wrap_int64(rec[Indx.PHASE]),
                    'ground': wrap_int64(rec[Indx.GROUND]),
                    'duration': wrap_int64(rec[Indx.SECONDS]),
                    'frequency': wrap_int64(rec[Indx.FREQ]),
                    'id': wrap_int64(rec[Indx.ID]),
                    'monitor_id': wrap_int64(rec[Indx.MONITOR]),
                    'waveform_id': wrap_int64(rec[Indx.RECORD]),
                    'file_name': wrap_string(rec[Indx.FILE])
                }
            # Wrap the data as TensorFlow Features.
            feature = tf.train.Features(feature=data)
            # Wrap again as a TensorFlow Example.
            example = tf.train.Example(features=feature)
            # Serialize the data.
            serialized = example.SerializeToString()
            # Write the serialized data to the TFRecords file.
            writer.write(serialized)

def dfa_records_input_fn(filenames, perform_shuffle=False, repeat_count=1, batch_size=1):
    def _parse_function(serialized):
        features = \
            {
                'waveform':tf.FixedLenFeature([], tf.string),
                'class': tf.FixedLenFeature([], tf.int64),
                'position': tf.FixedLenFeature([], tf.int64),
                'phase':tf.FixedLenFeature([], tf.int64),
                'ground': tf.FixedLenFeature([], tf.int64),
                'duration': tf.FixedLenFeature([], tf.int64),
                'frequency': tf.FixedLenFeature([], tf.int64),
                'id': tf.FixedLenFeature([], tf.int64),
                'monitor_id':tf.FixedLenFeature([], tf.int64),
                'waveform_id': tf.FixedLenFeature([], tf.int64),
                'file_name': tf.FixedLenFeature([], tf.string)
            }
        # Parse the serialized data so we get a dict with our data.
        parsed_example = tf.parse_single_example(serialized=serialized,
                                                 features=features)

        waveform_raw = parsed_example['waveform']
        # Decode the raw bytes so it becomes a tensor with type.
        waveform = tf.decode_raw(waveform_raw, tf.float32)
        #waveform = tf.cast(waveform, tf.float32)

        label = tf.cast(parsed_example['class'], tf.int64)
        d = dict(zip(['test_layer'], [waveform])), [label]
        return d
    dataset = tf.data.TFRecordDataset(filenames=filenames)
    # Parse the serialized data in the TFRecords files.
    # This returns TensorFlow tensors for the image and labels.
    dataset = dataset.map(_parse_function)
    if perform_shuffle:
        # Randomizes input using a window of 256 elements (read into memory)
        dataset = dataset.shuffle(buffer_size=256)
    dataset = dataset.repeat(repeat_count)  # Repeats dataset this # times
    dataset = dataset.batch(batch_size)  # Batch size to use
    iterator = dataset.make_one_shot_iterator()
    batch_features, batch_labels = iterator.get_next()
    return batch_features, batch_labels



next_batch = dfa_records_input_fn("D:/Downloads/Test_Dfa.tfrecords", perform_shuffle=False, batch_size=1)
with tf.Session() as sess:
    first_batch = sess.run(next_batch)
x_d = first_batch[0]['test_layer']

print(x_d.shape)






conn = sqlite3.connect("D:\\Downloads\\test_sqlite_db")
row = conn.execute('SELECT rms_data from dfa_ml_data_records where id = 1')
record = row.fetchall()
arr = np.frombuffer(record[0][0], dtype=np.float32)

import time

start = time.time()
records = get_records()
end = time.time()
print(end - start)

start = time.time()
records_oc = get_records(clause=" and classification_code=15110 and position_code=0 ")
end = time.time()
print(end - start)


start = time.time()
records_cap = get_records(clause=" and classification_code=10110 and position_code=0 ")
end = time.time()
print(end - start)


start = time.time()
records_motors = records_cap = get_records(clause=" and classification_code=12110 and position_code=0 ")
end = time.time()
print(end - start)

start = time.time()
sl_records_oc = get_sqlite_records("D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_6.sqlite", clause=" and min(classification_code) = 15110 and min(position_code=0) ")
end = time.time()
print(end - start)

start = time.time()
sl_records_motors = get_sqlite_records("D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_5.sqlite", clause=" and classification_code=12110 and position_code=0 ")
end = time.time()
print(end - start)

start = time.time()
sl_records_cap = get_sqlite_records("D:\\data\\dfa\\dfa_ml_sqlite\\dfa_ml_5.sqlite", clause=" and classification_code=10110 and position_code=0 ")
end = time.time()
print(end - start)
