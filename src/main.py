import flet as ft
from config.config import font_config
from components.chat_llm import chat_stream, get_model,chat_stream_new
import asyncio
import threading

CHAT_MAX_WIDTH = 900

class InputControl(ft.Row):
    def __init__(self, page: ft.Page,on_send, dark_model = False):
        super().__init__()
        self.theme = "dark" if dark_model else "light"
        self.page = page

        self.is_generating = False
        self.stop_requested = False

        self.input_box_color = ft.Colors.BLACK12 if self.theme == "dark" else ft.Colors.WHITE
        self.send_icon_color = ft.Colors.GREY_100 if self.theme == "dark" else ft.Colors.BLACK
        self.input_box = ft.TextField(
                hint_text="Ask anything", 
                expand=True,
                shift_enter=True,
                border_radius=10,
                on_submit=self.handle_send,
                bgcolor = self.input_box_color,
                color = ft.Colors.BLACK,
                focused_border_color=ft.Colors.GREY_400
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
        #print(self.is_generating)
        if self.is_generating:
            self.stop_requested = True
            return
        
        text = self.input_box.value.strip()
        if not text:
            return
        
        self.input_box.value = ""
        self.is_generating = True
        self.stop_requested = False
        self.send_btn.icon = ft.Icons.STOP
        self.update()
        self.on_send(text)

class ChatRow(ft.Row):
    def __init__(self, page: ft.Page,chat_value=None, character="user", dark_mode = False, window_width = 1000):
        super().__init__()
        self.window_width = window_width
        self.character = character
        self.dark_mode = dark_mode
        self.page = page
        is_user = self.character == "user"


        self.copy_btn = ft.IconButton(
            icon=ft.Icons.CONTENT_COPY,
            tooltip="Copy",
            icon_size=16, 
            on_click=self.copy_text,
            visible=False
            
        )

        self.thumbup_btn = ft.IconButton(
            icon = ft.Icons.THUMB_UP,
            tooltip="thumb up",
            icon_size=16, 
            #on_click=self.copy_text,
            visible=False
        )

        self.thumbdown_btn = ft.IconButton(
            icon = ft.Icons.THUMB_DOWN,
            tooltip="thumb down",
            icon_size=16, 
            #on_click=self.copy_text,
            visible=False
        )

        self.actions = ft.Row(
            controls = [
                self.copy_btn,
                self.thumbup_btn,
                self.thumbdown_btn
            ],
            tight=True,
            spacing=4,
            visible=False
        )

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

        self.text_content = ft.Markdown(
            value=chat_value,
            extension_set="gitHubWeb", 
            #color=self.text_color, 
            selectable=True,
            #weight=ft.FontWeight.W_400,
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
            border_radius=20,  
        )
        
        def get_max_width():
            return self.window_width * 0.7
    
        self.bubble_wrapper = ft.Column(
            controls=[self.bubble, self.actions],   
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
            
    def copy_text(self, e):
        text = self.text_content.value or ""
        self.page.set_clipboard(text)

        
        
class MainColumn(ft.Column):
    def __init__(self):
        super().__init__()
        self.input_control_ui = InputControl()
        self.controls = [
            ft.Text("Chat History Area", size=20, expand=True),
            self.input_control_ui
        ]


def model_response_stream(prompt = "hello", **kargs):
    import time
    time.sleep(1)# fake model thinking
    for char in f"Your prompt is: {prompt}":
        yield char
        time.sleep(0.01)


def main(page: ft.Page):
    page.title = "Chat"
    
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = font_config 
    page.theme = ft.Theme(font_family="GeminiFont" if "GeminiFont" in page.fonts else "sans-serif")
    current_model = get_model()
    model = current_model.get('model')
    key = current_model.get('key')

    
    chat_messages = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )
    def send_message_click(text):

        is_dark = page.theme_mode == ft.ThemeMode.DARK
        new_message = ft.Container(
            ChatRow(page = page, chat_value = text, character="user",dark_mode=is_dark, window_width=page.window.width),
            border_radius=5,
        )
        chat_messages.controls.append(new_message)
        #input_control.content.send_btn.icon = ft.Icons.STOP
        
        
        model_response = ft.Container(
            ChatRow(page = page, chat_value = f"", character="llm",dark_mode=is_dark, window_width=page.window.width),
            border_radius=5,
            
        )
        chat_messages.controls.append(model_response)
        #input_control.is_generating = True
        page.update()


        def worker():
            for part in model_response_stream(text, model = model, key = key):
                if input_control.content.stop_requested:
                    break
                model_response.content.text_content.value += part
                model_response.content.text_content.update()
                chat_messages.scroll_to(offset=-1, duration=100)
                
                
            model_response.content.actions.visible = True
            model_response.content.thumbup_btn.visible = True
            model_response.content.thumbdown_btn.visible = True
            model_response.content.copy_btn.visible = True

            input_control.content.is_generating = False
            input_control.content.stop_requested = False
            input_control.content.send_btn.icon = ft.Icons.SEND

            page.update()

        threading.Thread(target=worker, daemon=True).start()
        
        page.update()

    def handle_resize(e):
        for chat in chat_messages.controls:
            chat.content.bubble_wrapper.width = page.window.width * 0.7
            chat.update()


    input_control_color = ft.Colors.BLACK12 if page.theme_mode.value == "dark" else ft.Colors.GREY_100
    input_control = ft.Container(
            content = InputControl(page=page,on_send=send_message_click), 
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
            input_control.bgcolor = ft.Colors.WHITE
            input_control.content.input_box.bgcolor = ft.Colors.WHITE
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
    chat_layout = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        expand = True,
        controls=[
            ft.Container(
                width=CHAT_MAX_WIDTH,
                content = main_column
            )
        ],
        
    )
        
    page.add(setting)
    page.add(main_column)
    
    page.on_resized = handle_resize
    
    

ft.app(main)
