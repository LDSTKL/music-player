from utils.database_utils import DataBaseUtils


class SettingsUtils:
    '''在database_utils封装对设置的操作'''
    __settings = None
    @classmethod
    def get_settings(cls):
        if cls.__settings is not None:
            return cls.__settings
        else:
            conn = DataBaseUtils.get_new_connection()
            try:
                cls.__settings = DataBaseUtils.get_settings(conn)
                return cls.__settings
            finally:
                conn.close()

