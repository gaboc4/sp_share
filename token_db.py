import sqlite3

class TokenDB():
    def __init__(self) -> None:
        self.con = sqlite3.connect("sp_share.db")
    
    def set_token(self, user_id:str, refresh_token: str):
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS token_info(user_id, refresh_token)")
        cur.execute(f"INSERT INTO token_info VALUES ('{user_id}', '{refresh_token}')")
    
    def get_token(self, user_id: str):
        cur = self.con.cursor()
        res = cur.execute(f"SELECT refresh_token FROM token_info WHERE user_id = '{user_id}'")
        return res.fetchone()

