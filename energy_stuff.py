import cv2
import sys
import numpy as np

frameDif = 2
fps = 240

def main():
	if len(sys.argv) != 2:
		print("Please specify an input file.")
		sys.exit()
	cap = cv2.VideoCapture(sys.argv[1])
	totFrames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	p1 = None
	p2 = None
	fgbg = cv2.BackgroundSubtractorMOG()
	while(1):
		_, frame = cap.read()
		framePos = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
		res = fgbg.apply(frame)
		res = cv2.dilate(res, np.ones((10, 10),np.uint8), iterations = 1)
		contours, _ = cv2.findContours(res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		x = None
		y = None
		if len(contours) > 2:
			areas = [cv2.contourArea(c) for c in contours]
			max_index = np.argmax(areas)
			x, y, w, h = cv2.boundingRect(contours[max_index])
			if x > 1000:
				del areas[max_index]
				max_index = np.argmax(areas)
				x, y, w, h = cv2.boundingRect(contours[max_index])
			if y < 200:
				del areas[max_index]
				max_index = np.argmax(areas)
				x, y, w, h = cv2.boundingRect(contours[max_index])
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
		cv2.imshow('frame', cv2.resize(frame, (0,0), fx=0.75, fy=0.75))
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		if p1 == None:
			p1 = Pos(frame, x, y, framePos)
		elif p1.center[1] < y:
			p1 = Pos(frame, x, y, framePos)
		if p1 != None:
			if framePos - p1.pos == frameDif:
				p2 = Pos(frame, x, y, framePos)
				break
		if framePos == totFrames:
			print('Fail!')
			sys.exit()
	#cv2.imshow('p1', cv2.resize(p1.frame, (0,0), fx=0.75, fy=0.75))
	#cv2.imshow('p2', cv2.resize(p2.frame, (0,0), fx=0.75, fy=0.75))
	print(p1.center)
	print(p2.center)
	print 'Velocity: ', calcVf(p1, p2, frameDif), 'm/s'
	cap.release()
	cv2.destroyAllWindows()

def calcVf(p1, p2, frameDif):
	a = p2.x - p1.x
	b = p2.y - p1.y
	pixel_to_m = 51.04
	deltaX = np.sqrt(np.power(a, 2)+np.power(b, 2))
	deltaT = frameDif * fps
	return (deltaX * pixel_to_m) / deltaT

class Pos:

	def __init__(self, frame, x, y, pos):
		self.frame = frame
		self.x = x
		self.y = y
		self.center = (x, y)
		self.pos = pos

if __name__ == '__main__':
	main()
