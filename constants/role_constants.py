from PySide6.QtCore import Qt

class RoleConstants:
    store_music_id_role = Qt.ItemDataRole.UserRole # 存储音乐id
    store_full_path_role = Qt.ItemDataRole.UserRole +1 # 存储音乐所在的完整路径
    store_is_favorite_role = Qt.ItemDataRole.UserRole + 2 # 存储音乐是否标记为喜欢