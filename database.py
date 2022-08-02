#!/usr/bin/python
# updated 22 Aug 2018  changes to match Server schema on Monitor table
# Updated Sept 18th, changes to accomodate Hysteresis settttings in triggers 
# Updated Oct 9th, changes to add upper disk limit to monitor table
# Updated May 28th, changes to add vpn/server/device configurations 
# settings to monitor table

from peewee import *

database = MySQLDatabase('dfa_ddb', **{'host': 'localhost', 'password': 'dfa', 'port': 3306, 'user': 'root'})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class bus(BaseModel):
    bus = IntegerField(db_column='bus_id', unique=True)
    description = TextField(null=True)
    name = CharField(null=True)
    phase_to_phase_fault_current = IntegerField(null=True)
    phase_to_phase_to_ground_fault_current = IntegerField(null=True)
    power_rating = IntegerField(null=True)
    primary_connection = IntegerField(db_column='primary_connection_id', null=True)
    primary_voltage = IntegerField(null=True)
    secondary_connection = IntegerField(db_column='secondary_connection_id', null=True)
    secondary_voltage = IntegerField(null=True)
    single_phase_fault_current = IntegerField(null=True)
    substation = IntegerField(db_column='substation_id', index=True)
    three_phase_fault_current = IntegerField(null=True)

    class Meta:
        db_table = 'bus'

class classification_codes(BaseModel):
    bdeleted = IntegerField(null=True)
    classification_code = IntegerField(unique=True)
    description = CharField(null=True)
    icon = IntegerField(db_column='icon_id', null=True)
    mod_time = DateTimeField(null=True)
    mon_priority = IntegerField(null=True)
    non_mon_priority = IntegerField(null=True)
    short_description = CharField(null=True)

    class Meta:
        db_table = 'classification_codes'

class cluster_info(BaseModel):
    cluster = BigIntegerField(db_column='cluster_id')
    mod_time = DateTimeField(index=True)
    monitor = IntegerField(db_column='monitor_id')
    waveform = BigIntegerField(db_column='waveform_id')
    sync = IntegerField()
    id = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'cluster_info'

class confidence_codes(BaseModel):
    confidence_code = IntegerField(unique=True)
    description = CharField(null=True)
    mod_time = DateTimeField(null=True)

    class Meta:
        db_table = 'confidence_codes'

class db_history(BaseModel):
    change_from = CharField()
    change_to = CharField()
    datetime = DateTimeField()
    event = CharField()
    field = CharField()
    guid = CharField()
    id = BigIntegerField(primary_key=True)
    monitor = IntegerField(db_column='monitor_id')
    new = IntegerField()
    row = BigIntegerField(db_column='row_id')
    table = CharField()

    class Meta:
        db_table = 'db_history'

class db_tracking(BaseModel):
    added_time = DateTimeField()
    delay_time = DateTimeField()
    direction = IntegerField()
    history = BigIntegerField(db_column='history_id')
    id = BigIntegerField(primary_key=True)
    master_station = IntegerField(db_column='master_station_id')
    monitor = BigIntegerField(db_column='monitor_id')
    priority = IntegerField()
    status = IntegerField()
    sync_time = DateTimeField()
    type = CharField()

    class Meta:
        db_table = 'db_tracking'

class db_row_mapping(BaseModel):
    id = BigIntegerField(primary_key=True)
    master_station = IntegerField(db_column='master_station_id')
    monitor = IntegerField(db_column='monitor_id')
    monitor_row = BigIntegerField(db_column='monitor_row_id')
    ms_row = BigIntegerField(db_column='ms_row_id')
    table = CharField()

    class Meta:
        db_table = 'db_row_mapping'        

class feature_codes(BaseModel):
    feature_code = IntegerField(unique=True)
    feature_extractor = IntegerField(db_column='feature_extractor_id', null=True)
    feature_name = CharField(null=True)
    feature_value_type = IntegerField(null=True)
    mod_time = DateTimeField(db_column='mod_Time', null=True)

    class Meta:
        db_table = 'feature_codes'

