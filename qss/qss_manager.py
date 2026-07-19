'''
管理所有样式
'''

main_window ='''
*{{
    color: {font_color};
}}

QWidget#main_window{{
    background-color: {main_window_background_color};
}}

QToolTip {{
    background-color: {tooltip_background_color};
    border: none;
    color: {font_color};
}}

QPushButton{{
    background-color: transparent;
}}

QPushButton:hover {{
    border: none;
    background-color: {button_hover_color};  /* 或与正常状态相同 */
}}

QPushButton:pressed {{
    /* 按下时：上边距增加，下边距减小，产生向下移动错觉 */
    margin-top: 1px;
    margin-bottom: -1px;
    background-color: #555555;
}}
'''

play_lists='''
QWidget#play_lists QLineEdit {{
    height: 40px;
    background-color: #3a3a3b;
    border: none;
}}

QListWidget {{
    color: {font_color};
    background-color: transparent;
    border: 0px;
    outline: none;   /* 确保 item 获取焦点时没有虚线框 */
}}


QListWidget::item:selected {{
    background-color: transparent;
}}

/* 关键：失去焦点时的选中状态 */
QListWidget::item:selected:!active {{
    background-color: transparent;
    color: {font_color};       /* 强制保持白色 */
}}


QListWidget::item:hover {{
    background-color: {list_item_hover_color};
}}



QListWidget QScrollBar:vertical {{
    width: 8px;
    background-color: transparent;
}}

QListWidget QScrollBar::handle:vertical {{
    background-color: {list_and_table_handle_color};
    border-radius: 4px;
    min-height: 20px;
}}

QListWidget QScrollBar::handle:vertical:hover {{
    background-color: {list_and_table_handle_hover_color};
}}

QListWidget QScrollBar::add-line:vertical,
QListWidget QScrollBar::sub-line:vertical {{
    height: 0px;  /* 隐藏上下箭头 */
}}

QListWidget QScrollBar::add-page:vertical,
QListWidget QScrollBar::sub-page:vertical {{
    background-color: transparent;  /* 滑块轨道背景 */
}}
'''

player_controls = '''
QWidget#player_controls{{
    background-color: {song_info_and_player_control_background_color};
}}

QWidget#player_controls QPushButton {{
    border-radius: 16px;
}}

QWidget#player_controls QLabel {{
    font-size: 14px;
}}

QWidget#player_controls QMenu QLabel {{
    font-size: 12px;
}}

/* 水平slider部分 */
QSlider::groove:horizontal {{
    height: 4px;
    background-color: {horizontal_slider_background_color};  /* 轨道背景 */
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background-color: {slider_left_and_bottom_background_color};  /* 已播放部分 */
    border-radius: 2px;
}}

QSlider::add-page:horizontal {{
    background-color: transparent; /* 未播放部分（通常透明，露出 groove） */
}}

QSlider::handle:horizontal {{
    width: 18px;
    height: 18px;
    margin: -7px 0;  /* 让滑块突出轨道 */
    background-color: {font_color};
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {slider_handle_hover};
}}

/* 垂直slider部分 */
QSlider::groove:vertical {{
    width: 4px;
    background-color: vertical_slider_background_color;  /* 轨道背景 */
    border-radius: 2px;
}}

QSlider::sub-page:vertical {{
    background-color: transparent;  /* 上方透明 */
}}

QSlider::add-page:vertical {{
    background-color: {slider_left_and_bottom_background_color};  /* 下方有色 */
}}

QSlider::handle:vertical {{
    height: 12px;
    width: 12px;
    margin: 0 -4px;  /* 让滑块水平居中并突出 */
    background-color: {font_color};
    border-radius: 6px;
}}

QSlider::handle:vertical:hover {{
    background-color: {slider_handle_hover};
}}
'''

