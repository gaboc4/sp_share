import sqlite3

class TokenDB():
    def __init__(self) -> None:
        self.con = sqlite3.connect("sp_share.db")
    
    def set_token(self, token: str):
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS access_token(token)")
        cur.execute(f"INSERT INTO access_token VALUES ('{token}')")
    
    def get_token(self):
        cur = self.con.cursor()
        res = cur.execute("SELECT token FROM access_token")
        return res.fetchone()

