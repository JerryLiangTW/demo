import mysql.connector
import threading
import time
import datetime
import sys
import logging
import logging.handlers
import disconnect
from mysql.connector import Error
from mysql.connector import errorcode
from mysql.connector import pooling
from mysql.connector.connection import MySQLConnection
from sqlalchemy.orm import scoped_session
from typing import Dict, List

class Update_thread(threading.Thread):
    def __init__(self, threadID, data, Session, engine):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.data = data
        self.logger = logging.getLogger('MyLogger')
        self.retryCount = 0
        self.session = Session
        self.engine = engine

    def mysql_update_postman(self):
        sql_search = "select * from cppm.postman where mac_address = :mac_address"
        some_session = self.session()
        params = {
            "mac_address": self.data["mac_address"],
            "Action_Reason": self.data["Action_Reason"],
            "server_ip": self.data["server_ip"]
        }
        cursor = some_session.execute(sql_search, params) 
        records = cursor.fetchall()
        if records.__len__() == 0:
            sql_create = "INSERT INTO postman (mac_address,Action_Reason,server_ip,count,auth_date) values (:mac_address, :Action_Reason,:server_ip,:count,:auth_date)"
            params["count"] = 1
            params["auth_date"] = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')

            cursor = some_session.execute(sql_create, params) 
            some_session.commit()
            some_session.close()
        else:
            today = datetime.datetime.today()
            #for ubuntu
            last_update_time = records[0]["auth_date"]
            # last_update_time = datetime.datetime.strptime(records[0]["auth_date"][:-1],'%Y-%m-%d %H:%M:%S.%f')
            diff = today - last_update_time
            sql_update = "UPDATE postman Set mac_address=:mac_address, Action_Reason=:Action_Reason,server_ip=:server_ip,count=:count,auth_date=:auth_date"
            if(diff.days < 1):
                print(last_update_time)
                count = int(records[0]["count"]) + 1
                params["count"]= count
            else:
                # reset count to one
                params["count"] = 1
            
            params["auth_date"] = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            sql_update += " where mac_address=:mac_address"

            cursor = some_session.execute(sql_update, params) 
            some_session.commit()
            some_session.close()
    
    def mysql_update_cppm(self):
        sql_search = "select * from cppm.mtk where mac_address = :mac_address"
        some_session = self.session()
        params = {
            'mac_address': self.data["mac-addr"],
            "switch_name": self.data["switch-name"],
            "switch_ip": self.data["switch-ip"],
            "switch_port": self.data["switch-port"],
            "enforcement_profile": self.data["enforcement-profile"],
            "client_ip": self.data["client-ip"]
        }
        cursor = some_session.execute(sql_search, params) 
        records = cursor.fetchall()

        if records.__len__() == 0:
            sql_create = "INSERT INTO mtk (mac_address, switch_name,switch_ip,switch_port,enforcement_profile,client_ip,count,auth_date) values (:mac_address, :switch_name,:switch_ip,:switch_port,:enforcement_profile,:client_ip,:count,:auth_date)"
            params["count"] = 1
            params["auth_date"] = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')

            cursor = some_session.execute(sql_create, params) 
            some_session.commit()
            some_session.close()
        else:
            today = datetime.datetime.today()
            #for ubuntu
            last_update_time = records[0]["auth_date"]
            # last_update_time = datetime.datetime.strptime(records[0]["auth_date"][:-1],'%Y-%m-%d %H:%M:%S.%f')
            diff = today - last_update_time
            sql_update = "UPDATE mtk Set mac_address=:mac_address, switch_name=:switch_name,switch_ip=:switch_ip,switch_port=:switch_port,enforcement_profile=:enforcement_profile,client_ip=:client_ip,count=:count,auth_date=:auth_date"
            if(diff.days < 1):
                print(last_update_time)
                count = int(records[0]["count"]) + 1
                params["count"]= count
            else:
                # reset count to one
                params["count"] = 1
            
            params["auth_date"] = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            sql_update += " where mac_address=:mac_address"

            cursor = some_session.execute(sql_update, params) 
            some_session.commit()
            some_session.close()

    def get_pool_info(self) -> Dict:
        """Get information about the current connections and pool"""
        return {
        "pool id": id(self.engine.pool),
        "connections in current pool": (
            self.engine.pool.checkedin() + self.engine.pool.checkedout()
        ),
    }

    def run(self):
        connection = None
        try:
            if "Action_Reason" in self.data:
                self.mysql_update_postman()
                disconnect.disconnect(mac=self.data["mac_address"])
            else:
                self.mysql_update_cppm()
            # str_pool = self.get_pool_info()
            # print(str_pool)
            # self.logger.error("POOL DATA: %s", str_pool)
            # some_session.close()

            # connection = self.connect_pool.get_connection()
            # db_Info = connection.get_server_info()
            # cursor = connection.cursor()
            # self.update_record(cursor, connection)
        except Exception as ext:
            print("Exception: ", ext)
            time.sleep(3)
            self.retryCount += 1
            if self.retryCount <= 5:
                self.run()
            else:
                self.logger.error('Error: %s', ext)
                self.logger.error('Thread %s not update record: %s', self.threadID, self.data)
                sys.exit(0)
        # if(connection != None and connection.is_connected()):
        #     cursor.close()
        #     connection.close()
        #     print("MySQL connection is closed Thread", self.threadID)