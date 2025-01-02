import tkinter as tk
from tkinter import filedialog
from scipy import optimize
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

        label_decimal = tk.Label(self, text='decimal:', font=tk_const['FONT'])
        label_decimal.grid(row=3,column=0)
        decimal = tk.StringVar()
        self.entry_decimal = tk.Entry(self, textvariable=decimal, width=30, font=tk_const['FONT'])
        self.entry_decimal.grid(row=3,column=1)
        decimal.set('4')

        label_load = tk.Label(self, text='load files:', font=tk_const['FONT'])
        label_load.grid(row=4,column=0)
        self.path = tk.StringVar()
        self.entry_path = tk.Entry(self, textvariable=self.path, width=30, font=tk_const['FONT'])
        self.entry_path.grid(row=4,column=1)
        self.path.set('./loopbode_test.csv')
        btn_browse = tk.Button(self, text='...', font=tk_const['FONT'], command=self.browsefiles)
        btn_browse.grid(row=4,column=2)

        btn_load =tk.Button(self, text='load and plot', font=tk_const['FONT'], command=self.loadfiles)
        btn_load.grid(row=5,column=0)
        btn_plot_dd =tk.Button(self, text='plot ddgain/dphase', font=tk_const['FONT'], command=self.ddgain_dphase_plot)
        btn_plot_dd.grid(row=5,column=1)

        xscroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        yscroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        label_PZs = tk.Label(self, text='log10_PZs', font=tk_const['FONT'])
        label_PZs.grid(row=6,column=0)
        self.text_PZs = tk.Text(self, wrap=tk.NONE, width=30, height=16, font=tk_const['FONT'], yscrollcommand=yscroll.set,xscrollcommand=xscroll.set)
        self.text_PZs.grid(row=6,column=1)
        yscroll.config(command=self.text_PZs.yview)
        yscroll.grid(row=6,column=2,sticky='ns')
        xscroll.config(command=self.text_PZs.xview)
        xscroll.grid(row=7,column=1,sticky='we')

        btn_dphase_fit = tk.Button(self, text='dphase fitting', font=tk_const['FONT'],command=self.dphase_fitting)
        btn_dphase_fit.grid(row=8,column=0)
        btn_ddgain_fit = tk.Button(self, text='ddgain fitting', font=tk_const['FONT'],command=self.dphase_fitting)
        btn_ddgain_fit.grid(row=8,column=1)

        btn_freq_resp = tk.Button(self, text='freq resp plot', font=tk_const['FONT'], command=self.freq_resp_plot)
        btn_freq_resp.grid(row=9,column=0)

    def ddgain_dphase_plot(self):
        [log10_start, log10_stop, points_per_decade, _] = self.read_entries()
        dlog10_freq = 1.0/points_per_decade
        log10_freq = np.arange(log10_start,log10_stop+dlog10_freq,dlog10_freq)

        dphase = (-self.phase[4:]+8*self.phase[3:-1]-8*self.phase[1:-3]+self.phase[:-4])/(12*dlog10_freq)
        ddgain = (-self.gain[4:]+16*self.gain[3:-1]-30*self.gain[2:-2]+16*self.gain[1:-3]-self.gain[:-4])/(12*np.power(dlog10_freq,2))
        self.dphase = dphase/(180*np.log(10)/np.pi)
        self.ddgain = ddgain/(40*np.log(10))
        log10_freq_d = log10_freq[2:-2]

        self.curve_fitted = [[],[]]
        self.figure_plot(log10_freq_d, self.ddgain, self.dphase, self.curve_fitted)

    def ddgain_fitting(self):
        [log10_start, log10_stop, points_per_decade, decimal] = self.read_entries()
        dlog10_freq = 1.0/points_per_decade
        log10_freq = np.arange(log10_start,log10_stop+dlog10_freq,dlog10_freq)
        log10_freq_d = log10_freq[2:-2]
        str_format = '.'+str(decimal)+'f'

        str_log10_PZ = self.text_PZs.get(1.0,tk.END)
        list_str_log10_PZ = str_log10_PZ.strip().split()

        list_log10_PZ = [float(str_log10_PZ) for str_log10_PZ in list_str_log10_PZ]

        log10_PZ = np.array(list_log10_PZ).reshape((-1,3))
        p0_guess = log10_PZ[:,0]
        boundary = (log10_PZ[:,1],log10_PZ[:,2])

        popt = optimize.curve_fit(self.ddgain_PZ_N, log10_freq_d, self.dphase, p0=p0_guess, bounds=boundary)[0]

        self.curve_fitted = [self.ddgain_PZ_N(log10_freq_d,*popt), self.dphase_PZ_N(log10_freq_d,*popt)]
        self.figure_plot(log10_freq_d, self.ddgain, self.dphase, self.curve_fitted)

        log10_PZ[:,0] = np.array([*popt])
        str_text_dphase = ''
        for row0, row1, row2 in zip(log10_PZ[:-2:3], log10_PZ[1:-1:3], log10_PZ[2::3]):
            str_text_dphase = str_text_dphase+format(row0[0], str_format)+' '+format(row0[1], str_format)+' '+format(row0[2], str_format)+'\n'
            str_text_dphase = str_text_dphase+format(row1[0], str_format)+' '+format(row1[1], str_format)+' '+format(row1[2], str_format)+'\n'
            str_text_dphase = str_text_dphase+format(row2[0], str_format)+' '+format(row2[1], str_format)+' '+format(row2[2], str_format)+'\n\n'
        self.text_PZs.delete(1.0, tk.END)
        self.text_PZs.insert(1.0, str_text_dphase)

    def dphase_fitting(self):
        [log10_start, log10_stop, points_per_decade, decimal] = self.read_entries()
        dlog10_freq = 1.0/points_per_decade
        log10_freq = np.arange(log10_start,log10_stop+dlog10_freq,dlog10_freq)
        log10_freq_d = log10_freq[2:-2]
        str_format = '.'+str(decimal)+'f'

        str_log10_PZ = self.text_PZs.get(1.0,tk.END)
        list_str_log10_PZ = str_log10_PZ.strip().split()

        list_log10_PZ = [float(str_log10_PZ) for str_log10_PZ in list_str_log10_PZ]

        log10_PZ = np.array(list_log10_PZ).reshape((-1,3))
        p0_guess = log10_PZ[:,0]
        boundary = (log10_PZ[:,1],log10_PZ[:,2])

        popt = optimize.curve_fit(self.dphase_PZ_N, log10_freq_d, self.dphase, p0=p0_guess, bounds=boundary)[0]

        self.curve_fitted = [self.ddgain_PZ_N(log10_freq_d,*popt), self.dphase_PZ_N(log10_freq_d,*popt)]
        self.figure_plot(log10_freq_d, self.ddgain, self.dphase, self.curve_fitted)

        log10_PZ[:,0] = np.array([*popt])
        str_text_dphase = ''
        for row0, row1, row2 in zip(log10_PZ[:-2:3], log10_PZ[1:-1:3], log10_PZ[2::3]):
            str_text_dphase = str_text_dphase+format(row0[0], str_format)+' '+format(row0[1], str_format)+' '+format(row0[2], str_format)+'\n'
            str_text_dphase = str_text_dphase+format(row1[0], str_format)+' '+format(row1[1], str_format)+' '+format(row1[2], str_format)+'\n'
            str_text_dphase = str_text_dphase+format(row2[0], str_format)+' '+format(row2[1], str_format)+' '+format(row2[2], str_format)+'\n\n'
        self.text_PZs.delete(1.0, tk.END)
        self.text_PZs.insert(1.0, str_text_dphase)

    def ddgain_PZ_N(self, log10_freq_d, *params):
        log10_PZ = np.asarray(params[:-2:3])
        damp_ratio = np.asarray(params[1:-1:3])
        ai = np.asarray(params[2::3])
        ddgain = self.ddgain_PZ(log10_freq_d, log10_PZ, damp_ratio,ai)
        return ddgain

    def ddgain_PZ(self, log10_freq_d, log10_PZ, damp_ratio, ai):
        ddgain = []
        for log10_freq in log10_freq_d:
            t = np.power(10,2*(log10_freq-log10_PZ))
            b = 2*np.power(damp_ratio,2)-1
            # aii = np.sign(ai)*(1-0.5*np.floor(np.abs(damp_ratio)))
            # aii = 0.5*(2*(ai/np.abs(ai))+(ai-1)/np.abs(ai-1)+(ai+1)/np.abs(ai+1))
            ddgain.append(np.inner(ai,2*(b*(t+1/t)+2)/np.power(t+1/t+2*b,2)))
        return ddgain

    def dphase_PZ_N(self, log10_freq_d, *params):
        log10_PZ = np.asarray(params[:-2:3])
        damp_ratio = np.asarray(params[1:-1:3])
        ai = np.asarray(params[2::3])
        dphase = self.dphase_PZ(log10_freq_d, log10_PZ, damp_ratio,ai)
        return dphase
    
    def dphase_PZ(self, log10_freq_d, log10_PZ, damp_ratio, ai):
        dphase = []
        for log10_freq in log10_freq_d:
            t = np.power(10,log10_freq-log10_PZ)
            b = 4*np.power(damp_ratio,2)-4
            # aii = np.sign(ai)*(1-0.5*np.floor(np.abs(damp_ratio)))
            dphase.append(np.inner(ai,(2*damp_ratio*(t+1/t)/(np.power(t+1/t,2)+b))))
        return dphase

    def freq_resp_plot(self):
        [log10_start, log10_stop, points_per_decade, _] = self.read_entries()
        dlog10_freq = 1.0/points_per_decade
        log10_freq = np.arange(log10_start,log10_stop+dlog10_freq,dlog10_freq)

        str_log10_PZ = self.text_PZs.get(1.0, tk.END)
        list_str_log10_PZ = str_log10_PZ.strip().split()

        list_log10_PZ = [float(str_log10_PZ) for str_log10_PZ in list_str_log10_PZ]

        log10_PZ = np.array(list_log10_PZ).reshape((-1,3))
        PZ = log10_PZ[:,0].reshape((-1,3))
        [gain_fit, phase_fit] = self.freq_PZ(log10_freq, PZ)

        plt.clf()
        plt.get_current_fig_manager().window.wm_geometry('+500+50')
        fig1 = plt.subplot(2,1,1)
        if len(self.gain) != 0:
            fig1.plot(log10_freq, self.gain-self.gain[0], color = 'black', label = r'$LG$')
        fig1.plot(log10_freq, gain_fit, color = 'green', label = r'$LG_{fit}$')
        # fig1.set_xlabel(r'$\log_{10}f$')
        fig1.set_ylabel(r'loop gain (dB)')
        fig1.legend(loc = 'upper right')

        fig2 = plt.subplot(2,1,2)
        if len(self.phase) != 0:
            fig2.plot(log10_freq, self.phase-self.phase[0], color = 'black', label = r'$LG$')
        fig2.plot(log10_freq, phase_fit, color = 'green', label = r'$PM$')
        fig2.set_xlabel(r'$\log_{10}f$')
        fig2.set_ylabel(r'phase margin ($^o$)')
        fig2.legend(loc = 'upper right')
        plt.show()

    # def generatefiles(self):
    #     [log10_start, log10_stop, points_per_decade] = self.read_entries()
    #     freq = np.logspace(log10_start,log10_stop,num=int(1+(log10_stop-log10_start)*points_per_decade))

    #     filepath = self.entry_path.get().strip()
    #     str_output = 'Loop_Gain_Phase X,Loop_Gain_Phase Y,Loop_Gain_dB20 X,Loop_Gain_dB20 Y\n'
    #     for i in range(len(freq)):
    #         str_output = str_output + format(freq[i], 'f')+','+format(self.phase[i], 'f')+','+format(freq[i], 'f')+','+format(self.gain[i], 'f')+'\n'

    #     with open(filepath, 'w') as f:
    #         f.write(str_output)

    def loadfiles(self):
        [log10_start, log10_stop, points_per_decade, decimal] = self.read_entries()
        dlog10_freq = 1.0/points_per_decade
        log10_freq = np.arange(log10_start,log10_stop+dlog10_freq,dlog10_freq)
        str_format = '.'+str(decimal)+'f'

        str_text_PZs = format(1.0000, str_format)+' '+format(log10_start, str_format)+' '+format(log10_stop, str_format)+'\n'+ \
                       format(0.5097, str_format)+' '+format(-1.0000, str_format)+' '+format(1.0000, str_format)+'\n'+ \
                       format(1.0000, str_format)+' '+format(-1.0000, str_format)+' '+format(1.0000, str_format)+'\n'+ \
                       '\n'+ \
                       format(2.0000, str_format)+' '+format(log10_start, str_format)+' '+format(log10_stop, str_format)+'\n'+ \
                       format(1.0000, str_format)+' '+format(-1.0000, str_format)+' '+format(1.0000, str_format)+'\n'+ \
                       format(0.5000, str_format)+' '+format(-1.0000, str_format)+' '+format(1.0000, str_format)+'\n'+ \
                       '\n'+ \
                       format(3.0000, str_format)+' '+format(log10_start, str_format)+' '+format(log10_stop, str_format)+'\n'+ \
                       format(1.0000, str_format)+' '+format(-1.0000, str_format)+' '+format(1.0000, str_format)+'\n'+ \
                       format(0.5000, str_format)+' '+format(-1.0000, str_format)+' '+format(1.0000, str_format)
        
        self.text_PZs.delete(1.0, tk.END)
        self.text_PZs.insert(1.0, str_text_PZs)

        filepath =self.entry_path.get().strip()

        with open(filepath) as f:
            lines = f.readlines()
            headings =lines[0].strip().split(',')
            data = [line.strip().split(',') for line in lines[1:]]

            sym_names = ['Phase Y', 'dB20 Y']
            sym_locs = [[heading.find(syn_name) > 0 for heading in headings].index(True) for syn_name in sym_names]
            self.phase = np.array([float(dataline[sym_locs[0]]) for dataline in data])
            self.gain = np.array([float(dataline[sym_locs[1]]) for dataline in data])

            plt.clf()
            plt.get_current_fig_manager().window.wm_geometry('+500+50')
            fig1 = plt.subplot(2,1,1)
            fig1.plot(log10_freq, self.gain, color = 'black', label = r'$LG$')
            fig1.set_ylabel(r'loop gain(dB)')
            fig1.legend(loc = 'upper right')

            fig2 = plt.subplot(2,1,2)
            fig2.plot(log10_freq, self.phase, color = 'black', label = r'$LG$')
            fig2.set_xlabel(r'$\log_{10}f$')
            fig2.set_ylabel(r'phase margin(dB)')
            fig2.legend(loc = 'upper right')
            plt.show()

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

        decimal = int(self.entry_decimal.get().strip())
        return [log10_start, log10_stop, points_per_decade, decimal]

    def figure_plot(self, log10_freq_d, ddgain, dphase, curve_fitted):
        plt.clf()
        plt.get_current_fig_manager().window.wm_geometry('+500+50')
        fig1 = plt.subplot(2,1,1)
        fig1.plot(log10_freq_d, ddgain, color = 'black', label = r'$ddLG$')
        fig1.plot([log10_freq_d[0],log10_freq_d[-1]], [0.25,0.25], linestyle='dotted', color='red')
        fig1.plot([log10_freq_d[0],log10_freq_d[-1]], [-0.25,-0.25], linestyle='dotted', color='red')
        if len(curve_fitted[0]) != 0:
            ddgain_fit = curve_fitted[0]
            fig1.plot(log10_freq_d, ddgain_fit, color='green', label = r'$ddLG_{fit}$')
        fig1.set_ylabel(r'normalized ddLG (1)')
        fig1.legend(loc = 'upper right')

        fig2 = plt.subplot(2,1,2)
        fig2.plot(log10_freq_d, dphase, color = 'black', label = r'$dPM$')
        fig2.plot([log10_freq_d[0],log10_freq_d[-1]], [0.5,0.5], linestyle='dotted', color='red')
        fig2.plot([log10_freq_d[0],log10_freq_d[-1]], [-0.5,-0.5], linestyle='dotted', color='red')
        if len(curve_fitted[1]) != 0:
            dphase_fit = curve_fitted[1]
            fig2.plot(log10_freq_d, dphase_fit, color='green', label = r'$dPM_{fit}$')
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