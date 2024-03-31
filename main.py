# librerias utilizadas
import tkinter as tk # Para la GUI
from tkinter import ttk # Para la GUI
from tkinter import PhotoImage # Para la GUI
from tkinter import messagebox # Para la GUI
import time # Para el tiempo
import subprocess # Abrir apps
import webbrowser # Abrir sitios web
import cv2 # Para la cámara
import mediapipe as mp # Para la detección de manos
import mediapipe as mp # Para la detección de manos
import numpy as np # Para la detección de manos
import pyautogui # Para el control del mouse
import threading # Para los subprocesos

# Constantes
fontGUI = "Times New Roman"
colorMain = "light blue"

# Variables globales
state = True

# Centrar la ventana
def centrar_ventana(ventana):
    ventana.update_idletasks() # Actualizar la ventana
    ancho_ventana = ventana.winfo_width()
    alto_ventana = ventana.winfo_height()
    x_ubicacion = (ventana.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_ubicacion = (ventana.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana.geometry('{}x{}+{}+{}'.format(ancho_ventana, alto_ventana, x_ubicacion, y_ubicacion))

def mouse_control():
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    color_mouse_pointer = (255, 0, 255)

    # Rectangulo donde se moverá el mouse (en pixeles y considerando una resolucion FULL HD)
    SCREEN_GAME_X_INI = 480
    SCREEN_GAME_Y_INI = 270
    SCREEN_GAME_X_FIN = 480 + 960
    SCREEN_GAME_Y_FIN = 270 + 540

    X_Y_INI = 100 # Distancia del rectangulo a los bordes de la pantalla

    # Función para calcular la distancia entre dos puntos
    def calculate_distance(x1, y1, x2, y2):
        p1 = np.array([x1, y1])
        p2 = np.array([x2, y2])
        return np.linalg.norm(p1 - p2)

    # Función para detectar si el dedo índice está hacia abajo
    def detect_finger_down(hand_landmarks):
        finger_down = False
        color_base = (255, 0, 112)
        color_index = (255, 198, 82)

        # Coordenadas de los puntos de interes
        x_base1 = int(hand_landmarks.landmark[0].x * width)
        y_base1 = int(hand_landmarks.landmark[0].y * height)

        x_base2 = int(hand_landmarks.landmark[9].x * width)
        y_base2 = int(hand_landmarks.landmark[9].y * height)

        x_index = int(hand_landmarks.landmark[8].x * width)
        y_index = int(hand_landmarks.landmark[8].y * height)

        # Calculo de las distancias
        d_base = calculate_distance(x_base1, y_base1, x_base2, y_base2)
        d_base_index = calculate_distance(x_base1, y_base1, x_index, y_index)

        # Si la distancia entre el dedo índice y la base es menor a la distancia entre los dos puntos de la base, el dedo índice está hacia abajo
        if d_base_index < d_base:
            finger_down = True
            color_base = (255, 0, 255)
            color_index = (255, 0, 255)

        # Dibujar los puntos y las lineas
        cv2.circle(output, (x_base1, y_base1), 5, color_base, 2)
        cv2.circle(output, (x_index, y_index), 5, color_index, 2)
        cv2.line(output, (x_base1, y_base1), (x_base2, y_base2), color_base, 3)
        cv2.line(output, (x_base1, y_base1), (x_index, y_index), color_index, 3)

        # Devolver el estado del dedo índice
        return finger_down

    # Ciclo principal
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5) as hands:

        while state:
            ret, frame = cap.read()
            if ret == False:
                break

            height, width, _ = frame.shape
            frame = cv2.flip(frame, 1)

            # Dibujar el rectangulo
            area_width = width - X_Y_INI * 2
            area_height = int(area_width / (SCREEN_GAME_X_FIN - SCREEN_GAME_X_INI) * (SCREEN_GAME_Y_FIN - SCREEN_GAME_Y_INI))
            aux_image = np.zeros(frame.shape, np.uint8)
            aux_image = cv2.rectangle(aux_image, (X_Y_INI, X_Y_INI), (X_Y_INI + area_width, X_Y_INI + area_height), (255, 0, 0), -1)
            output = cv2.addWeighted(frame, 1, aux_image, 0.7, 0)

            # Detección de las manos
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(frame_rgb)
            
            # Dibujar el mouse pointer
            if results.multi_hand_landmarks is not None:
                for hand_landmarks in results.multi_hand_landmarks:
                    x = int(hand_landmarks.landmark[9].x * width)
                    y = int(hand_landmarks.landmark[9].y * height)
                    xm = np.interp(x, (X_Y_INI, X_Y_INI + area_width), (SCREEN_GAME_X_INI, SCREEN_GAME_X_FIN))
                    ym = np.interp(y, (X_Y_INI, X_Y_INI + area_height), (SCREEN_GAME_Y_INI, SCREEN_GAME_Y_FIN))
                    pyautogui.moveTo(int(xm), int(ym))
                    if detect_finger_down(hand_landmarks):
                        pyautogui.click()
                    cv2.circle(output, (x, y), 10, color_mouse_pointer, 3)
                    cv2.circle(output, (x, y), 5, color_mouse_pointer, -1)

            # cv2.imshow('output', output)
            # Cancelar el ciclo con la tecla ESC
            if cv2.waitKey(1) & 0xFF == 27:
                break
    # Liberar la cámara
    cap.release()
    cv2.destroyAllWindows()


# Ventana del navegador
def win_inter():
    # Función para regresar
    def regret():
        win_main.deiconify()
        win_inter.destroy()

    # Función para ir a la URL
    def ir():
        if txt_url.get() == "":
            messagebox.showinfo("Info", "Ingrese una URL")
        elif ".com" not in txt_url.get() and ".co" not in txt_url.get() and ".org" not in txt_url.get() and ".net" not in txt_url.get() and ".edu" not in txt_url.get() and ".gov" not in txt_url.get():
            messagebox.showinfo("Info", "Ingrese una URL válida")
        else:
            webbrowser.open_new(txt_url.get())

    # Ventana de interacción
    win_main.withdraw()
    win_inter = tk.Toplevel()
    win_inter.title("withoutMouse system")
    win_inter.geometry("960x480")
    win_inter.resizable(False, False)
    win_inter.config(bg=colorMain)
    win_inter.iconbitmap("./images/hand.ico")
    centrar_ventana(win_inter)

    # Etiquetas
    lbl_title = tk.Label(win_inter, text="Navegar por internet", font=(fontGUI, 30), bg=colorMain, justify="center")
    lbl_subtitle = tk.Label(win_inter, text="Ingresa la URL del sitio web", font=(fontGUI, 15), bg=colorMain, justify="center")

    # Posicionamiento de las etiquetas
    lbl_title.place(x=0, y=0, width=960, height=100)
    lbl_subtitle.place(x=0, y=100, width=960, height=50)

    # Entradas
    txt_url = tk.Entry(win_inter, font=(fontGUI, 15), justify="center")

    # Posicionamiento de las entradas
    txt_url.place(x=75, y=170, width=810, height=80)

    # Botones
    btn_go = tk.Button(win_inter, text="Ir", font=(fontGUI, 20), bd=0, bg="tomato", fg="white", cursor = "hand2", command=lambda:ir())
    btn_back = tk.Button(win_inter, text="Regresar", font=(fontGUI, 20), bd=0, bg="green", fg="white", cursor = "hand2", command=lambda:regret())

    # Posicionamiento de los botones
    btn_go.place(x=400, y=280, width=160, height=80)
    btn_back.place(x=0, y=400, width=960, height=80)

# Ventana del contador
def counter():
    # Variables globales
    global count
    count = 0

    # Función para regresar
    def regret():
        win_main.deiconify()
        win_counter.destroy()

    def sumar():
        global count
        count += 1
        lbl_count.config(text=count)

    def restar():
        global count
        count -= 1
        if count < 0:
            count = 0
        lbl_count.config(text=count)

    # Ventana del contador
    win_main.withdraw()
    win_counter = tk.Toplevel()
    win_counter.title("withoutMouse system")
    win_counter.geometry("960x480")
    win_counter.resizable(False, False)
    win_counter.config(bg=colorMain)
    win_counter.iconbitmap("./images/hand.ico")
    centrar_ventana(win_counter)

    # Etiquetas
    lbl_title = tk.Label(win_counter, text="Contador", font=(fontGUI, 30), bg=colorMain, justify="center")
    lbl_subtitle = tk.Label(win_counter, text="Sumale o restale 1 al contador", font=(fontGUI, 15), bg=colorMain, justify="center")
    lbl_count = tk.Label(win_counter, text=count, font=(fontGUI, 50), bg=colorMain, justify="center")

    # Posicionamiento de las etiquetas
    lbl_title.place(x=0, y=0, width=960, height=100)
    lbl_subtitle.place(x=0, y=100, width=960, height=50)
    lbl_count.place(x=380, y=220, width=200, height=100)

    # Botones
    btn_sumar = tk.Button(win_counter, text="+", font=(fontGUI, 60),fg="black",bg=colorMain, bd=0, cursor = "hand2", command=lambda:sumar())
    btn_restar = tk.Button(win_counter, text="-", font=(fontGUI, 60),fg="black",bg=colorMain, bd=0, cursor = "hand2", command=lambda:restar())
    btn_back = tk.Button(win_counter, text="Regresar", font=(fontGUI, 20), bd=0, bg="green", fg="white", cursor = "hand2", command=lambda:regret())

    # Posicionamiento de los botones
    btn_restar.place(x=160, y=220, width=200, height=100)
    btn_sumar.place(x=600, y=220, width=200, height=100)
    btn_back.place(x=0, y=400, width=960, height=80)

# Subproceso para el control del mouse
thread1 = threading.Thread(target=mouse_control)

# Ventana principal
win_main = tk.Tk()

# Configuración de la ventana principal
win_main.title("withoutMouse system")
win_main.geometry("960x480")
win_main.resizable(False, False)
# win_main.overrideredirect(True) # Eliminar la barra de título
win_main.config(bg=colorMain)
win_main.iconbitmap("./images/hand.ico")
centrar_ventana(win_main)

# Imagenes
img_note = tk.PhotoImage(file="./images/note.png")
img_note = img_note.subsample(3)
img_calc = tk.PhotoImage(file="./images/calc.png")
img_calc = img_calc.subsample(3)
img_inter = tk.PhotoImage(file="./images/inter.png")
img_inter = img_inter.subsample(3)
img_counter = tk.PhotoImage(file="./images/contador.png")
img_counter = img_counter.subsample(3)

# Etiquetas
lbl_title = tk.Label(win_main, text="Bienvenid@", font=(fontGUI, 30), bg=colorMain, justify="center")
lbl_menu = tk.Label(win_main, text="Seleciona una de las siguientes opciones", font=(fontGUI, 20), bg=colorMain, justify="center")

# Posicionamiento de las etiquetas
lbl_title.place(x=0, y=0, width=960, height=100)
lbl_menu.place(x=0, y=100, width=960, height=50)

# Botones
btn_note = tk.Button(win_main,image = img_note, bg = colorMain, bd=0, cursor = "hand2", command=lambda:note())
btn_calc = tk.Button(win_main,image = img_calc, bg = colorMain, bd=0, cursor = "hand2", command=lambda:calc())
btn_inter = tk.Button(win_main,image = img_inter, bg = colorMain, bd=0, cursor = "hand2", command=lambda:win_inter())
btn_counter = tk.Button(win_main,image = img_counter, bg = colorMain, bd=0, cursor = "hand2", command=lambda:counter())
btn_exit = tk.Button(win_main, text="Exit", font=(fontGUI, 20), bd=0, bg="red", fg="white", cursor = "hand2", command=lambda:win_main.destroy())

# Posicionamiento de los botones
btn_note.place(x=32, y=170, width=200, height=200)
btn_calc.place(x=264, y=170, width=200, height=200)
btn_inter.place(x=496, y=170, width=200, height=200)
btn_counter.place(x=728, y=170, width=200, height=200)
btn_exit.place(x=0, y=400, width=960, height=80)

# Ejecucion de apps
def note():
    btn_note.config(state="disabled")
    time.sleep(2)
    subprocess.Popen("notepad.exe")
    btn_note.config(state="normal")

def calc():
    btn_calc.config(state="disabled")
    time.sleep(2)
    subprocess.Popen("calc.exe")
    btn_calc.config(state="normal")

# Ejecuta el control del mouse si no está ejecutandose
if state == True and not thread1.is_alive():
    thread1.start()

# Ejecución de la ventana principal
win_main.mainloop()

# Detiene el control del mouse
state = False
thread1.join()