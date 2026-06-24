from tinytag import TinyTag
import os

class AudioMetaDataUtils:
    @classmethod
    def get_music_meta(cls,file_path: str) -> dict:
        """
        使用 tinytag 快速获取音乐元数据
        :param file_path: 音乐文件的绝对路径
        :return: 包含 title, artist, album, duration, genre 的字典
        """
        if not os.path.exists(file_path):
            return {}

        try:
            # TinyTag.get 会自动识别格式并解析
            tag = TinyTag.get(file_path)

            return {
                "title": tag.title or os.path.splitext(os.path.basename(file_path))[0],  # 如果没有标题，用文件名
                "artist": tag.artist or "未知歌手",
                "album": tag.album or "未知专辑",
                "duration": int(tag.duration*1000),  # 单位：秒 (float)
                "genre": tag.genre or "",
                "year": tag.year or "",
            }
        except Exception as e:
            print(f"解析失败 {file_path}: {e}")
            return {}

if __name__=='__main__':
    print(AudioMetaDataUtils.get_music_meta('D:\音乐\许嵩 - 如果当时.mp3'))