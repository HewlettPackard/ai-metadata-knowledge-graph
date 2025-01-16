###
# Copyright (2024) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

from neo4j import GraphDatabase
import logging


# class to establish connection to neo4j
class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
            # logger.debug("Neo4j driver initialized successfully.")
        except Exception as e:
            print("Failed to create the driver:", e)
            # logger.error("Failed to initialize Neo4j driver: %s", e)
            
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
            
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            #response = (session.run(query, parameters))
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        
        #return pd.DataFrame([r.values() for r in response], columns=response.keys())
        return response
        
    def multi_query(self, multi_line_query, parameters=None, db=None):
        for li in multi_line_query.splitlines():
                print(li)
                result=self.query(li, parameters=None, db=None)
                print(result)