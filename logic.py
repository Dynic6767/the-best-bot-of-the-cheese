import sqlite3
from config import DATABASE

cheeses = [(_,) for _ in (['Чеддер', 'Бри', 'Гауда', 'Моцарелла'])]
statuses = [(_,) for _ in (['На этапе созревания', 'В процессе производства', 'Готов к употреблению', 'Обновлен', 'Завершен. Не поддерживается'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)

        with conn:
            conn.execute(""" CREATE TABLE cheese_projects(
                        project_id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        cheese_name TEXT,
                        description TEXT,
                        recommendations TEXT,
                        url TEXT,
                        status_id INTEGER,
                        photo TEXT,  
                        FOREIGN KEY (status_id)  REFERENCES cheese_status (status_id))
        """)
            conn.execute(""" CREATE TABLE cheese_status(
                        status_id INTEGER PRIMARY KEY,
                        status_name TEXT
                        )
        """)
            conn.execute(""" CREATE TABLE cheese_skills(
                        skill_id INTEGER PRIMARY KEY,
                        skill_name TEXT
                        )
        """)
            conn.execute(""" CREATE TABLE cheese_project_skills(
                        project_id INTEGER,
                        skill_id INTEGER,
                        FOREIGN KEY (project_id)  REFERENCES cheese_projects (project_id),
                        FOREIGN KEY (skill_id)  REFERENCES cheese_skills (skill_id))
        """)

    def add_photo_column(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        try:
            alter_query = "ALTER TABLE cheese_projects ADD COLUMN photo TEXT"
            cursor.execute(alter_query)
        except sqlite3.OperationalError:
            pass
        
        photo_data = {
            1: 'C:\\kodland\\dbbaza\\cheese_project_1.png',
            2: 'C:\\kodland\\dbbaza\\cheese_project_2.png',
            3: 'C:\\kodland\\dbbaza\\cheese_project_3.png',
            4: 'C:\\kodland\\dbbaza\\cheese_project_4.png',
        }
        
        for project_id, photo in photo_data.items():
            update_query = "UPDATE cheese_projects SET photo = ? WHERE project_id = ?"
            cursor.execute(update_query, (photo, project_id))
        
        conn.commit()
        conn.close()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        sql = 'INSERT INTO cheese_skills (skill_name) values(?)'
        data = cheeses
        self.__executemany(sql, data)
        sql = 'INSERT INTO cheese_status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)

    def insert_project(self, data):
        sql = """INSERT INTO cheese_projects 
        (user_id, cheese_name, recommendations, url, status_id) 
        values(?, ?, ?, ?, ?)"""
        self.__executemany(sql, data)

    def insert_skill(self, user_id, cheese_name, skill):
        sql = 'SELECT project_id FROM cheese_projects WHERE cheese_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (cheese_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM cheese_skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO cheese_project_skills VALUES(?, ?)'
        self.__executemany(sql, data)
    
    def get_statuses(self):
        sql="SELECT status_name from cheese_status"
        return self.__select_data(sql)

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM cheese_status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None
    
    def update_projects(self, param, data):
        sql = f"""UPDATE cheese_projects SET {param} = ? 
        WHERE cheese_name = ? AND user_id = ?"""
        self.__executemany(sql, [data]) 
    
    def delete_project(self, user_id, project_id):
        sql = """DELETE FROM cheese_projects 
        WHERE user_id = ? AND project_id = ? """
        self.__executemany(sql, [(user_id, project_id)])

    def get_projects(self, user_id):
        sql="""SELECT * FROM cheese_projects 
        WHERE user_id = ?"""
        return self.__select_data(sql, data = (user_id,))
    
    def get_project_id(self, cheese_name, user_id):
        return self.__select_data(sql='SELECT project_id FROM cheese_projects WHERE cheese_name = ? AND user_id = ?  ', data = (cheese_name, user_id,))[0][0]
    
    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM cheese_skills')
    
    def get_project_skills(self, cheese_name):
        res = self.__select_data(sql='''SELECT skill_name FROM cheese_projects 
        JOIN cheese_project_skills ON cheese_projects.project_id = cheese_project_skills.project_id 
        JOIN cheese_skills ON cheese_skills.skill_id = cheese_project_skills.skill_id 
        WHERE cheese_name = ?''', data = (cheese_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, cheese_name):
        sql = """
        SELECT cheese_name, description, url, status_name, photo FROM cheese_projects 
        JOIN cheese_status ON
        cheese_status.status_id = cheese_projects.status_id
        WHERE cheese_name=? AND user_id=?
        """
        return self.__select_data(sql=sql, data = (cheese_name, user_id))
    
    def delete_skill(self, project_id, skill_id):
        sql = """DELETE FROM cheese_skills 
        WHERE skill_id = ? AND project_id = ? """
        self.__executemany(sql, [(skill_id, project_id)])

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()
    manager.add_photo_column()

