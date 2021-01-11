from tkinter import ttk
from tkinter import *
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from random import random

class Clients:
    # connection dir property
    db_name = 'dbClients.db'
    def __init__(self, window):

        # Initializations
        self.wind = window
        self.wind.title('Клиенты')

        #create main menu
        main_menu = Menu()
        settings_menu = Menu(tearoff=0)
        file_menu = Menu(tearoff=0)
        settings_menu.add_command(label="Настроить параметр \"вид сделки\" ", command = self.edit_Kind_klient)
        file_menu.add_command(label="Выйти из приложения", command = self.wind.destroy)
        main_menu.add_cascade(label="Файл", menu=file_menu)
        main_menu.add_cascade(label="Настройки", menu=settings_menu)
        self.wind.config(menu=main_menu)

        #create Notebook
        self.tab_control = ttk.Notebook(self.wind)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='Клиент')
        #self.tab_control.add(self.tab3, text='Недвижимость')
        self.tab_control.add(self.tab2, text='Статистика')
        self.tab_control.pack(expand=1, fill='both')

        # Creating a Frame Container
        frame = LabelFrame(self.tab1, text = 'Детальная информация')
        frame.grid(row = 0, column = 0, columnspan = 5, pady = 20)

        # FIO Input
        Label(frame, text = 'ФИО: ').grid(row = 1, column = 0)
        self.FIO = Entry(frame)
        self.FIO.focus()
        self.FIO.grid(row = 1, column = 1, columnspan=2)

        # NumberTelephone Input
        Label(frame, text = 'Номер Телефона: ').grid(row = 2, column = 0)
        self.NumberTelephone = Entry(frame)
        self.NumberTelephone.grid(row = 2, column = 1, columnspan=2)

        # KindClient Input
        Label(frame, text = 'Вид сделки: ').grid(row = 3, column = 0)
        self.KindClientcombobox = ttk.Combobox(frame,height=6)
        self.KindClientcombobox['value'] = self.get_query('SELECT vidclienta FROM KindClient')
        self.KindClientcombobox.current(newindex=0)
        self.KindClientcombobox.grid(row = 3, column = 1, columnspan=2)

        # Button Add Product
        ttk.Button(frame, text = 'Сохранить', command = self.add_client).grid(row = 4, columnspan = 3, sticky = W + E)

        # Output Messages
        self.message = Label(self.tab1,text = '', fg = 'red')
        self.message.grid(row = 5, column = 0, columnspan = 2, sticky = W + E)

        # Table
        self.tree = ttk.Treeview(self.tab1,height = 15)
        self.tree["columns"] = ("#0", "#1","#2","#3")
        self.tree.column("#0", width=250, anchor="center")
        self.tree.column("#1", width=250, anchor="center")
        self.tree.column("#2", width=200, anchor="center")
        self.tree.heading("#0", text="ФИО")
        self.tree.heading("#1", text="Номер телефона")
        self.tree.heading("#2", text="Вид сделки")
        self.tree["displaycolumns"] = ("#0","#1")
        self.tree.grid(row = 6, column = 0, columnspan = 3)

        # Buttons
        ttk.Button(self.tab1,text = 'Удалить', command = self.delete_client).grid(row = 7, column = 0, sticky = W + E)
        ttk.Button(self.tab1,text = 'Редактировать', command = self.edit_client).grid(row = 7, column = 1, columnspan=2, sticky = W + E)

        # Filling the Rows
        self.get_clients()

        ttk.Button(self.tab2,text = 'Показать график', command = self.barplot).grid(padx = 20, pady =20)

    # Function to Execute Database Querys
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    # Get Products from Database
    def get_clients(self):
        # cleaning Table
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        # getting data
        query = 'SELECT * FROM clients'
        db_rows = self.run_query(query)
        # filling data
        for row in db_rows:
            self.tree.insert('', 0, text = row[1], values = (row[2],self.get_queryWithParametrs('SELECT vidclienta FROM KindClient WHERE id = ?',(row[3],))[0],row[0]))

    def get_query(self,query):
        res = []
        result_query = self.run_query(query)
        for row in result_query.fetchall():
            res.append(row[0])
        return res

    def get_queryWithParametrs(self,query,parametrs):
        res = []
        result_query = self.run_query(query,parametrs)
        for row in result_query.fetchall():
            res.append(row[0])
        return res

    # User Input Validation
    def validation(self):
        return len(self.FIO.get()) != 0 and len(self.NumberTelephone.get()) != 0

    def add_client(self):
        if self.validation():
            query = 'INSERT INTO clients VALUES(NULL, ?, ?, ?)'
            parameters =  (self.FIO.get(), self.NumberTelephone.get(), self.get_queryWithParametrs('SELECT id FROM KindClient WHERE vidclienta = ?', (self.KindClientcombobox.get(),))[0])
            self.run_query(query, parameters)
            self.message['text'] = 'Клиент {} добавлен успешно'.format(self.FIO.get())
            self.FIO.delete(0, END)
            self.NumberTelephone.delete(0, END)
        else:
            self.message['text'] = 'Вы не заполнили необходимые поля!(ФИО, НОМЕР ТЕЛЕФОНА)'
        self.get_clients()

    def delete_client(self):
        self.message['text'] = ''
        try:
           self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Пожалуйста выберите запись'
            return
        self.message['text'] = ''
        FIO = self.tree.item(self.tree.selection())['text']
        idClient = self.tree.item(self.tree.selection())['values'][2]
        query = 'DELETE FROM clients WHERE id = ?'
        self.run_query(query, (idClient,))
        self.message['text'] = 'Запись {} удалена успешно'.format(FIO)
        self.get_clients()

    def edit_client(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Пожалуйста, выберите запись'
            return
        idClient         = self.tree.item(self.tree.selection())['values'][2]
        FIO              = self.get_queryWithParametrs('SELECT FIO FROM clients WHERE id = ?',(idClient,))[0]
        NumberTelephone  = self.get_queryWithParametrs('SELECT NumberTelephone FROM clients WHERE id = ?',(idClient,))
        KindClient       = self.get_queryWithParametrs('SELECT KindClient FROM clients WHERE id = ?',(idClient,))[0]
        self.edit_wind = Toplevel()
        self.edit_wind.title('Edit Client')
        # Old FIO
        Label(self.edit_wind, text = 'ФИО:').grid(row = 0, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = FIO), state = 'readonly').grid(row = 0, column = 2)
        # New FIO
        Label(self.edit_wind, text = '(НОВЫЙ) фио:').grid(row = 1, column = 1)
        new_FIO = Entry(self.edit_wind)
        new_FIO.grid(row = 1, column = 2)

        # Old NumberTelephone
        Label(self.edit_wind, text = 'Номер телефона:').grid(row = 2, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = NumberTelephone), state = 'readonly').grid(row = 2, column = 2)
        # New NumberTelephone
        Label(self.edit_wind, text = '(НОВЫЙ) номер телефона:').grid(row = 3, column = 1)
        new_NumberTelephone = Entry(self.edit_wind)
        new_NumberTelephone.grid(row = 3, column = 2)

        # Old KindClient
        Label(self.edit_wind, text = 'Вид сделки:').grid(row = 4, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = self.get_queryWithParametrs('SELECT vidclienta FROM KindClient WHERE id = ?',(KindClient,))[0]), state = 'readonly').grid(row = 4, column = 2)
        # New KindClient
        Label(self.edit_wind, text = '(НОВЫЙ) вид сделки:').grid(row = 5, column = 1)
        KindClientcomboboxEdit = ttk.Combobox(self.edit_wind,height=6)
        KindClientcomboboxEdit['value'] = self.get_query('SELECT vidclienta FROM KindClient')
        KindClientcomboboxEdit.current(newindex=0)
        KindClientcomboboxEdit.grid(row = 5, column = 2)

        Button(self.edit_wind, text = 'Обновить запись', command = lambda: self.edit_records(FIO, new_FIO.get(), new_NumberTelephone.get(), self.get_queryWithParametrs('SELECT id FROM KindClient WHERE vidclienta = ?', (KindClientcomboboxEdit.get(),))[0], idClient)).grid(row = 6, column = 2, sticky = W)
        self.edit_wind.mainloop()

    def edit_records(self, FIO, new_FIO, new_NumberTelephone, new_KindClient, idClient):
        query = 'UPDATE clients SET FIO = ?, NumberTelephone = ?, KindClient = ? WHERE id = ?'
        parameters = (new_FIO, new_NumberTelephone, new_KindClient, idClient)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = 'Запись {} обновлена успешно'.format(FIO)
        self.get_clients()

    def barplot(self):

        #SUM() clients for barplots
        id_list_kind_clients_barplot = self.get_query('SELECT id FROM KindClient')
        query = 'SELECT count(FIO) FROM clients WHERE KindClient = ?'
        query1 = 'SELECT vidclienta FROM KindClient WHERE id = ?'
        bars_height = []
        for i in id_list_kind_clients_barplot:
            bars_height_TEMP = [self.get_queryWithParametrs(query1,(i,))[0],self.get_queryWithParametrs(query,(i,))[0]]
            bars_height.append(bars_height_TEMP)
        # Make a dataset
        height = []
        bars = []
        for i in bars_height:
            height.append(i[1])
            bars.append(i[0])
        y_pos = np.arange(len(bars))
        #plt.bar(y_pos, height, color=['black', 'red', 'green', 'blue', 'cyan'])
        plt.bar(y_pos, height)
        plt.xticks(y_pos, bars)
        plt.yticks(np.arange(0, max(height)+1, step=1))
        plt.ylabel("Количество клиентов")
        plt.title("Зависимость количества клиентов от вида сделки")
        plt.show()

        #number = random.randint(20, 35)

    def center(self,win):
        """
        centers a tkinter window
        :param win: the root or Toplevel window to center
        """
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    def edit_Kind_klient(self):
        self.edit_Kind_klientFORMmain = Toplevel()
        self.edit_Kind_klientFORMmain.title("Виды клиентов")
        self.edit_Kind_klientFORMmain.resizable(False, False)
        self.edit_Kind_klientFORMmain.geometry("400x400")
        self.center(self.edit_Kind_klientFORMmain)

        #TreeView Table Kind klient
        db_rows = self.run_query('SELECT count(id) FROM KindClient')
        for row in db_rows:
            count_id = row[0]
        self.TreeEdit_Kind_klient = ttk.Treeview(self.edit_Kind_klientFORMmain, height = 10)
        self.TreeEdit_Kind_klient["columns"] = ("#0","#1")
        self.TreeEdit_Kind_klient.column("#1", width=150, anchor="center")
        self.TreeEdit_Kind_klient.heading("#0", text="Вид Клиента")
        self.TreeEdit_Kind_klient["displaycolumns"] = ()
        self.TreeEdit_Kind_klient.grid(row = 0, column = 0, columnspan = 2)

        ttk.Button(self.edit_Kind_klientFORMmain, text = 'Удалить', command = self.delet_Kind_clients).grid(row = 1, column = 0, sticky = W + E)
        ttk.Button(self.edit_Kind_klientFORMmain, text = 'Редактировать', command = self.edit_Form_Kind_klients).grid(row = 2, column = 0, sticky = W + E)
        ttk.Button(self.edit_Kind_klientFORMmain, text = 'Добавить', command = lambda : self.add_Form_Kind_klients()).grid(row = 3, column = 0, sticky = W + E)

        # Output Messages
        self.messageEdit_Kind_klient = Label(self.edit_Kind_klientFORMmain,text = '', fg = 'red')
        self.messageEdit_Kind_klient.grid(row = 4, column = 0, columnspan = 2, sticky = W + E)

        self.get_Kind_clients()

        self.edit_Kind_klientFORMmain.mainloop()

    def delet_Kind_clients(self):
        self.messageEdit_Kind_klient['text'] = ''
        try:
            self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['text'][0]
        except IndexError as e:
            self.messageEdit_Kind_klient['text'] = 'Пожалуйста выберите запись'
            return
        self.message['text'] = ''
        Kind_klient = self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['text']
        idKind_klient = self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['values'][0]
        self.run_query('DELETE FROM KindClient WHERE id = ?', (idKind_klient,))
        if self.foreign_key_check():
            self.messageEdit_Kind_klient['text'] = 'Запись {} успешно удалена'.format(Kind_klient)
        else:
            self.run_query('INSERT INTO KindClient VALUES(?, ?)', (idKind_klient,Kind_klient))
            self.messageEdit_Kind_klient['text'] = 'Вид клиента не может быть удален, есть клиенты с такой записью'
        self.update_all_table()

    def get_Kind_clients(self):
        # cleaning Table
        records = self.TreeEdit_Kind_klient.get_children()
        for element in records:
            self.TreeEdit_Kind_klient.delete(element)
        # getting data
        db_rows = self.run_query('SELECT * FROM KindClient')
        # filling data
        for row in db_rows:
            self.TreeEdit_Kind_klient.insert('', 0, text = row[1], values = (row[0]))

    def edit_Form_Kind_klients(self):
        self.messageEdit_Kind_klient['text'] = ''
        try:
            self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['text'][0]
        except IndexError as e:
            self.messageEdit_Kind_klient['text'] = 'Пожалуйста выберите запись'
            return
        self.message['text'] = ''
        Kind_klient = self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['text']
        idKind_klient = self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['values'][0]
        self.edit_Form_Kind_klientsF = Toplevel()
        self.center(self.edit_Form_Kind_klientsF)
        self.edit_Form_Kind_klientsF.title("Редактировать")
        self.edit_Form_Kind_klientsF.resizable(False, False)
        self.edit_Form_Kind_klientsF.geometry("200x200")
        lbl = Label(self.edit_Form_Kind_klientsF,text="Редактировать запись {0}".format(Kind_klient), padx = 20)
        lbl.grid(row =0, column = 0)
        EntEdit_Form = Entry(self.edit_Form_Kind_klientsF)
        EntEdit_Form.grid(row =1, column = 0)
        EntEdit_Form.focus()
        btn = Button(self.edit_Form_Kind_klientsF, text="ОК", command = lambda : self.edit_Kind_clientsFunc(EntEdit_Form.get()))
        btn.grid(row =2, column = 0)
        self.edit_Form_Kind_klientsF.mainloop()

    def add_Form_Kind_klients(self):
        self.message['text'] = ''
        self.add_Form_Kind_klientsF = Toplevel()
        self.center(self.add_Form_Kind_klientsF)
        self.add_Form_Kind_klientsF.title("Добавить")
        self.add_Form_Kind_klientsF.resizable(False, False)
        self.add_Form_Kind_klientsF.geometry("200x200")
        lbl = Label(self.add_Form_Kind_klientsF,text="Добавить запись", padx = 20)
        lbl.grid(row =0, column = 0)
        Entadd_Form = Entry(self.add_Form_Kind_klientsF)
        Entadd_Form.grid(row =1, column = 0)
        Entadd_Form.focus()
        btn = Button(self.add_Form_Kind_klientsF, text="ОК", command = lambda: self.add_Kind_clientsFunc(Entadd_Form.get()))
        btn.grid(row =2, column = 0)
        self.add_Form_Kind_klientsF.mainloop()

    def validation_Kind_clients_Edit(self,EntEdit_Form):
        return len(EntEdit_Form) != 0

    def validation_Kind_clients_Add(self,Entadd_Form):
        return len(Entadd_Form) != 0

    def add_Kind_clientsFunc(self,Entadd_Form):
        self.add_Form_Kind_klientsF.destroy()
        if self.validation_Kind_clients_Add(Entadd_Form):
            query = 'INSERT INTO KindClient VALUES((SELECT count(KindClient.id)+1 FROM KindClient),?)'
            parameters = (Entadd_Form,)
            try:
                self.run_query(query, parameters)
            except:
                self.run_query('INSERT INTO KindClient VALUES((SELECT count(KindClient.id)+2 FROM KindClient),?)', parameters)
            self.messageEdit_Kind_klient['text'] = 'Запись {} успешно добавлена'.format(Entadd_Form)
        else:
            self.messageEdit_Kind_klient['text'] = 'Вы не заполнили необходимое поле!'
        self.update_all_table()



    def edit_Kind_clientsFunc(self,EntEdit_Form):
        self.edit_Form_Kind_klientsF.destroy()
        if self.validation_Kind_clients_Edit(EntEdit_Form):
            query = 'UPDATE KindClient SET vidclienta = ? WHERE id = ?'
            parameters = (EntEdit_Form,self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['values'][0])
            self.run_query(query, parameters)
            self.messageEdit_Kind_klient['text'] = 'Запись {} успешно обновлена'.format(self.TreeEdit_Kind_klient.item(self.TreeEdit_Kind_klient.selection())['text'])
        else:
            self.messageEdit_Kind_klient['text'] = 'Вы не заполнили необходимое поле!'
        self.update_all_table()

    def foreign_key_check(self):
        db_rows = self.run_query('PRAGMA foreign_key_check')
        ErorDelete =[]
        for row in db_rows:
            ErorDelete.append(row)
        if ErorDelete==[]:
            return True
        else:
            return False

    def update_all_table(self):
        self.get_Kind_clients()
        self.get_clients()
        self.KindClientcombobox['value'] = self.get_query('SELECT vidclienta FROM KindClient')
        self.KindClientcombobox.current(newindex=0)

if __name__ == '__main__':
    window = Tk()
    application = Clients(window)
    window.mainloop()
