import cv2
cap = cv2.VideoCapture('theft.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
duration = frame_count / fps if fps > 0 else 0
print(f'Duration: {duration:.5f} seconds')
print(f'FPS: {fps}')
print(f'Frames: {int(frame_count)}')
