import base64
import io
import os
import random
from tkinter import filedialog
from customtkinter import *
from PIL import Image, ImageDraw


class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()
        self.username = None
        self.title('Приєднатися до чату')
        self.geometry('300x300')
        self.resizable(False, False)

        CTkLabel(self, text='Вхід в LogiTalk (Демо)', font=('Arial', 20, 'bold')).pack(pady=40)
        self.name_entry = CTkEntry(self, placeholder_text='Введіть імʼя')
        self.name_entry.pack(pady=10)

        # Поля хосту/порту залишено для візуальної схожості, але вони заблоковані
        self.host_entry = CTkEntry(self, placeholder_text='localhost (Імітація)')
        self.host_entry.configure(state="disabled")
        self.host_entry.pack(pady=5)
        
        self.submit_button = CTkButton(self, text='Увійти в чат', command=self.start_chat)
        self.submit_button.pack(pady=15)

    def start_chat(self):
        self.username = self.name_entry.get().strip()
        if not self.username:
            self.username = "Гість"
            
        self.destroy()
        # Відкриваємо головне вікно без реального сокету
        win = MainWindow(username=self.username)
        win.mainloop()


class MainWindow(CTk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        
        # Створюємо дефолтну аватарку (заглушку), якщо користувач не обрав свою
        self.user_avatar = self.create_default_avatar("👤")

        self.geometry('500(' if self.winfo_screenwidth() > 600 else '450') # трохи розширив для зручності
        self.geometry('500x400')
        self.title("LogiTalk Chat Simulator")

        # Бічне Меню
        self.menu_frame = CTkFrame(self, width=30, height=400, fg_color="#2b2b2b")
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -20
        
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        # Елементи всередині меню (створюємо одразу, керуємо видимістю)
        self.menu_content_frame = CTkFrame(self.menu_frame, fg_color="transparent")
        
        self.avatar_label = CTkLabel(self.menu_content_frame, text="", image=self.user_avatar)
        self.btn_change_avatar = CTkButton(self.menu_content_frame, text="Змінити фото", command=self.change_avatar, width=120)
        
        self.label = CTkLabel(self.menu_content_frame, text='Ваш нікнейм:', font=('Arial', 12, 'bold'))
        self.entry = CTkEntry(self.menu_content_frame, placeholder_text="Новий нік...")
        self.save_button = CTkButton(self.menu_content_frame, text="Зберегти", command=self.save_name, width=120)

        # Основне поле чату
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        # Поле введення та кнопки
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)
        
        # Кнопка відправки тексту за допомогою Enter
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.open_img_button = CTkButton(self, text='📂', width=50, height=40, command=self.open_image)
        self.open_img_button.place(x=0, y=0)

        # Початкове системне повідомлення
        self.add_message(f"[SYSTEM]: Ви приєдналися як {self.username}!")
        
        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu = -20
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu = 20
            self.btn.configure(text='◀️')
            
            # Оновлюємо дані в інпутах перед показом
            self.entry.delete(0, END)
            self.entry.insert(0, self.username)
            self.avatar_label.configure(image=self.user_avatar)
            
            self.menu_content_frame.pack(pady=40, padx=10, fill="both", expand=True)
            self.avatar_label.pack(pady=5)
            self.btn_change_avatar.pack(pady=5)
            self.label.pack(pady=10)
            self.entry.pack(pady=5)
            self.save_button.pack(pady=10)
            
            self.show_menu()

    def show_menu(self):
        current_width = self.menu_frame.winfo_width()
        new_width = current_width + self.speed_animate_menu
        
        # Обмеження меж анімації (від 30 до 200 пікселів)
        if self.is_show_menu and new_width <= 200:
            self.menu_frame.configure(width=new_width)
            self.after(10, self.show_menu)
        elif not self.is_show_menu and new_width >= 30:
            self.menu_frame.configure(width=new_width)
            self.after(10, self.show_menu)
        else:
            # Фіксація кінцевих станів
            if self.is_show_menu:
                self.menu_frame.configure(width=200)
            else:
                self.menu_frame.configure(width=30)
                self.menu_content_frame.pack_forget()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name and new_name != self.username:
            old_name = self.username
            self.username = new_name
            self.add_message(f"[SYSTEM]: {old_name} змінив(ла) нік на {self.username}")
            self.toggle_show_menu()
            
            # Імітація реакції ботів
            self.after(1000, lambda: self.simulate_bot_response("system_change"))

    def change_avatar(self):
        file_name = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.bmp")])
        if file_name:
            try:
                pil_img = Image.open(file_name)
                self.user_avatar = CTkImage(pil_img, size=(80, 80))
                self.avatar_label.configure(image=self.user_avatar)
                self.add_message(f"[SYSTEM]: Ви оновили аватарку профілю.")
            except Exception as e:
                print(f"Помилка завантаження аватарки: {e}")

    def create_default_avatar(self, text):
        # Проста генерація кольорового квадрату з іконкою
        img = Image.new('RGB', (80, 80), color='#1f6aa5')
        return CTkImage(img, size=(80, 80))

    def adaptive_ui(self):
        menu_w = self.menu_frame.winfo_width()
        win_w = self.winfo_width()
        win_h = self.winfo_height()

        self.menu_frame.configure(height=win_h)
        self.chat_field.place(x=menu_w)
        self.chat_field.configure(width=win_w - menu_w - 10, height=win_h - 50)
        
        self.send_button.place(x=win_w - 55, y=win_h - 45)
        self.open_img_button.place(x=win_w - 110, y=win_h - 45)
        
        self.message_entry.place(x=menu_w + 5, y=win_h - 45)
        self.message_entry.configure(width=win_w - menu_w - 120)

        self.after(50, self.adaptive_ui)

    def add_message(self, message, img=None):
        # Визначаємо колір фону залежно від того, хто пише
        if "[SYSTEM]" in message:
            bg_color = '#3e3e3e'
        elif message.startswith(f"{self.username}:"):
            bg_color = '#1f6aa5'  # Ваш колір (синій)
        else:
            bg_color = '#4a4a4a'  # Колір ботів (сірий)

        message_frame = CTkFrame(self.chat_field, fg_color=bg_color)
        
        # Вирівнювання: ваші повідомлення праворуч, боти/система — ліворуч
        if message.startswith(f"{self.username}:"):
            message_frame.pack(pady=5, padx=10, anchor='e')
        else:
            message_frame.pack(pady=5, padx=10, anchor='w')
            
        wrapleng_size = max(200, self.winfo_width() - self.menu_frame.winfo_width() - 60)

        if not img:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                     text_color='white', justify='left').pack(padx=10, pady=5)
        else:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                     text_color='white', image=img, compound='top',
                     justify='left').pack(padx=10, pady=5)
            
        # Автоматичний скролл вниз при новому повідомленні
        self.chat_field._parent_canvas.yview_moveto(1.0)

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            self.add_message(f"{self.username}: {message}")
            self.message_entry.delete(0, END)
            
            # Емуляція затримки відповіді "інших користувачів"
            self.after(random.randint(800, 2000), lambda: self.simulate_bot_response("text"))

    def open_image(self):
        file_name = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.gif")])
        if not file_name:
            return
        try:
            # Локально відображаємо картинку у себе в чаті
            pil_img = Image.open(file_name)
            ctk_img = CTkImage(pil_img, size=(250, 200))
            
            self.add_message(f"{self.username} надіслав(ла) зображення:", img=ctk_img)
            
            # Імітуємо реакцію ботів на картинку
            self.after(1500, lambda: self.simulate_bot_response("image"))
        except Exception as e:
            self.add_message(f"[SYSTEM]: Не вдалося відкрити зображення: {e}")

    # --- СЕКЦІЯ ІМІТАЦІЇ БОТІВ ---
    def simulate_bot_response(self, event_type):
        bots = ["Олександр", "Марія", "Дмитро_IT", "Кіт_Вчений"]
        bot_name = random.choice(bots)
        
        bot_phrases = [
            "Круто! 👍", "Привіт усім!", "LogiTalk працює чудово навіть без серверів) 😎",
            "Які плани на сьогодні?", "Цікава думка...", "Ахаха, життєво!", "++"
        ]
        bot_img_phrases = ["Ого, гарне фото!", "Де це знято?", "Класний кадр! ✨", "Вау! 😍"]
        bot_system_phrases = ["О, новий нік топовий!", "Будемо знати)", "Записав собі в контакти."]

        if event_type == "text":
            phrase = random.choice(bot_phrases)
            self.add_message(f"{bot_name}: {phrase}")
            
        elif event_type == "image":
            phrase = random.choice(bot_img_phrases)
            self.add_message(f"{bot_name}: {phrase}")
            
            # Іноді бот може кинути картинку у відповідь
            if random.random() > 0.5:
                self.after(1000, self.bot_sends_fake_image)
                
        elif event_type == "system_change":
            phrase = random.choice(bot_system_phrases)
            self.add_message(f"{bot_name}: {phrase}")

    def bot_sends_fake_image(self):
        bots = ["Марія", "Дмитро_IT", "Кіт_Вчений"]
        bot_name = random.choice(bots)
        
        # Створюємо абстрактну генеративну картинку (кольоровий стікер), щоб не залежати від локальних файлів
        colors = ["#ff5733", "#33ff57", "#3357ff", "#f333ff", "#fff333"]
        img = Image.new('RGB', (200, 200), color=random.choice(colors))
        d = ImageDraw.Draw(img)
        d.text((50, 90), "STIKER_BOT", fill="white")
        
        ctk_img = CTkImage(img, size=(200, 200))
        self.add_message(f"{bot_name} надіслав(ла) стікер:", img=ctk_img)


if __name__ == "__main__":
    # Налаштування темної теми customtkinter
    set_appearance_mode("dark")
    set_default_color_theme("blue")
    
    app = RegisterWindow()
    app.mainloop()