#!/usr/bin/env python
import json
from decimal import Decimal
import requests
import logging
log = logging.getLogger(__name__)

def data_records_to_json(data_list,schema_list,dest_file):
    with open(dest_file,'wb') as outfile:
        for row in data_list:
            result_dct = process_data_row(row,schema_list)
            outfile.write("%s\n" % json.dumps(result_dct, default=_defaultencode))


def data_records_list(data_list,schema_list):
    result_list = []
    for row in data_list:
        result_dct = process_data_row(row,schema_list)
        result_list.append(result_dct)
    return result_list


def data_record_list_to_json(data_records_list,dest_file):
    with open(dest_file,'wb') as outfile:
        for dct in data_records_list:
            outfile.write("%s\n" % json.dumps(dct, default=_defaultencode))


def process_data_row(row,schema_list):
    tmp_set = set()
    result_dct = {}
    i = 0
    for k,t in schema_list:
        if "list" in str(t):
            tmp_val = row[i]
        try:
            if "date" in str(t) or str(t) == 'timestamp':
                if row[i] is None or row[i] =="":
                    result_dct[k] = None #row[i]
                elif str(t) == "<type 'datetime.date'>":
                    result_dct[k] = str(row[i]) + " 00:00:00"
                else:
                    result_dct[k] = str(row[i]).split('.')[0]
            elif "list" in str(t):
                if row[i] is None:
                    #print tmp_id, 'none'
                    tmp_set.add(tmp_val)
                elif row[i] == '[null]':
                    pass
                else:
                    val = row[i].replace('[','').replace(']','')
                    val = val.replace('"','')
                    l = []
                    for itm in val.split(','):
                        l.append(itm)
                    result_dct[k] = l
            elif "bool" in str(t):
                if row[i] == 1 or row[i] == True:
                    result_dct[k] = True
                elif row[i] is not None:
                    result_dct[k] = False
                else: result_dct[k] = None
            else:
                if row[i] is None or row[i]=="":
                    result_dct[k] = None
                else:
                    result_dct[k] = row[i]
        except(KeyError, IndexError) as e:
            log.error('Error in dictionary call: {0} for index {1}'.format(e,i))
        i += 1

    return result_dct


def process_postgres_data_row(row,schema_list):
    tmp_set = set()
    result_dct = {}
    i = 0
    for k,t in schema_list:
        if "list" in str(t):
            tmp_val = row[i]
        try:
            if str(t) == '1114': # datetime
                if row[i] is None or row[i] =="":
                    result_dct[k] = None
                else:
                    result_dct[k] = str(row[i])
            elif str(t) == '1043': # varchar
                if row[i] is None or row[i]=="":
                    result_dct[k] = None
                else:
                    result_dct[k] = row[i]
            elif "list" in str(t):
                if row[i] is None:
                    tmp_set.add(tmp_val)
                elif row[i] == '[null]':
                    pass
                else:
                    val = row[i].replace('[','').replace(']','')
                    val = val.replace('"','')
                    l = []
                    for itm in val.split(','):
                        l.append(itm)
                    result_dct[k] = l
            elif str(t) == '16': # boolean
                if row[i] == 1 or row[i] == True:
                    result_dct[k] = True
                elif row[i] is not None:
                    result_dct[k] = False
                else: result_dct[k] = None
            else:
                if row[i] is None or row[i]=="":
                    result_dct[k] = None
                else:
                    result_dct[k] = row[i]
        except(KeyError, IndexError) as e:
            log.error('Error in dictionary call: {0} for index {1}'.format(e,i))
        i += 1

    return result_dct

def _defaultencode(o):
    if isinstance(o, Decimal):
        return str(o)   
    raise TypeError(repr(o) + " is not JSON serializable")


def punt_baxter():
    try:
        import webbrowser
        webbrowser.open('https://giphy.com/gifs/will-ferrell-anchorman-jack-black-ikcJ56KAyhm8w/fullscreen')
    except Exception as e:
        log.info("The man punted baxter! I'm in a glass case of emotion.")


def send_alert_to_opsgenie(api_url, api_key, message, description):
    payload = {'apiKey': api_key, 'message': message, 'description': description}
    json_payload = json.dumps(payload)
    r = requests.post(api_url, data=json_payload)