class ground_codes(BaseModel):
    description = CharField(null=True)
    ground_code = IntegerField(unique=True)
    mod_time = DateTimeField(null=True)

    class Meta:
        db_table = 'ground_codes'

class interval_data(BaseModel):
    a_average = FloatField(null=True)
    a_maximum = FloatField(null=True)
    a_minimum = FloatField(null=True)
    a_standard_dev = FloatField(null=True)
    b_average = FloatField(null=True)
    b_maximum = FloatField(null=True)
    b_minimum = FloatField(null=True)
    b_standard_dev = FloatField(null=True)
    c_average = FloatField(null=True)
    c_maximum = FloatField(null=True)
    c_minimum = FloatField(null=True)
    c_standard_dev = FloatField(null=True)
    data_type = IntegerField(db_column='data_type_id')
    mod_time = DateTimeField()
    monitor = IntegerField(db_column='monitor_id', index=True)
    n_average = FloatField(null=True)
    n_maximum = FloatField(null=True)
    n_minimum = FloatField(null=True)
    n_standard_dev = FloatField(null=True)
    stat_record_ndx = IntegerField()

    class Meta:
        db_table = 'interval_data'

class monitor(BaseModel):
    abc_phase_rotation = IntegerField(null=True)
    abc_rotation = IntegerField()
    bus = BigIntegerField(db_column='bus_id', index=True)
    company = BigIntegerField(db_column='company_id')
    connect = IntegerField(null=True)
    daylight_savings = IntegerField(null=True)
    days_interval_data_on_monitor = IntegerField(null=True)
    delta_connected_pts = IntegerField()
    delta_free_space = IntegerField(null=True)
    max_free_space = IntegerField(null=True)
    description = CharField(null=True)
    feeder_ndx = IntegerField(null=True)
    feeder_number = CharField(null=True)
    firmware_version = IntegerField(db_column='firmware_version_id')
    id = BigIntegerField(primary_key=True)
    interval_data_logging_period = CharField(null=True)
    is_downstream_monitor = IntegerField()
    lastalert = IntegerField(db_column='lastAlert')
    last_check_in = DateTimeField(null=True)
    last_connect = DateTimeField(null=True)
    last_data_stat_record_ndx = IntegerField(null=True)
    last_event_sync_time = DateTimeField(null=True)
    last_modified_by = IntegerField()
    last_modified_time = DateTimeField(null=True)
    last_rec_stat_record_ndx = IntegerField(null=True)
    last_settings_sync_time = DateTimeField(null=True)
    last_stat_sync_time = DateTimeField(null=True)
    last_sync_time = DateTimeField(null=True)
    last_tees_table_sync_time = DateTimeField(null=True)
    last_waveform_sync_time = DateTimeField(null=True)
    location_info = CharField(null=True)
    location_type = CharField(null=True)
    master_monitor = BigIntegerField(db_column='master_monitor_id', null=True)
    maximum_single_waveform_file_length = IntegerField(null=True)
    monitor = BigIntegerField(db_column='monitor_id', unique=True)
    name = CharField(null=True)
    ntp_server = CharField()
    phase_a_ct_present = IntegerField()
    phase_b_ct_present = IntegerField()
    phase_c_ct_present = IntegerField()
    phase_n_ct_present = IntegerField()
    post_trigger_recording_duration = IntegerField(null=True)
    pre_trigger_recording_duration = IntegerField(null=True)
    pts_connected_delta = IntegerField(null=True)
    revision_group = CharField(null=True)
    serial_number = CharField(null=True)
    substation = BigIntegerField(db_column='substation_id', index=True)
    sync_time_to = CharField()
    time_threshold_before_new_trigger = IntegerField(null=True)
    time_zone = CharField(null=True)
    upstream_monitor = BigIntegerField()
    upstream_monitor_id = BigIntegerField(null=True)
    uuid = CharField()
    voltage_a_pt_present = IntegerField()
    voltage_b_pt_present = IntegerField()
    voltage_c_pt_present = IntegerField()
    waveform_free_space_to_maintain = IntegerField(null=True)
    last_interval = DateTimeField(null=True)
    unit_type = CharField()
    sync_key = TextField(null=True)
    pt_primary_a = DoubleField(default=1)
    pt_primary_b = DoubleField(default=1)
    pt_primary_c = DoubleField(default=1)
    pt_secondary_a = DoubleField(default=1)
    pt_secondary_b = DoubleField(default=1)
    pt_secondary_c = DoubleField(default=1)
    ct_primary_a = DoubleField(default=1)
    ct_primary_b = DoubleField(default=1)
    ct_primary_c = DoubleField(default=1)
    ct_secondary_a = DoubleField(default=1)
    ct_secondary_b = DoubleField(default=1)
    ct_secondary_c = DoubleField(default=1)

    max_sync_rows                   = IntegerField(default=100)
    master_station_server           = CharField(default='dfa-proxy.tamu.edu')
    master_station_port             = IntegerField(default=45123)
    master_station_file_server      = CharField(default='dfa-proxy.tamu.edu')
    master_station_file_server_port = IntegerField(default=45124)
    command_server                  = CharField(default='dfa-proxy.tamu.edu')
    command_server_port             = IntegerField(default=45125)
    command_server_poll_interval    = IntegerField(default=60)
    secondary_ms_server             = CharField(null=True)
    secondary_ms_port               = IntegerField(null=True)
    tertiary_ms_server              = CharField(null=True)
    tertiary_ms_port                = IntegerField(null=True)
    primary_ms_enabled              = IntegerField(default=1)
    secondary_ms_enabled            = IntegerField(default=0)
    tertiary_ms_enabled             = IntegerField(default=0)
    time_sync_server                = CharField(default='NTP')

    aib_os                   = CharField()
    system_frequency         = CharField()
    metered_connection       = CharField()
    algorithms_enabled       = IntegerField(default=1)
    router_address           = CharField(default='10.245.245.1')
    aib_address              = CharField(default='10.245.245.2')
    high_accuracy_timestamp  = IntegerField(default=0)
    mac_address              = CharField()


    ipsec_server                = CharField(default='dfa.tamu.edu')
    open_vpn_server             = CharField(default='dfa.tamu.edu')
    open_vpn_port               = IntegerField(default=1194)
    vpn_certificate             = TextField(null=True)
    vpn_key                     = TextField(null=True)
    wiregaurd_server            = CharField(null=True)
    wiregaurd_port              = IntegerField(null=True)
    wiregaurd_private_key       = TextField(null=True)
    wiregaurd_server_key        = TextField(null=True)
    vpn_enabled                 = CharField()
    route_all_through_open_vpn  = IntegerField(default=0)

    class Meta:
        db_table = 'monitor'
        