playerlist_view ='''
QTableView {{
    color: {font_color};
    background-color: {table_background_color};
    border: none;
    gridline-color: transparent;       /* 隐藏网格线 */
    outline: none; /* 尝试去掉外轮廓 */
}}

QTableView::item:selected {{
    background-color: {table_item_selected_color};
}}

/* 失去焦点时的选中状态 */
QTableView::item:selected:!active {{
    color: {font_color};       /* 强制保持白色 */
}}


QHeaderView::section {{
    background-color: {table_background_color};
    border: none;
    height: 30px;
}}


QHeaderView::section:hover {{
    background-color: {table_item_selected_color};
}}


QTableView QScrollBar:vertical {{
    width: 8px;
    background-color: {table_slider_background_color};         /* 【改】用实色替代 transparent */
}}
QTableView QScrollBar::handle:vertical {{
    background-color: {list_and_table_handle_color};         /* 与 QListWidget 一致 */
    min-height: 20px;
}}
QTableView QScrollBar::handle:vertical:hover {{
    background-color: {list_and_table_handle_hover_color};         /* 与 QListWidget 一致 */
}}
QTableView QScrollBar::add-line:vertical,
QTableView QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QTableView QScrollBar::add-page:vertical,
QTableView QScrollBar::sub-page:vertical {{
    background-color: {table_slider_background_color};         /* 【改】用实色替代 transparent */
}}
'''

qmenu = '''
QMenu {{
    background-color: {menu_background_color};
    border-radius:5px;
}}

QMenu::item {{
    background-color: transparent;  /* 菜单项背景 */
}}

QMenu::item:selected {{
    background-color:  {menu_item_selected};  /* 选中项背景 */
}}
'''

song_info_panel ='''
QWidget#song_info_panel{{
    background-color: {song_info_and_player_control_background_color};
}}
QWidget#song_info_panel QLabel#title_label{{
    font-size: 18px;
}}
QWidget#song_info_panel QLabel#artist_label{{
    font-size: 15px;
}}
'''

titlebar ='''
QWidget#titlebar QPushButton{{
    border-radius: 5px;
}}
'''

widget_list = [main_window,play_lists,player_controls,playerlist_view,qmenu,song_info_panel,titlebar]

dark_theme = {
    'font_color' : 'white', # 总体字体颜色
    'main_window_background_color' : '#656564', # 主窗口的背景色
    'button_hover_color' :'#858585', # 鼠标放在按钮上悬停的颜色

    'tooltip_background_color': 'black', # tooltip的背景颜色
    'menu_item_selected' : '#2ABf9E', # 菜单选中项的背景颜色
    'menu_background_color' : '#656564', # menu的背景色

    # player_controls 和 song_info_panel 部分
    'song_info_and_player_control_background_color' : '#3a3329', # 窗口底部播放模块的背景颜色
    'horizontal_slider_background_color' : '#716b65', #音频轨道背景颜色
    'vertical_slider_background_color' : '#333333', # 音量控制轨道背景颜色
    'slider_left_and_bottom_background_color':'#2ABf9E', # 音频轨道左侧和音量控制轨道下方轨道背景颜色
    'slider_handle_hover' : '#EEEEEE', # 鼠标悬停在音频轨道和音量控制轨道上滑块的颜色

    # playlist_view 和 play_lists 部分
    'table_background_color' : '#33373B', # 音乐列表的背景颜色
    'table_item_selected_color' : '#2ABf9E', # table中item、表头选中时的背景颜色
    'table_slider_background_color' : '#656564', # table中轨道的背景颜色
    'list_item_hover_color' : '#858585',# 鼠标放在list中item上悬停的颜色
    'list_and_table_handle_color': '#515151', # list、table滑块的颜色
    'list_and_table_handle_hover_color': '#7c7c7c', # 鼠标放在list、table滑块上悬停的颜色

    # 没有直接继承父组件的单独组件的样式设置
}



def get_style():
    qss_template = ''
    for widget in widget_list:
        qss_template  = qss_template + '\n' + widget

    return qss_template.format(**dark_theme)