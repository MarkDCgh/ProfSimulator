import sqlite3 as sql

#TODO:Control SQlite class functions, check if they work (create table and insert into table are already checked)
#TODO: FIX IMAGE LOADING

class SQLite: 
    # NEED TO UNDERSTAND when to commit
    def __init__(self, path): 
        '''Creates a new SQLite database
        Args:
            path (str): path to the database
        '''
        self.connection = sql.connect(path)
        self.cursor = self.connection.cursor()
        
    def Execute(self, command):
        '''DEVELOPER ONLY, Executes a command in the database  
        Args:
            command (str): command to be executed
        '''
        self.cursor.execute(command)
            
    def CreateTable(self, table_name, column_names): 
        '''Creates a table in the database
        Args:
            table_name (str): name of the table
            columns_names (str): name of columns of the table, each column is separated by a comma
        '''
        self.cursor.execute(f"CREATE TABLE {table_name} ({column_names})") 
        self.cursor.connection.commit()
        
    def InsertIntoTable(self, table_name, columns, values):
        '''Inserts values into the table   
        Args:
            table_name (str): name of the table
            columns (str): columns of the table
            values (tuple of str): values to be inserted
        '''
        placeholders = ('?,' * len(values))[:-1] # string with as many ? as values, then removes last char, which is ','
        
        self.cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});", values)
        self.cursor.connection.commit()
        
    def ChangeValuesInTable(self, table_name, columns, values, condition):
        '''Changes values in the table
        Args:
            table_name (str): name of the table
            columns (str): columns to be changed, each column is separated by a comma
            values (tuple): values to insert
            condition (str): condition to change values
        '''
        placeholders = ('?,' * len(values))[:-1] 

        self.cursor.execute(f"UPDATE {table_name} SET {columns} = {placeholders} WHERE {condition};", values)
        self.cursor.connection.commit()
        
    def ReadFromTable(self, table_name, columns, condition = True, response_size = 0):
        '''Returns rows (list of tuples) from the table
        Args: 
            table_name (str): name of the table
            columns (str): columns to be returned, each column is separated by a comma
            condition (str): condition to return values
            response_size (int): number of rows to be returned 
        Returns: 
            list of tuples (table rows)
        '''
        self.cursor.execute(f"SELECT {columns} FROM {table_name} WHERE {condition};")
        
        if response_size == 0:
            response = self.cursor.fetchall()
        else: 
            response = self.cursor.fetchmany(response_size)
    
        return response
        
    def DeleteTable(self, table_name): 
        '''Deletes a table from the database
        Args:
            table_name (str): name of the table
        ''' 
        self.cursor.execute(f"DROP TABLE {table_name};")
        self.cursor.connection.commit()
        
    def DeleteFromTable(self, table_name, condition): 
        '''Deletes values from the table
        Args:
            table_name (str): name of the table
            condition (str): condition to delete values
        '''
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition};")
        self.cursor.connection.commit()