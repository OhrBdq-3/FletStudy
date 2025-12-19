import flet as ft
from config.config import font_config

class InputControl(ft.Row):
    def __init__(self, on_send, dark_model = False):
        super().__init__()
        self.theme = "dark" if dark_model else "light"
        self.input_box_color = ft.Colors.BLACK12 if self.theme == "dark" else ft.Colors.GREY_100
        self.send_icon_color = ft.Colors.GREY_100 if self.theme == "dark" else ft.Colors.BLACK
        self.input_box = ft.TextField(
                hint_text="Ask Your Assistant", 
                expand=True,
                shift_enter=True,
                border_radius=10,
                on_submit=self.handle_send,
                bgcolor = self.input_box_color,
                #cursor_color = 
            )
        
        self.send_btn = ft.IconButton(
                icon = ft.Icons.SEND,
                on_click = self.handle_send,
                icon_color=self.send_icon_color
            )
        
        self.controls = [
            self.input_box, 
            self.send_btn
        ]

        self.alignment = ft.MainAxisAlignment.CENTER
        self.expand = True
        self.on_send = on_send
        

    def handle_send(self, e):
        if self.input_box.value.strip() != "":
            text = self.input_box.value
            self.input_box.value = ""
            self.on_send(text)
            self.update()

class ChatRow(ft.Row):
    def __init__(self, chat_value=None, character="user", dark_mode = False, window_width = 1000):
        super().__init__()
        self.window_width = window_width
        self.character = character
        self.dark_mode = dark_mode
        is_user = self.character == "user"

        if self.dark_mode:
            self.avatar_icon = ft.Icons.PERSON if is_user else ft.Icons.AUTO_AWESOME
            self.avatar_color = ft.Colors.WHITE 
            self.avatar_icon_color = ft.Colors.BLACK
            self.text_color = ft.Colors.WHITE
            self.bubble_color = ft.Colors.BLACK
        else:
            self.avatar_icon = ft.Icons.PERSON if is_user else ft.Icons.AUTO_AWESOME
            self.avatar_color = ft.Colors.BLUE_400 
            self.avatar_icon_color = ft.Colors.WHITE
            self.text_color = ft.Colors.BLACK
            self.bubble_color = ft.Colors.WHITE

        self.text_content = ft.Text(
            value=chat_value, 
            color=self.text_color, 
            selectable=True,
            weight=ft.FontWeight.W_400,
            )
        
        self.avatar = ft.CircleAvatar(
            content=ft.Icon(self.avatar_icon, color= self.avatar_icon_color),
            bgcolor=self.avatar_color,
            radius=16,
        )

        self.bubble = ft.Container(
            content=self.text_content, 
            bgcolor=self.bubble_color,
            padding=ft.padding.all(12),
            
            # border_radius=ft.border_radius.only(
            #     top_left=15,
            #     top_right=15,
            #     bottom_left=15 if is_user else 2, 
            #     bottom_right=2 if is_user else 15, 
            # ),
            border_radius=20,
            #alignment=ft.alignment.center_right if is_user else ft.alignment.center_left,
            #constraints=ft.BoxConstraints(max_width=500),
            
        )
        def get_max_width():
            return self.window_width * 0.7
    
        self.bubble_wrapper = ft.Column(
            controls=[self.bubble],
            tight=True, 
            width=get_max_width(),
            horizontal_alignment=ft.CrossAxisAlignment.END if is_user else ft.CrossAxisAlignment.START,
        )
        self.alignment = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        self.vertical_alignment = ft.CrossAxisAlignment.START
        
        if is_user:
            self.controls = [self.bubble_wrapper, self.avatar]
        else:
            self.controls = [self.avatar, self.bubble_wrapper]


        
        
class MainColumn(ft.Column):
    def __init__(self):
        super().__init__()
        self.input_control_ui = InputControl()
        self.controls = [
            ft.Text("Chat History Area", size=20, expand=True),
            self.input_control_ui
        ]


def model_response_stream(text = "hello"):
    import time
    for char in text:
        time.sleep(0.01)        
        yield char


def main(page: ft.Page):
    page.title = "Chat"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = font_config 
    page.theme = ft.Theme(font_family="GeminiFont" if "GeminiFont" in page.fonts else "sans-serif")
    print(page.theme)
    

    chat_messages = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )
    def send_message_click(text):
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        new_message = ft.Container(
            ChatRow(chat_value = text, character="user",dark_mode=is_dark, window_width=page.window.width),
            border_radius=5,
        )
        chat_messages.controls.append(new_message)
        
        
        model_response = ft.Container(
            ChatRow(chat_value = f"", character="llm",dark_mode=is_dark, window_width=page.window.width),
            border_radius=5,
        )

        chat_messages.controls.append(model_response)
        page.update()
        for char in model_response_stream(f"Your question is \'{text}\'"):
            model_response.content.text_content.value += char
            model_response.update()

    def handle_resize(e):
        for chat in chat_messages.controls:
            chat.content.bubble_wrapper.width = page.window.width * 0.7
            chat.update()

    input_control_color = ft.Colors.BLACK12 if page.theme_mode.value == "dark" else ft.Colors.GREY_100
    input_control = ft.Container(
            content = InputControl(on_send=send_message_click), 
            alignment=ft.alignment.bottom_center,
            padding=10,
            margin=10,
            border_radius=10,
            bgcolor=input_control_color,
            
        )
    
    def change_theme(e):
        if page.theme_mode.value == "dark":
            page.theme_mode = ft.ThemeMode.LIGHT
            e.control.icon = ft.Icons.DARK_MODE
            e.control.icon_color = ft.Colors.BLACK
            input_control.bgcolor = ft.Colors.GREY_200
            input_control.content.input_box.bgcolor = ft.Colors.GREY_100
            input_control.content.send_btn.icon_color = ft.Colors.BLACK
            for chat in chat_messages.controls:
                chat.content.bubble.bgcolor = ft.Colors.GREY_100
                chat.content.text_content.color = ft.Colors.BLACK
                chat.content.avatar.content.color = ft.Colors.WHITE
                chat.content.avatar.bgcolor = ft.Colors.BLUE_400
            page.update()

        elif page.theme_mode.value == "light":
            page.theme_mode = ft.ThemeMode.DARK
            e.control.icon = ft.Icons.LIGHT_MODE
            e.control.icon_color = ft.Colors.WHITE
            input_control.bgcolor = ft.Colors.GREY_700
            input_control.content.input_box.bgcolor = ft.Colors.GREY_600
            input_control.content.send_btn.icon_color = ft.Colors.WHITE
            for chat in chat_messages.controls:
                chat.content.bubble.bgcolor = ft.Colors.BLACK38
                chat.content.text_content.color = ft.Colors.WHITE
                chat.content.avatar.content.color = ft.Colors.BLACK
                chat.content.avatar.bgcolor = ft.Colors.WHITE
            page.update()



    setting = ft.IconButton(
        icon = ft.Icons.LIGHT_MODE,
        on_click=change_theme,
        icon_color=ft.Colors.BLACK if page.theme_mode.value == "light" else ft.Colors.WHITE
    )

    
    main_column = ft.Column(
            controls=[
                chat_messages,
                input_control
            ],
            expand=True
        )
        
    page.add(setting)
    page.add(main_column)
    page.on_resized = handle_resize
    
    

ft.app(main)