class monitor_health_db(BaseModel):
    datetime = DateTimeField(null=True)
    id = BigIntegerField(primary_key=True)
    monitor = BigIntegerField(db_column='monitor_id', index=True)
    monitor_row_count = BigIntegerField()
    ms_row_count = BigIntegerField()
    table = CharField(index=True)

    class Meta:
        db_table = 'monitor_health_db'

class monitor_firmware_versions(BaseModel):
    available = IntegerField()
    guid = CharField(unique=True)
    release_date = DateTimeField()
    id = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'monitor_firmware_versions'

class monitor_health_events(BaseModel):
    action = CharField()
    datetime = DateTimeField()
    emailsent = IntegerField(db_column='emailSent')
    event_type = CharField()
    monitor = IntegerField(db_column='monitor_id')
    process = CharField()
    id = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'monitor_health_events'

class monitor_health_resources(BaseModel):
    aib_temp_1 = CharField(null=True)
    aib_temp_2 = CharField(null=True)
    aib_temp_3 = CharField(null=True)
    cpu0 = CharField(null=True)
    cpu0_frequency = CharField(null=True)
    cpu0_temp = CharField()
    cpu1 = CharField(null=True)
    cpu1_frequency = CharField(null=True)
    cpu1_temp = CharField()
    cpu2 = CharField(null=True)
    cpu2_frequency = CharField(null=True)
    cpu2_temp = CharField()
    cpu3 = CharField(null=True)
    cpu3_frequency = CharField(null=True)
    cpu3_temp = CharField()
    cpu_temp_avg = CharField()
    cpu_total = CharField()
    disk = CharField()
    mem = CharField()
    monitor = IntegerField(db_column='monitor_id')
    time = DateTimeField()
    id = BigIntegerField(primary_key=True)
    net_hour_rx = CharField(null=True)
    net_hour_tx = CharField(null=True)
    net_today_rx = CharField(null=True)
    net_today_tx = CharField(null=True)
    net_yesterday_rx = CharField(null=True)
    net_yesterday_tx = CharField(null=True)
    net_month_rx = CharField(null=True)
    net_month_tx = CharField(null=True)
    ip_addr = CharField(null=True)

    class Meta:
        db_table = 'monitor_health_resources'


