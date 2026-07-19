import os


class AssetsUtils:
    '''静态资源工具类'''
    @classmethod
    def get_icon_full_path_by_asset_name(cls,asset_name:str):
        proj_root_path = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(proj_root_path,'assets/icons/'+asset_name)



if __name__ =='__main__':
    ans = AssetsUtils.get_icon_full_path_by_asset_name('1')
    print(ans)
