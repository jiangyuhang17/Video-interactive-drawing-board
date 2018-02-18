# -*- coding:utf-8 -*-
'''
Created on 2016/12/1

@author: jyh
''' 
import numpy as np   
import cv2  
import time 

#设定追踪物件的阈值，HSV空间
redLower = np.array([165,160,100])  
redUpper = np.array([180,255,255]) 
#设定要使用的全局变量
pts = []
pts2 = []
drawing = False 
wipe = False
n = 0
m = 0
r = 0
g = 0
b = 0
w = 5
#建立窗口
cv2.namedWindow('Drawing')
#nothing函数
def nothing(x):
    pass
#建立调色板
cv2.createTrackbar('R','Drawing',255,255,nothing)
cv2.createTrackbar('G','Drawing',0,255,nothing)
cv2.createTrackbar('B','Drawing',0,255,nothing)
#建立橡皮擦的大小调节板
cv2.createTrackbar('Delete','Drawing',5,50,nothing)
#打开摄像头以及延时2s
camera = cv2.VideoCapture(0)  
time.sleep(2)  
#取得摄像机画面的尺寸
(ret, f) = camera.read()
size = f.shape
#建立白色画布
img = np.zeros((size[0],size[1],3),np.uint8)
img[0:size[0],0:size[1]] = [255,255,255]
#使用操作說明说明
print u'畫布上的半透明点點代表畫畫上色的點'
print u'按D鍵 開始畫畫,再次按下停止畫畫'
print u'按R鍵 清空畫布'
print u'按W鍵 橡皮擦,再次按下取消橡皮擦,橡皮擦大小在精度條里設定'
print u'按Esc鍵 關閉畫布'
print u'根據調色板RGB值選擇繪畫顏色,顏色變化會反映在透明點上'
print u'根據滑條Delete值橡皮擦粗細,變化會反映在透明點上'
print u'按S鍵 保存繪圖Drawing.jpg至程序文件夾'
#执行程式
while True:  
    #读取帧图像
    (ret, f) = camera.read()  
    #判断是否打开摄像头
    if not ret:  
        print 'No Camera'  
        break  
    #设置画笔颜色
    drawcolor = (b,g,r)
    #设置未叠加的画布
    imgmask = np.zeros((size[0],size[1],3),np.uint8)
    imgmask[0:size[0],0:size[1]] = [255,255,255]
    #图像的垂直对称翻转
    frame = cv2.flip(f,1)
    #转到HSV空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  
    #根据阈值构建掩膜
    mask = cv2.inRange(hsv, redLower, redUpper)  
    #腐蚀操作
    mask = cv2.erode(mask, None, iterations=2)  
    #膨胀操作，其实先腐蚀再膨胀的效果是开运算，去除噪点 
    mask = cv2.dilate(mask, None, iterations=2)  
    #轮廓检测 
    cnts=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]  
    #初始化物件的轮廓质心 
    center = None  
    #如果存在轮廓
    if len(cnts) > 0:  
        #找到面积最大的轮廓  
        c = max(cnts, key = cv2.contourArea)  
        #确定面积最大的轮廓的外接圆  
        ((x, y), radius) = cv2.minEnclosingCircle(c) 
        #计算轮廓的矩 
        M = cv2.moments(c)  
        #计算质心
        center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))  
        #只有当半径大于10时，才执行画图  
        if radius > 10:  
            #出现在白色画布上的质心
            cv2.circle(imgmask, center, 5, drawcolor, -1)
            #进行画画或者橡皮擦操作
            if drawing :
                pts.append(center) 
                cv2.circle(imgmask, center, 5, drawcolor, -1)
                cv2.line(img, pts[n - 1], pts[n], drawcolor, 3) 
                n = n + 1 
            else :
                pts = []
                n = 0
            if wipe :
                pts2.append(center)
                cv2.circle(imgmask, center, w, drawcolor, -1)
                cv2.circle(img, center, w, (255,255,255), -1)
                m = m + 1
            else :
                pts2 = []
                m = 0   
    #质点和画布叠加操作
    dst = cv2.addWeighted(img,0.7,imgmask,0.3,0)
    #设置画图颜色
    r = cv2.getTrackbarPos('R','Drawing')
    g = cv2.getTrackbarPos('G','Drawing')
    b = cv2.getTrackbarPos('B','Drawing') 
    #設置橡皮擦大小
    w = cv2.getTrackbarPos('Delete','Drawing')
    #显示叠加后的画布          
    cv2.imshow('Drawing', dst)  
    #设置按键操作
    k = cv2.waitKey(5)&0xFF
    if k == ord('d'):
        drawing = not drawing
        wipe = False
    if k == ord('w'):
        wipe = not wipe 
        drawing = False
    if k == ord('r'):
        img[0:size[0],0:size[1]] = [255,255,255] 
    if k == ord('s'):
        cv2.imwrite("Drawing.jpg",dst)
    if k == 27:  
        break  
     
camera.release()   
cv2.destroyAllWindows()  