class monitor_process_status(BaseModel):
    last_check_in = DateTimeField()
    monitor = BigIntegerField(db_column='monitor_id')
    process = CharField()
    version = CharField()
    build_date = CharField(null=True)
    last_normal_start = DateTimeField()
    last_restart = DateTimeField()
    check_in_interval = IntegerField()

    class Meta:
        db_table = 'monitor_process_status'


class monitor_trigger(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = CharField(unique=True)
    display_name = CharField()
    type = CharField()
    ordering = BigIntegerField(index=True)

    class Meta:
        db_table = 'monitor_trigger'


class monitor_trigger_settings(BaseModel):
    id = BigIntegerField(primary_key=True)
    monitor_id = BigIntegerField(index=True)
    trigger_name = CharField(max_length=256, index=True)
    phase = FixedCharField(max_length=1)
    abs_min = CharField(max_length=256)
    abs_max = CharField(max_length=256)
    multi_min = CharField(max_length=256)
    multi_max = CharField(max_length=256)
    noise_floor = CharField(max_length=256)
    hysteresis  = CharField(max_length=256)
    time_max  = CharField(max_length=256)
    time_min  = CharField(max_length=256)

    class Meta:
        db_table = 'monitor_trigger_settings'
        indexes = (
            (('monitor_id', 'trigger_name', 'phase'), True),
        )


class monitor_commands(BaseModel):
    command = CharField(null=True)
    id = BigIntegerField(primary_key=True)
    issed_by = IntegerField(index=True, null=True)
    monitor = BigIntegerField(db_column='monitor_id', index=True, null=True)
    results = TextField(null=True)
    status = CharField(null=True)
    time_received = DateTimeField(null=True)
    time_sent = DateTimeField(null=True)

    class Meta:
        db_table = 'monitor_commands'         

class phase_codes(BaseModel):
    description = TextField(null=True)
    mod_time = DateTimeField()
    name = CharField(null=True, unique=True)

    class Meta:
        db_table = 'phase_codes'

class position_codes(BaseModel):
    description = CharField()
    mod_time = DateTimeField()
    name = CharField(null=True)

    class Meta:
        db_table = 'position_codes'

class problem_codes(BaseModel):
    description = TextField(null=True)
    mod_time = DateTimeField()
    name = CharField(null=True)
    problem_code = IntegerField(unique=True)

    class Meta:
        db_table = 'problem_codes'


class queue(BaseModel):
    id = BigIntegerField(primary_key=True)
    user_id = BigIntegerField(null=True)
    job_type = CharField(max_length=30, index=True)
    data = TextField(null=True)
    state = CharField(max_length=14, default='Pending', index=True)
    added_date = DateTimeField()
    release_time = DateTimeField()
    expires_time = DateTimeField(index=True)

    class Meta:
        db_table = 'queue'
        indexes = (
            (('job_type', 'state'), False),
            (('user_id', 'job_type'), False)
        )


class report_features(BaseModel):
    cluster = IntegerField(db_column='cluster_id')
    feature_code = IntegerField()
    feature_info = CharField(null=True)
    feature_valid = IntegerField(null=True)
    feature_value_a = FloatField(null=True)
    feature_value_b = FloatField(null=True)
    feature_value_c = FloatField(null=True)
    mod_time = DateTimeField(index=True)
    monitor = IntegerField(db_column='monitor_id')
    id = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'report_features'

class report_line_item(BaseModel):
    being_synced = IntegerField()
    cluster = IntegerField(db_column='cluster_id')
    first_seen = DateTimeField(null=True)
    gen_location = IntegerField(null=True)
    ground_code = IntegerField(null=True)
    last_seen = DateTimeField(index=True, null=True)
    look_back_window = IntegerField(null=True)
    mod_time = DateTimeField(index=True)
    monitor = IntegerField(db_column='monitor_id')
    phase_code = IntegerField(null=True)
    problem_code = IntegerField(null=True)
    rli_flags = IntegerField(null=True)
    processed = IntegerField(null=True)
    id = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'report_line_item'

class substation(BaseModel):
    address = IntegerField(db_column='address_id', index=True, null=True)
    company = IntegerField(db_column='company_id', index=True, null=True)
    description = TextField(null=True)
    name = CharField(null=True)
    substation = IntegerField(db_column='substation_id', unique=True)

    class Meta:
        db_table = 'substation'

class waveform_classifications(BaseModel):
    classification_code = IntegerField()
    confidence_code = IntegerField()
    deleted_on_feeder = IntegerField()
    eq_circuit = IntegerField(db_column='eq_circuit_id')
    ground_code = IntegerField()
    ignore = IntegerField()
    mod_time = DateTimeField()
    monitor = IntegerField(db_column='monitor_id')
    needs_to_be_written = IntegerField()
    oc_device_code = IntegerField()
    phase_code = IntegerField()
    position_code = IntegerField()
    user_comments = TextField(null=True)
    user = IntegerField(db_column='user_id')
    waveform = IntegerField(db_column='waveform_id')
    sync = IntegerField()
    flag_code = IntegerField(null=True)
    id = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'waveform_classifications'

class waveform_features(BaseModel):
    feature_code = IntegerField(null=True)
    feature_info = CharField(null=True)
    feature_valid = IntegerField(null=True)
    feature_value_a = FloatField(null=True)
    feature_value_b = FloatField(null=True)
    feature_value_c = FloatField(null=True)
    mod_time = DateTimeField()
    monitor = IntegerField(db_column='monitor_id')
    sub_event = IntegerField(db_column='sub_event_id')
    waveform = BigIntegerField(db_column='waveform_id')
    sync = IntegerField()
    id = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'waveform_features'

class waveform_records(BaseModel):
    archival = IntegerField(null=True)
    confidence_code = IntegerField(null=True)
    data_reduced = IntegerField()
    deleted_on_circuit_monitor = IntegerField()
    file_name = CharField(null=True)
    icon = IntegerField(null=True)
    investigation = IntegerField()
    major_event = IntegerField()
    mod_time = DateTimeField(index=True)
    monitor = IntegerField(db_column='monitor_id', null=True)
    outage = IntegerField()
    priority = IntegerField(null=True)
    process_control_code = IntegerField(null=True)
    record_time = DateTimeField()
    trigger_phase = CharField()
    trigger_type_code = IntegerField(null=True)
    watch_list = IntegerField()
    waveform_file_transferred = IntegerField()
    waveform = BigIntegerField(db_column='waveform_id')
    waveform_written = IntegerField()
    id = BigIntegerField(primary_key=True)
    crc = CharField()
    crc_pass = IntegerField()

    class Meta:
        db_table = 'waveform_records'

database.connect()
 