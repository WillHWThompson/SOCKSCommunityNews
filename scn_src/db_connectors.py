from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import pymysql
import sqlite3 
import os
import pandas as pd


#load the psswd_dict from the environment
WTHOMPS3_ADMIN_PSSWD= os.environ.get("WTHOMPS3_ADMIN_PSSWD")
WTHOMPS3_READER_PSSWD= os.environ.get("WTHOMPS3_READER_PSSWD")
WTHOMPS3_WRITER_PSSWD= os.environ.get("WTHOMPS3_WRITER_PSSWD")
psswd_dict = {"admin":WTHOMPS3_ADMIN_PSSWD,"reader":WTHOMPS3_READER_PSSWD,"writer":WTHOMPS3_WRITER_PSSWD}




class DBConnector:
    def __init__(self):
        pass

    def make_connector(self):
        pass 
    
    def load_csv_to_sqlite(self, csv_path, table_name, if_exists="replace"):
        """
        Load data from a CSV file into an SQLite database table.

        Parameters:
        csv_path (str): The path to the CSV file.
        table_name (str): The name of the table to create.
        if_exists (str): What to do if the table already exists. Options are "replace", "append", and "fail".

        Returns:
        None
        """
        engine = self.make_connector()
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        
   # def load_data_to_sql(
   #     self,table_name, file_path=None, df=None, if_exists="replace"
   # ):
   #     """
   #     Load data from a CSV, JSON, or Parquet file into an SQLite database table.

   #     :param db_path: Path to the SQLite database file.
   #     :param table_name: Name of the table where the data will be inserted.
   #     :param file_path: Path to the source file (CSV, JSON, or Parquet), provided instead of df
   #     :param df: DataFrame to load, provided instead of file_path
   #     :param if_exists: What to do if the table already exists - options are 'fail', 'replace', or 'append'. Default is 'replace'.

   #     :return: None
   #     """
   #     if file_path != None:
   #        df = self.load_df_from_file(file_path)
   #     if (type(df) != type(None)) and (file_path != None):
   #         ValueError("One of'file_path' or 'df' may be passed but not both")
   #     # Write the data to the SQLite table
   # 
   #     df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
   #     # Close the database connection
    def load_data_to_sql(self, table_name, df, unique_keys = None):
        with self.engine.connect() as connection:
            # Get column names from DataFrame
            columns = df.columns.tolist()
            # Generate the column placeholders
            columns_placeholder = ", ".join(columns)
            # Generate the value placeholders
            values_placeholder = ", ".join([f":{col}" for col in columns])
            # Generate the update placeholders for ON DUPLICATE KEY UPDATE
            update_placeholder = ", ".join([f"{col}=VALUES({col})" for col in columns if col not in unique_keys])

            for index, row in df.iterrows():
                # Convert the row to a dictionary of values
                values = {col: row[col] for col in columns}
                insert_query = f"""
                INSERT INTO {table_name} ({columns_placeholder})
                VALUES ({values_placeholder})
                ON DUPLICATE KEY UPDATE {update_placeholder};
                """
                connection.execute(text(insert_query), **values)
            connection.commit()

        
    def load_df_from_file(self, file_path):
        """
        Load a DataFrame from a file.

        Parameters:
        file_path (str): The path to the file.

        Returns:
        df (DataFrame): The DataFrame.
        """
        file_type = file_path.split(".")[-1]
        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type == "json":
            df = pd.read_json(file_path)
        elif file_type == "parquet":
            df = pd.read_parquet(file_path)
        else:
            raise ValueError("File type not supported")
        return df 


    def execute_query(self,query):
        with self.engine.connect() as connection: 
            response = connection.execute(text(query))
        return response
            

class SQLiteConnector(DBConnector):
    def __init__(self, db_file):
        self.db_file = db_file
        print("hello")
        self.engine = self.make_connector()
        
        super().__init__()
        
    def make_connector(self):
        engine = None
        print("hello")
        try:
            engine =  create_engine(f'sqlite:///{self.db_file}')
        except sqlalchemy.Error as e:
            print(e)
        return engine
    

    def load_data_to_sql(
        self,table_name, df=None,unique_keys = None 
    ):
        super().load_data_to_sql(table_name,df,unique_keys)
        print(f"Data has been loaded into {table_name} in database at {self.db_file}")

class MySQLConnector(DBConnector):
    def __init__(self, user = 'wthomps3', password = None ,permission = 'reader', host = 'webdb.uvm.edu', database = 'WTHOMPS3_scn_socks'):
        self.user = user+'_'+permission
        if password is None:
            self.password = psswd_dict[permission]
        else :
            self.password = password
            
        self.host = host
        self.database = database
        self.engine = self.make_connector()

        super().__init__()
        
    def make_connector(self):
        engine_string = f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}"
        engine = create_engine(engine_string)
        return engine


    def load_data_to_sql(
        self,table_name,df=None,unique_keys = None 
    ):
        super().load_data_to_sql(table_name,df = df,unique_keys = unique_keys)
        print(f"Data has been loaded into {table_name} in database at {self.host}:{self.database}")

        

