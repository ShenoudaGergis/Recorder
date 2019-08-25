from tkinter import Tk , Label , Button , PhotoImage;
from tkinter.ttk import Progressbar;
from tkinter.filedialog import asksaveasfile
from threading import Thread;
from os import remove , fdopen;
from sys import getsizeof;
from tempfile import mkstemp;
from time import time , sleep , strftime , gmtime;
import wave;
import pyaudio;
import audioop;
import numpy as np;


class MainWin(Tk) :
	def __init__(self,title) :
		Tk.__init__(self);
		self.title(title);
		self.resizable(False,False);
		self.geometry("500x50")

		self.columnconfigure(1,weight=1);
		self.rowconfigure(0,weight=1);
		self._part();
		self.count= 0;
		self.size = 0;
		self.stop = False;
		self.play = False;
		self.starter = True;

	def _part(self) :
		self.dataSize = Label(self,text="0B".center(10," "))
		self.dataSize.grid(row=0,column=0,padx=10,sticky="ew");
		self.progressBar = Progressbar(self,mode="determinate")
		self.progressBar["maximum"] = 100;
		self.progressBar.grid(row=0,column=1,ipady=3,sticky="ew");
		self.clockLabel = Label(self,text="00:00:00");
		self.clockLabel.grid(row=0,column=2,padx=10,sticky="ew");
		
		self.actionBtn = Button(self,text="jesus",relief="flat",command=self._onAction);
		self.actionBtn.grid(row=0,column=3,padx=5);

		self.stopBtn = Button(self,text="jesus",relief="flat",state="disabled",command=self._onStop);
		self.stopBtn.grid(row=0,column=4,padx=5);

		try : image = PhotoImage(file="img/play.png")
		except : pass;
		else : self.actionBtn.configure(image=image);self.actionBtn.img = image;

		try : image = PhotoImage(file="img/stop.png")
		except : pass;
		else : self.stopBtn.configure(image=image);self.stopBtn.img = image;

		self.bind("<space>" , lambda x : self._onAction());

	def voice(self) :
		def callback(inData,frameCount,timeInfo,statues) :
			if self.stop : 
				file = open(self.nameTemp,"rb")
				binaries = b''.join(file.readlines())
				pathName = self.saveFile();	
				if pathName != None :					
					waveFile = wave.open(pathName, 'wb')
					waveFile.setnchannels(2)
					waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
					waveFile.setframerate(44100)
					waveFile.writeframes(binaries)
					waveFile.close()

				file.close();
				self.fileTemp.close();
				remove(self.nameTemp);
				self.reset()
				return (inData,pyaudio.paComplete);
			else :
				vis = np.fromstring(inData,dtype=np.int16);
				peak = np.average(np.abs(vis))*2;
				self._updateProgressBar(int(int(peak)*100/2**16));
				if self.play : 
					#print(inData)
					self.fileTemp.write(inData);
					self.size += getsizeof(inData);
					self.dataSize.configure(text=self.formateSize(self.size))
					return (inData,pyaudio.paContinue);				
				else : return (inData,pyaudio.paContinue);

		audio = pyaudio.PyAudio();
		stream = audio.open(
			format=pyaudio.paInt16,
			channels=2,
			rate=44100,
			input=True,
			frames_per_buffer=1024,
			stream_callback=callback
			);

	def _changeFlags(self) :
		if self.play : file = "img/play.png";self.play=False;
		else : file = "img/pause.png";self.play=True;
		try :
			image = PhotoImage(file=file);
		except : pass
		else : self.actionBtn.configure(image=image);self.actionBtn.img=image

	def _onStop(self) : self.stop = True;

	def _updateProgressBar(self,value) : self.progressBar["value"] = value;

	def _onAction(self) :
		self._changeFlags();
		if self.starter :
			self.starter = False;
			self.handlerTemp , self.nameTemp = mkstemp();
			self.fileTemp = fdopen(self.handlerTemp , "wb");
			self._updateTime();
			self.voice();
			self.stopBtn.configure(state="normal")
	
	@staticmethod
	def _startNewThread(func) :
		thread = Thread(target=func,args=());
		thread.setDaemon(True)
		thread.start();
	
	@staticmethod
	def saveFile() :
		f = asksaveasfile(mode='wb', defaultextension=".wav")
		if f is None : return
		f.close()
		return f.name

	@staticmethod
	def formateSize(num, suffix='B') :
		for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi'] :
			if abs(num) < 1024.0 :
				return "%3.1f%s%s" % (num, unit, suffix)
			num /= 1024.0;
		return ("%.1f%s%s" % (num, 'Yi', suffix));

	def reset(self) :
		try : image = PhotoImage(file="img/play.png")
		except : pass;
		else : self.actionBtn.configure(image=image);self.actionBtn.img = image;

		try : image = PhotoImage(file="img/stop.png")
		except : pass;
		else : self.stopBtn.configure(image=image,state="disabled");self.stopBtn.img = image;

		self.size = 0;
		self.count = 0;
		self.starter = True;
		self.play = False;
		self.stop = False;
		self.progressBar["value"] = 0;
		self.dataSize.configure(text="0B".center(10," "))
		self.clockLabel.configure(text="00:00:00");


	def _updateTime(self) :
		if self.stop : return;
		if self.play : self.count += 0.2;self.clockLabel.configure(text=str(strftime("%H:%M:%S", gmtime(self.count))));self.after(200,self._updateTime);
		else : self.after(200,self._updateTime);


	def run(self) :
		self.mainloop();



MainWin("jesus christ").run(); 