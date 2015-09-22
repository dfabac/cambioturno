#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, datetime, getopt

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import Tkinter as tk
import tkMessageBox

import configuration
from configuration import ConfigException



class editmail_window(tk.Tk):
    def __init__(self, parent, scheduledmode):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.scheduledmode = scheduledmode
        self.initialize()


    def initialize(self):
        self.grid()

        self.lblVar = tk.StringVar()
        self.label = tk.Label(self,textvariable=self.lblVar,anchor="w",fg="white",bg="red")
        self.label.grid(column=0,row=0,columnspan=2,sticky='EW')
        self.lblVar.set(u"Mensaje para el cambio de turno:")

        self.text1 = tk.Text(self,bd=0,height=10,bg="ghost white",wrap='word')
        self.text1.insert(1.0, cfg.get('MAIL_BODY'))
        self.text1.grid(column=0,row=1,columnspan=3,sticky='NSEW')
        self.text1.focus_set()

        button1 = tk.Button(self,text=u"Enviar",command=self.OnButton1Click)
        button1.grid(column=0,row=2,sticky='NSEW')
        button2 = tk.Button(self,text=u"Descartar",command=self.OnButton2Click)
        button2.grid(column=1,row=2,columnspan=2,sticky='NSEW')

        if self.scheduledmode:
            button3 = tk.Button(self, text=u"Recordar en...",command=self.OnButton3Click)
            button3.grid(column=0,row=3,columnspan=3,sticky='NSEW')

        button4 = tk.Button(self, text="Config", bg='red', bd=0, relief='groove',command=self.OnButton4Click)
        button4.grid(column=2, row=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.resizable(False,False)
        self.update()


    def OnButton1Click(self):
        bodymsg = self.text1.get('1.0', 'end-1c')
        try:
            sendmail(cfg.get('MAIL_FROM'), cfg.get('MAIL_DEST').split(','), bodymsg)
            self.lblVar.set(u"Enviado OK!")
            self.label.configure(bg="green", fg="black")
            self.after(2000, lambda: self.destroy()) 
        except Exception as e:
            tkMessageBox.showerror("Error", u"Error en el envío: %s" % e.message)


    def OnButton2Click(self):
        self.destroy()


    def OnButton3Click(self):
        print "show choices to set the next reminder"
        self.destroy()

    def OnButton4Click(self):
        cfg_win = config_window()
        cfg_win.transient(self)
        cfg_win.grab_set()
        self.wait_window(cfg_win)



class config_window(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.__initialize()
        self.__populate()


    def __initialize(self):
        self.grid()

        self.title(u'Configuración')

        timeFrame = tk.Frame(self)

        label1 = tk.Label(self,text=u'Servidor SMTP',anchor="w")
        label2 = tk.Label(self,text=u'Mail remitente',anchor="w")
        label3 = tk.Label(self,text=u'Usuario',anchor="w")
        label4 = tk.Label(self,text=u'Contraseña',anchor="w")
        label5 = tk.Label(self,text=u'Destinatario(s)',anchor="w")
        label6 = tk.Label(self,text=u'Cuerpo del mail por defecto:',height=2,anchor="sw")
        label7 = tk.Label(self,text=u'Hora de irse:',height=2,anchor="sw")
        label8 = tk.Label(timeFrame,text=u' : ')

        self.entry1 = tk.Entry(self)
        self.entry2 = tk.Entry(self)
        self.entry3 = tk.Entry(self)
        self.entry4 = tk.Entry(self,show='*')
        self.entry5 = tk.Entry(self)
        self.entry6 = tk.Entry(timeFrame,width=2) # Hora
        self.entry7 = tk.Entry(timeFrame,width=2) # Min

        self.entry6.bind('<KeyPress>', config_window.keyPress)
        self.entry7.bind('<KeyPress>', config_window.keyPress)

        self.text1 = tk.Text(self,bd=1,height=10,wrap='word')

        button1 = tk.Button(self,text=u"Guardar",command=self.OnButton1Click)
        button2 = tk.Button(self,text=u"Cancelar",command=self.OnButton2Click)

        label1.grid(column=0,row=0,sticky='NW')
        label2.grid(column=0,row=1,sticky='NW')
        label3.grid(column=2,row=0,sticky='NW')
        label4.grid(column=2,row=1,sticky='NW')
        label5.grid(column=0,row=2,sticky='NW')
        label6.grid(column=0,row=4,sticky='SW')
        label7.grid(column=0,row=3,sticky='SW')
        
        self.entry1.grid(column=1,row=0,sticky='NW')
        self.entry2.grid(column=1,row=1,sticky='NW')
        self.entry3.grid(column=3,row=0,sticky='NW')
        self.entry4.grid(column=3,row=1,sticky='NW')
        self.entry5.grid(column=1,row=2,columnspan=3,sticky='NSEW')

        self.entry6.pack(side='left')
        label8.pack(side='left')
        self.entry7.pack(side='left')
        timeFrame.grid(column=1,row=3,sticky='SW')

        self.text1.grid(column=0,row=5,columnspan=4)
        button1.grid(column=0,row=6,columnspan=2,sticky='NSEW')
        button2.grid(column=2,row=6,columnspan=2,sticky='NSEW')

        self.resizable(False,False)
        self.update()


    @staticmethod
    def keyPress(event):
        if event.char in ('0','1','2','3','4','5','6','7','8','9'):
            pass
        elif event.keysym not in ('Alt_r', 'Alt_L', 'F4','BackSpace', 'Delete','Left', 'Right'):
            return 'break'


    def __populate(self):
        self.entry1.insert(0, cfg.get('SMTP_SERV'))
        self.entry2.insert(0, cfg.get('MAIL_FROM'))
        self.entry3.insert(0, cfg.get('SMTP_USER'))
        self.entry4.insert(0, cfg.get('SMTP_PASS'))
        self.entry5.insert(0, cfg.get('MAIL_DEST'))
        self.entry6.insert(0, "%02d" % cfg.get('SCH_HOUR'))
        self.entry7.insert(0, "%02d" % cfg.get('SCH_MIN'))
        self.text1.insert(1.0, cfg.get('MAIL_BODY'))


    def OnButton1Click(self):
        aux = self.entry5.get()
        aux = aux.replace(' ', ',')
        aux = aux.replace(';', ',')

        cfg.set('SMTP_SERV', self.entry1.get())
        cfg.set('MAIL_FROM', self.entry2.get())
        cfg.set('SMTP_USER', self.entry3.get())
        cfg.set('SMTP_PASS', self.entry4.get())
        cfg.set('MAIL_DEST', aux)
        cfg.set('SCH_HOUR',  int(self.entry6.get()))
        cfg.set('SCH_MIN',   int(self.entry7.get()))
        cfg.set('MAIL_BODY', self.text1.get("1.0",'end-1c'))

        try:
            cfg.save()
            self.destroy()
        except ConfigException as ce:
            tkMessageBox.showerror("Error", u"Error de configuración: %s" % ce.message)
			

    def OnButton2Click(self):
        #cfg.read()
        self.destroy()



class snooze_window(tk.Tk):
    def __init__(self, parent, scheduledmode):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.scheduledmode = scheduledmode
        self.initialize()


    def initialize(self):
        pass


def sendmail(strfrom, to, strbody):
    print "mando mail a: %s" % ', '.join(to)

    subject  = u"Estado de la plataforma, día: " 
    subject += datetime.date.today().strftime('%d/%b/%Y')

    mailmsg = MIMEMultipart()
    mailmsg['Subject'] = Header(subject, "utf-8")
    mailmsg['To'] = ', '.join(to)
    mailmsg['From'] = strfrom
    mailmsg.attach(MIMEText(strbody.encode('utf-8'), 'plain', 'utf-8'))

    session = smtplib.SMTP(cfg.get('SMTP_SERV'))
    try:
        session.ehlo()
        session.login(str(cfg.get('SMTP_USER')), str(cfg.get('SMTP_PASS')))
        session.sendmail(strfrom, to, mailmsg.as_string())
        session.quit()
    except smtplib.SMTPException as stmpe:
        raise Exception(str(stmpe))



def showMainWindow(scheduled_mode):
    edit_win = editmail_window(None, scheduled_mode)
    edit_win.title('Hora de irse')
    edit_win.mainloop()


def usage():
    print u'\nUtilidad para envío de correo en cambio de turno a una hora ' \
          u'dada.\nOpciones:\n\t-h,--help\tMuesta esta ayuda\n\t-n,--noschedule' \
          u'\tSe ejecuta sin programador (servirse de uno externo)'


def dothework(scheduled_mode):
    def addSchedule():
        showMainWindow(True)
        sch_time = datetime.datetime.combine(datetime.datetime.now() + datetime.timedelta(days=1), daily_time)
        scheduler.enterabs(time.mktime(sch_time.timetuple()), 1, addSchedule, ())


    if(scheduled_mode):
        print u"Modo estándar"
        try:
            import sched
        except ImportError as ie:
            print u"Error: necesitas instalar módulo 'sched' (i.e: pip install sched)"
            sys.exit(1)

        scheduler = sched.scheduler(time.time, time.sleep)
        daily_time = datetime.time(cfg.get('SCH_HOUR'), cfg.get('SCH_MIN'))
        first_time = datetime.datetime.combine(datetime.datetime.now(), daily_time)
        scheduler.enterabs(time.mktime(first_time.timetuple()), 1, addSchedule, ())
        scheduler.run()
    else:
        print "Modo sin programador"
        showMainWindow(False)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn", ["help", "noschedule"])
    except getopt.GetoptError as err:
        print "%s" % err
        usage()
        sys.exit(2)

    scheduled_mode = True
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-n", "--noschedule"):
           scheduled_mode = False

    global cfg
    try:
        cfg = configuration.Config(__file__)
    except Exception as e:
        print e.message
        sys.exit(3)

    dothework(scheduled_mode)


cfg = None

if __name__ == '__main__': 
    main()
