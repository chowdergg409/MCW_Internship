from moviepy.editor import ImageSequenceClip

frame_directory = '/home/hauderc/Documents/GitHub/MCW_Internship/frames'  # Directory where the frames are saved
output_video = 'output.mp4'  # Desired output video file

clip = ImageSequenceClip(frame_directory, fps=30)  # 30 FPS, adjust as needed
clip.write_videofile(output_video, codec='libx264')  # Codec can be changed as needed
