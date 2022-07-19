/*
-- Query: SELECT 
-- UNIX_TIMESTAMP(score.rec_time) DIV 3600 * 3600 as time, 
    TIMESTAMP(DATE_FORMAT(score.rec_time,'%Y-%m-%d %H:00:00'))  as 'time',
    CONCAT(substation.name,
            ' ',
            monitor.feeder_number) AS metric,
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
    monitor,
    substation,
    (SELECT 
        waveform_records.monitor_id AS mid,
            record_time AS rec_time,
            SUM(IF(classification_code IN (23100 , 23104, 23102, 23180, 23190), 1, 0)) AS arc_score,
            SUM(IF(classification_code IN (15110 , 20410, 15220) and waveform_features.feature_code =151002, 
            GREATEST(feature_value_a,feature_value_b, feature_value_c), 0)) AS fault_score,
            SUM(IF(waveform_features.feature_code = 151017, 1, 0)) AS slap_score,
            SUM(IF(waveform_features.feature_code = 151012, 1, 0)) AS broken_score
    FROM
        waveform_records, waveform_classifications, waveform_features
    WHERE
     record_time BETWEEN FROM_UNIXTIME(1632774572) AND FROM_UNIXTIME(1633379372) 
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
    GROUP BY TIMESTAMP(DATE_FORMAT(record_time,'%Y-%m-%d %H:00:00'))  , waveform_records.monitor_id) AS score
WHERE
     score.rec_time BETWEEN FROM_UNIXTIME(1632774572) AND FROM_UNIXTIME(1633379372)
        AND monitor.monitor_id = score.mid
        AND substation.substation_id = monitor.substation_id
GROUP BY time,score.mid
HAVING value > 59
ORDER BY score.rec_time
LIMIT 0, 10

-- Date: 2021-10-12 20:49
*/
INSERT INTO `score` VALUES ('2021-09-28 22:00:00','Esperanza EP-50','60');
INSERT INTO `score` VALUES ('2021-09-28 22:00:00','Esperanza EP-40','60');
INSERT INTO `score` VALUES ('2021-09-29 01:00:00','Lyle Wolz LW20','60');
INSERT INTO `score` VALUES ('2021-09-29 02:00:00','Rocksprings RS-60','30');
INSERT INTO `score` VALUES ('2021-09-29 09:00:00','Junction JN-40','40');
INSERT INTO `score` VALUES ('2021-09-30 13:00:00','Grape Creek West','30');
INSERT INTO `score` VALUES ('2021-09-30 21:00:00','Junction JN-40','60');
INSERT INTO `score` VALUES ('2021-09-30 22:00:00','Rocksprings RS-40','90');
INSERT INTO `score` VALUES ('2021-09-30 22:00:00','Rocksprings RS-60','60');
INSERT INTO `score` VALUES ('2021-09-30 23:00:00','Rocksprings RS-60','70');
