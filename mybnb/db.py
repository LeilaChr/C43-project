import mysql.connector

connection = mysql.connector.connect(user='root', password='',
                                     host='127.0.0.1',
                                     database='mybnb',
                                     autocommit=True)

def query(sql: str, **env):
    print(trim_lines(sql % env))

    global connection
    cursor = connection.cursor(named_tuple=True)
    cursor.execute(sql, env)
    return cursor

def trim_lines(text: str):
    return '\n'.join([line.strip() for line in text.split('\n')])
