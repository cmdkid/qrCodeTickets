import time

from src.DbSqlite import db
import config


COL_NAME_UUID = 'uuid'
COL_NAME_STATUS = 'status'
COL_NAME_DT = 'dt'

ticket_status_list = {
    'generated': 'G',
    'active': 'A',
    'used': 'U',
    'revoked': 'R'
}


def get_status_by_char(status_char: str):
    for k, v in ticket_status_list.items():
        if status_char == v:
            return k
    return None


def get_timestamp():
    return str(int(time.time()*10000000))


def create_table(table_name: str):
    sql = f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}';'''
    table_count = db.exec_select(sql, one_val=True)
    if 0 == table_count:
        sql = f'''CREATE TABLE {config.DB_UUID_TABLE_NAME} ({COL_NAME_UUID} CHAR(36) PRIMARY KEY NOT NULL, 
                  {COL_NAME_STATUS} char(1) NOT NULL, {COL_NAME_DT} timestamp NOT NULL);'''
        result = db.exec_create(sql)
    return True


def insert_new_uuid(uuid_val: str):
    sql = f"""INSERT INTO {config.DB_UUID_TABLE_NAME}({COL_NAME_UUID}, {COL_NAME_STATUS}, {COL_NAME_DT}) 
              VALUES("{uuid_val}", '{ticket_status_list.get("generated")}', {get_timestamp()});"""
    return db.exec_create(sql)


def set_uuid_status(uuid_val: str, new_status: str):
    if new_status not in ticket_status_list.keys():
        err_msg = f'Wrong new_status val {new_status}.'
        raise ValueError(err_msg)

    sql = f"""UPDATE {config.DB_UUID_TABLE_NAME} SET {COL_NAME_STATUS}='{ticket_status_list.get(new_status)}', {COL_NAME_DT}={get_timestamp()} WHERE {COL_NAME_UUID}="{uuid_val}";"""
    return db.exec_create(sql)


def get_uuid_status(uuid_val: str):
    sql = f"""SELECT status FROM {config.DB_UUID_TABLE_NAME} WHERE {COL_NAME_UUID}="{uuid_val}";"""
    return db.exec_select(sql, one_val=True)


def change_uuid_status(uuid: str, new_status: str, username: str):
    current_status = get_uuid_status(uuid)
    if current_status is None:
        return False

    if 'seller' == username:
        if ticket_status_list.get('generated', '<noSuchStatus>') == current_status and 'active' == new_status:
            set_uuid_status(uuid, new_status)
            return True
    else:
        if username in config.VALIDATORS_LIST:
            if current_status in [ticket_status_list.get('active', '<noSuchStatus>'),
                                  ticket_status_list.get('used', '<noSuchStatus>')] \
                    and new_status in ['used', 'revoked']:
                set_uuid_status(uuid, new_status)
                return True
    return False
