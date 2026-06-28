import sqlite3


class DataBaseUtils:
    db_path = "music_library.db"

    @classmethod
    def get_new_connection(cls):
        """为子线程提供一个全新的、独立的数据库连接"""
        path = cls.db_path
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn


    @classmethod
    def init_database(cls):
        """初始化数据库和表结构"""
        conn = cls.get_new_connection()
        cursor = conn.cursor()

        try:
            # 创建音乐库表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS music_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    genre TEXT,
                    year INTEGER,
                    is_favorite INTEGER DEFAULT 0
                )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON music_library(title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_artist ON music_library(artist)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_album ON music_library(album)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_favorite ON music_library(is_favorite);")

            # 创建播放列表表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_default INTEGER DEFAULT 0
                )
            """)

            # 创建播放列表项表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER NOT NULL,
                    music_id INTEGER NOT NULL,
                    position INTEGER NOT NULL
                )
            """)

            # 创建播放列表项索引
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_playlist_items_playlist ON playlist_items(playlist_id, position)")

            conn.commit()
        except Exception as e:
            print(f"数据库初始化出错: {e}")
        finally:
            conn.close()

    @classmethod
    def insert_or_update_music(cls, conn: sqlite3.Connection, file_path: str, title: str = None, artist: str = None,
                               album: str = None, genre: str = None, year: int = None, is_favorite: int = 0) -> int:
        """插入或更新单首音乐信息，返回音乐ID"""

        cursor = conn.cursor()
        try:
            # 先查询是否已存在
            cursor.execute("SELECT id FROM music_library WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()

            if row:
                # 更新现有记录
                music_id = row[0]
                cursor.execute("""
                        UPDATE music_library 
                        SET title = ?, artist = ?, album = ?, genre = ?, year = ?, is_favorite = ?
                        WHERE file_path = ?
                    """, (title, artist, album, genre, year, is_favorite, file_path))
            else:
                # 插入新记录
                cursor.execute("""
                        INSERT INTO music_library (file_path, title, artist, album, genre, year, is_favorite)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (file_path, title, artist, album, genre, year, is_favorite))
                music_id = cursor.lastrowid

            conn.commit()
            return music_id
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return -1

    @classmethod
    def select_all_music(cls, conn:sqlite3.Connection)->list[tuple]:
        """获取所有可用的音乐列表"""
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_path, title, artist, album, genre, year, is_favorite FROM music_library")
        return cursor.fetchall()

    @classmethod
    def create_playlist(cls, conn:sqlite3.Connection, name: str, is_default: int = 0):
        """创建新播放列表"""
        cursor = conn.cursor()
        try:
            cursor.execute("""
                  INSERT INTO playlists (name, is_default) VALUES (?, ?)
              """, (name, is_default))
            conn.commit()
            return cursor.lastrowid  # 返回新创建的播放列表 ID
        except sqlite3.IntegrityError:
            print(f"Playlist '{name}' already exists.")
            return None

    @classmethod
    def add_to_playlist(cls, conn:sqlite3.Connection, playlist_id: int, music_id: int):
        """向播放列表末尾添加歌曲"""
        cursor = conn.cursor()

        try:
            # 1. 计算当前播放列表中已有的歌曲数量，作为新歌曲的 position
            cursor.execute("""
                    SELECT COUNT(*) FROM playlist_items 
                    WHERE playlist_id = ?
                """, (playlist_id,))
            count = cursor.fetchone()[0]

            # 2. 插入数据，position 即为当前的 count (从 0 开始)
            cursor.execute("""
                    INSERT INTO playlist_items (playlist_id, music_id, position)
                    VALUES (?, ?, ?)
                """, (playlist_id, music_id, count))

            conn.commit()
        except sqlite3.Error as e:
            print(f"添加歌曲到播放列表失败: {e}")

    @classmethod
    def get_all_playlists(cls, conn: sqlite3.Connection) -> list[tuple]:
        """获取所有播放列表（用于左侧 playlists 组件展示）"""
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, is_default FROM playlists ORDER BY id ASC")
        return cursor.fetchall()

    @classmethod
    def get_playlist_music_ids(cls, conn: sqlite3.Connection, playlist_id: int) -> set[int]:
        """获取指定播放列表包含的所有音乐 ID（用于 ProxyModel 过滤）"""
        cursor = conn.cursor()
        cursor.execute("SELECT music_id FROM playlist_items WHERE playlist_id = ?", (playlist_id,))
        return {row[0] for row in cursor.fetchall()}

    @classmethod
    def toggle_favorite(cls, conn: sqlite3.Connection, id: int, is_favorite: int):
        """设置歌曲的喜欢状态,0表示从喜欢列表移除,1表示设置为喜欢"""
        cursor = conn.cursor()
        try:
            cursor.execute("""
                    UPDATE music_library 
                    SET is_favorite = ? 
                    WHERE id = ?
                """, (is_favorite, id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"更新喜欢状态失败: {e}")

    @classmethod
    def remove_from_playlist(cls, conn: sqlite3.Connection, playlist_id: int, music_id: int):
        """从播放列表中移除指定歌曲"""
        cursor = conn.cursor()
        try:
            cursor.execute("""
                   DELETE FROM playlist_items 
                   WHERE playlist_id = ? AND music_id = ?
               """, (playlist_id, music_id))

            # 重新排序剩余歌曲的 position
            cursor.execute("""
                   UPDATE playlist_items 
                   SET position = position - 1 
                   WHERE playlist_id = ? AND position > (
                       SELECT position FROM playlist_items 
                       WHERE playlist_id = ? AND music_id = ?
                   )
               """, (playlist_id, playlist_id, music_id))

            conn.commit()
        except sqlite3.Error as e:
            print(f"从播放列表移除歌曲失败: {e}")

    @classmethod
    def delete_playlist(cls, conn: sqlite3.Connection, playlist_id: int):
        """删除播放列表及其所有歌曲项"""
        cursor = conn.cursor()
        try:
            # 先删除播放列表中的所有歌曲项
            cursor.execute("DELETE FROM playlist_items WHERE playlist_id = ?", (playlist_id,))
            # 再删除播放列表本身
            cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"删除播放列表失败: {e}")

    @classmethod
    def clear_all_data(cls, conn: sqlite3.Connection):
        """清除所有表中的数据，但保留表结构"""
        cursor = conn.cursor()
        try:
            # 按外键依赖顺序删除数据
            cursor.execute("DELETE FROM playlist_items")
            cursor.execute("DELETE FROM playlists")
            cursor.execute("DELETE FROM music_library")

            # 重置自增ID计数器
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='music_library'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='playlists'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='playlist_items'")

            conn.commit()
        except sqlite3.Error as e:
            print(f"清除数据失败: {e}")




if __name__ == '__main__':
    pass

