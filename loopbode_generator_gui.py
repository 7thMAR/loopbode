import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt

tk_const ={
    'FONT': ('DejaVu', 10),
}

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidget()

    def createWidget(self):
        label_log10_start = tk.Label(self, text='log10_start:', font=tk_const['FONT'])
        label_log10_start.grid(row=0,column=0)
        log10_start = tk.StringVar()
        self.entry_log10_start = tk.Entry(self, textvariable=log10_start, width=30, font=tk_const['FONT'])
        self.entry_log10_start.grid(row=0,column=1)
        log10_start.set('-2')

        label_log10_stop = tk.Label(self, text='log10_stop:', font=tk_const['FONT'])
        label_log10_stop.grid(row=1,column=0)
        log10_stop = tk.StringVar()
        self.entry_log10_stop = tk.Entry(self, textvariable=log10_stop, width=30, font=tk_const['FONT'])
        self.entry_log10_stop.grid(row=1,column=1)
        log10_stop.set('10')

        label_points_per_decade = tk.Label(self, text='points_per_decade:', font=tk_const['FONT'])
        label_points_per_decade.grid(row=2,column=0)
        points_per_decade = tk.StringVar()
        self.entry_points_per_decade = tk.Entry(self, textvariable=points_per_decade, width=30, font=tk_const['FONT'])
        self.entry_points_per_decade.grid(row=2,column=1)
        points_per_decade.set('50')

        label_output = tk.Label(self, text='output name:', font=tk_const['FONT'])
        label_output.grid(row=3,column=0)
        self.path = tk.StringVar()
        self.entry_path = tk.Entry(self, textvariable=self.path, width=30, font=tk_const['FONT'])
        self.entry_path.grid(row=3,column=1)
        self.path.set('./loopbode_test.csv')
        btn_browse = tk.Button(self, text='...', font=tk_const['FONT'], command=self.browsefiles)
        btn_browse.grid(row=3,column=2)

        btn_plot_freq_resp = tk.Button(self, text='plot freq resp', font=tk_const['FONT'], command=self.freq_resp_plot)
        btn_plot_freq_resp.grid(row=4,column=0)

        btn_plot_dd = tk.Button(self, text='plot ddgain/dphase', font=tk_const['FONT'], command=self.ddgain_dphase_plot)
        btn_plot_dd.grid(row=4,column=1)

        xscroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        yscroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        label_log_PZ = tk.Label(self, text='log10_PZs', font=tk_const['FONT'])
        label_log_PZ.grid(row=5,column=0)
        self.text_PZs = tk.Text(self, wrap=tk.NONE, width=30, height=16, font=tk_const['FONT'], yscrollcommand=yscroll.set,xscrollcommand=xscroll.set)
        self.text_PZs.grid(row=5,column=1)
        yscroll.config(command=self.text_PZs.yview)
        yscroll.grid(row=5,column=2,sticky='ns')
        xscroll.config(command=self.text_PZs.xview)
        xscroll.grid(row=6,column=1,sticky='we')
        self.text_PZs.insert(1.0,'1.0442 1.0000 -0.5\n4.5773 1.0000 -0.5\n6.2323 0.5097 1.0')

        btn_generate = tk.Button(self, text='generate', font=tk_const['FONT'], command=self.generatefiles)
        btn_generate.grid(row=7,column=0)
        self.ckvar_noise = tk.IntVar()
        ckbtn_noise = tk.Checkbutton(self, text='noise', variable=self.ckvar_noise, onvalue=1, offvalue=0)
        ckbtn_noise.grid(row=7,column=1)
        self.ckvar_noise.set(0)

    def ddgain_dphase_plot(self):
        [log10_start, log10_stop, points_per_decade] = self.read_entries()
        dlog10_freq = 1.0/points_per_decade
        log10_freq = np.arange(log10_start,log10_stop+dlog10_freq,dlog10_freq)

        dphase = (-self.phase[4:]+8*self.phase[3:-1]-8*self.phase[1:-3]+self.phase[:-4])/(12*dlog10_freq)
        ddgain = (-self.gain[4:]+16*self.gain[3:-1]-30*self.gain[2:-2]+16*self.gain[1:-3]-self.gain[:-4])/(12*np.power(dlog10_freq,2))
        self.dphase = dphase/(180*np.log(10)/np.pi)
        self.ddgain = ddgain/(40*np.log(10))
        log10_freq_d = log10_freq[2:-2]

        self.figure_plot(log10_freq_d, self.ddgain, self.dphase, [])

    def freq_resp_plot(self):
        [log10_start, log10_stop, points_per_decade] = self.read_entries()
        dlog10_freq = 1.0/points_per_decade
        log10_freq = np.arange(log10_start,log10_stop+dlog10_freq,dlog10_freq)

        str_log10_PZ = self.text_PZs.get(1.0, tk.END)
        list_str_log10_PZ = str_log10_PZ.strip().split()
        list_log10_PZ = [float(str_log10_PZ) for str_log10_PZ in list_str_log10_PZ]
        log10_PZ = np.array(list_log10_PZ).reshape((-1,3))

        [self.gain, self.phase] = self.freq_PZ(log10_freq, log10_PZ)
        if self.ckvar_noise.get() == 1:
            self.gain = self.gain+np.random.rand(len(self.gain))
            self.phase = self.phase+np.random.rand(len(self.phase))

        plt.clf()
        plt.get_current_fig_manager().window.wm_geometry('+500+50')
        fig1 = plt.subplot(2,1,1)
        fig1.plot(log10_freq, self.gain, color = 'black', label = r'$LG$')
        # fig1.set_xlabel(r'$\log_{10}f$')
        fig1.set_ylabel(r'loop gain (dB)')
        fig1.legend(loc = 'upper right')

        fig2 = plt.subplot(2,1,2)
        fig2.plot(log10_freq, self.phase, color = 'black', label = r'$PM$')
        fig2.set_xlabel(r'$\log_{10}f$')
        fig2.set_ylabel(r'phase margin ($^o$)')
        fig2.legend(loc = 'upper right')
        plt.show()

    def generatefiles(self):
        [log10_start, log10_stop, points_per_decade] = self.read_entries()
        freq = np.logspace(log10_start,log10_stop,num=int(1+(log10_stop-log10_start)*points_per_decade))

        filepath = self.entry_path.get().strip()
        str_output = 'Loop_Gain_Phase X,Loop_Gain_Phase Y,Loop_Gain_dB20 X,Loop_Gain_dB20 Y\n'
        for i in range(len(freq)):
            str_output = str_output + format(freq[i], 'f')+','+format(self.phase[i], 'f')+','+format(freq[i], 'f')+','+format(self.gain[i], 'f')+'\n'

        with open(filepath, 'w') as f:
            f.write(str_output)

    def browsefiles(self):
        filename = filedialog.askopenfilename(initialdir='.',
                                              title='Select a File',
                                              filetypes=(('CSV files', '*.csv'),
                                                         ('all files', '*,*')))
        self.path.set(filename)

    def read_entries(self):
        log10_start = float(self.entry_log10_start.get().strip())
        log10_stop = float(self.entry_log10_stop.get().strip())
        points_per_decade = float(self.entry_points_per_decade.get().strip())

        return [log10_start, log10_stop, points_per_decade]

    def figure_plot(self, log10_freq_d, ddgain, dphase, PZ):
        plt.clf()
        plt.get_current_fig_manager().window.wm_geometry('+500+50')
        fig1 = plt.subplot(2,1,1)
        fig1.plot(log10_freq_d, ddgain, color = 'black', label = r'$ddLG$')
        fig1.plot([log10_freq_d[0],log10_freq_d[-1]], [0.25,0.25], linestyle='dotted', color='red')
        fig1.plot([log10_freq_d[0],log10_freq_d[-1]], [-0.25,-0.25], linestyle='dotted', color='red')
        if len(PZ) == 3:
            log10_fn = PZ[0]
            damp_ratio = PZ[1]
            ai = PZ[2]
            fig1.plot(log10_fn, ai/(2*np.power(damp_ratio,2)), '*', color='red')
        fig1.set_ylabel(r'normalized ddLG (1)')
        fig1.legend(loc = 'upper right')

        fig2 = plt.subplot(2,1,2)
        fig2.plot(log10_freq_d, dphase, color = 'black', label = r'$dPM$')
        fig2.plot([log10_freq_d[0],log10_freq_d[-1]], [0.5,0.5], linestyle='dotted', color='red')
        fig2.plot([log10_freq_d[0],log10_freq_d[-1]], [-0.5,-0.5], linestyle='dotted', color='red')
        if len(PZ) == 3:
            log10_fn = PZ[0]
            damp_ratio = PZ[1]
            ai = PZ[2]
            fig2.plot(log10_fn, ai/damp_ratio, '*', color='red')
        fig2.set_xlabel(r'$\log_{10}f$')
        fig2.set_ylabel(r'normalized dPM (1)')
        fig2.legend(loc = 'upper right')
        plt.show()

    def freq_PZ(self, log10_freq, log10_PZ):
        log10_fn = log10_PZ[:,0]
        damp_ratio = log10_PZ[:,1]
        ai = log10_PZ[:,2]

        gain = np.array([])
        phase = np.array([])
        for log10_f in log10_freq:
            t = np.power(10,log10_f-log10_fn)
            gain_normalized = np.log(np.power(1-np.power(t,2),2)+4*np.power(damp_ratio,2)*np.power(t,2))
            phase_normalized = np.arctan2((2*damp_ratio*t),(1-np.power(t,2)))
            gain = np.append(gain, np.inner(ai,gain_normalized))
            phase = np.append(phase, np.inner(ai,phase_normalized))
        return (10/np.log(10))*gain, (180/np.pi)*phase

    def destroy(self):
        super().destroy()
        quit()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Bodeplot Generator')
    root.geometry('+50+50')
    app = Application(master=root)

    root.mainloop()