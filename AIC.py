import sys, random, argparse
import numpy as np
import math
from PIL import Image
import cv2
import os
import time
from threading import Thread

class VideoConverter:

    def __init__(self,path:str):

        if not os.path.exists('buffer'):
            os.mkdir('buffer')
        else:
            for file in os.listdir('buffer'):
                os.remove('buffer/'+file.strip())
        self.path=path
        self.dir='buffer/'
        self.cap = cv2.VideoCapture(self.path)

    def videoToImages(self):
     counter=0
     while(True):

            self.ret, self.frame = self.cap.read()
            counter += 1
            try:

                cv2.imwrite("{}.jpg".format(os.path.join(self.dir,str(counter))),self.frame)
            except:
                break
     self.cap.release()
     cv2.destroyAllWindows()

class ImageConverter:


    def __init__(self,cols:int, scale:float, moreLevels: bool):

        self.gscale1 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
        self.gscale2 = '@%#*+=-:. '
        self.cols=cols
        self.scale=scale
        self.moreLevels=moreLevels
        self.aimg = []

    def getAverageL(self,image):

     im = np.array(image)
     w,h = im.shape
     return np.average(im.reshape(w*h))

    def loadImage(self,image_path:str):

        self.image = Image.open(image_path).convert('L')
        self.W, self.H = self.image.size[0], self.image.size[1]
        self.w = float(self.W)/float(self.cols)
        self.h = float(self.w)/float(self.scale)
        self.rows = int(self.H/self.h)

    def covertImageToAscii(self):

        for j in range(self.rows):
            y1 = int(j*self.h)
            y2 = int((j+1)*self.h)
            if j == self.rows-1:
                y2 = self.H

            self.aimg.append("")

            for i in range(self.cols):
                x1 = int(i*self.w)
                x2 = int((i+1)*self.w)
                if i == self.cols-1:
                    x2 = self.W
                img = self.image.crop((x1, y1, x2, y2))

                avg = int(self.getAverageL(img))
                if self.moreLevels:

                    gsval = self.gscale1[int((avg*69)/255)]

                else:

                    gsval = self.gscale2[int((avg*9)/255)]

                self.aimg[j] += gsval

    def write_output(self,output_path:str):

        self.check_image(output_path)
        self.covertImageToAscii()
        with open(output_path[:-4]+'.txt','w') as writer:
            for line in self.aimg:
                writer.write(line+'\n')
        self.aimg=[]
        os.remove(output_path)

    def check_image(self,image_path:str):

        self.loadImage(image_path)
        if float(self.cols) > float(self.W) or float(self.rows) > float(self.H):
            print("Error(image too small)")
            exit(0)
            sys.exit()

    def sort_files_frames(self):

        files=[]
        for file in os.listdir('buffer'):
            if os.path.isfile(f'buffer/{file.strip()}'):
                files.append(int(file[:-4]))
        files.sort()
        for name in files:
        	files.insert(files.index(name),f'buffer/{name}.txt');files.remove(name)
        return files

class Parser():

  def __init__(self):

     import argparse
     self.parser = argparse.ArgumentParser(description="AIC-Auto Image Converter")
     self.parser.add_argument("--file",'-f', help="File with video(even gif)", required=True)
     self.parser.add_argument("--colums",'-c', help="Size of colums",default=80,type=int)
     self.parser.add_argument("--scale",'-s', help="Scale of font",default=0.43,type=float)
     self.parser.add_argument("--moreLevels",help="Use more leves of symbols",action='store_true',default=False)
     self.parser.add_argument("--noTerminal",help="Output in terminal",action='store_true',default=True)
     self.parser.add_argument("--mirror",'-m',help="Does mirror effect",action='store_true',default=False)
     self.parser.add_argument("--time",'-t',help="Time between new frame",type=float,default=0.0)
     self.args = self.parser.parse_args()
     self.file_path=self.args.file
     self.colums=self.args.colums
     self.scale=self.args.scale
     self.moreLevels=self.args.moreLevels
     self.terminal=self.args.noTerminal
     self.mirror=self.args.mirror
     self.time=self.args.time

if __name__ == '__main__':

    Parser=Parser()
    VideoConverter=VideoConverter(Parser.file_path)
    VideoConverter.videoToImages()
    ImageConverter=ImageConverter(Parser.colums,Parser.scale,Parser.moreLevels)
    threads=[]
    ImageConverter.check_image('buffer/{}'.format(os.listdir('buffer')[0]))
    for names in os.listdir('buffer'):	
    		threads.append(Thread(target=ImageConverter.write_output, args=('buffer/'+names.strip(),)))
    for thread in threads:
        thread.start()
        thread.join()
    files=ImageConverter.sort_files_frames()
    if Parser.terminal:
        while True:
            for file in files:
                    try:
                    	with open(file,'r',errors='ignore') as reader:
                            symbols=reader.read().split('\n')
                            for symbol in symbols:
                                if Parser.mirror:
                                    print(f'{symbol} {symbol[::-1]}')
                                else:
                                    print (symbol)
                            time.sleep(Parser.time)
                            os.system("cls")
                    except KeyboardInterrupt:
                    	os.system("cls")
                    	print ("Exiting...")
                    	exit()
                    

    else:
        print ("All images are converted!")
        exit()
