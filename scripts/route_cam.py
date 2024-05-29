#!/usr/bin/env python3

import json
import subprocess

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


def get_dimensions(url):
    """
    Get the image dimensions using ffprobe
    """
    # Get the image dimensions at startup using ffprobe
    ffprobe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "json",
        url,
    ]
    try:
        rospy.logdebug(f"Running FFprobe: {ffprobe_cmd}")
        ffprobe_process = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT)
        video_info = json.loads(ffprobe_process)
        width = video_info["streams"][0]["width"]
        height = video_info["streams"][0]["height"]
        rospy.loginfo(f"Raw {video_info}")
        rospy.logdebug(f"Raw Stream dimensions: {width}x{height}")
        return width, height
    except subprocess.CalledProcessError as e:
        rospy.logerr(f"Error running FFprobe: {e.output}")
        rospy.loginfo("IP Camera Stream not accessible. Exiting __ip_camera_publisher__ ...")
        exit()


def convert_rtsp_to_opencv(url, width, height):
    """
    Streams RTSP video using FFMPEG and converts it to OpenCV image format.
    Then publishes the image to a ROS topic
    """
    # Constructing the ffmpeg command line
    ffmpeg_cmd = [
        "ffmpeg",  # ffmpeg command
        "-nostdin",  # Disabling interaction on standard input in the background process group
        "-flags",  # Sets flags for low delay for real-time streaming
        "low_delay",
        "-rtsp_transport",  # Specifies the RTSP transport protocol as TCP
        "tcp",
        "-i",  # Specifies the input URL for the RTSP stream
        url,
        "-pix_fmt",  # Sets output pixel format
        # "yuv420p",
        "bgr24",  # Camera feed is converted from yuv420p to bgr24
        "-an",  # Disables audio recording
        "-vcodec",  # Sets the input video codec
        # "h264",
        # "-tune",
        # "zerolatency",
        "rawvideo",  # Camera feed is converted from h264 to rawvideo
        "-vf",  # Adding video filter to scale down the images
        f"scale={width}:{height}",
        "-f",  # Specifies the output format
        "rawvideo",
        "-",  # Output stream to stdout
    ]

    # Starting the ffmpeg process
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Creating an empty numpy array for the raw frame
    raw_frame = np.empty((height, width, 3), np.uint8)
    # Make raw frame a buffer that can be overwritten by the ffmpeg process
    frame_bytes = memoryview(raw_frame).cast("B")

    rospy.loginfo("IP Camera Stream: Starting")
    # Continuously read frames from the ffmpeg process while ROS is running
    while ffmpeg_process.poll() is None and not rospy.is_shutdown():
        try:
            ffmpeg_process.stdout.readinto(frame_bytes)
        except ValueError as e:
            rospy.logerr(f"Error reading frame: {e}")
            rospy.loginfo("IP Camera Stream not accessible. Exiting __ip_camera_publisher__ ...")
            break
        frame = raw_frame.reshape((height, width, 3))  # OpenCV image frame
        frame = cv2.resize(frame, (1920, 1080))  # Scale down to variable resolution?

        image_pub.publish(bridge.cv2_to_imgmsg(frame, "bgr8"))

    rospy.loginfo("IP Camera Stream: Stoping")


if __name__ == "__main__":
    rospy.init_node("ip_camera_publisher")

    # Get the RTSP stream URL from the launch params
    try:
        rtsp_stream_url = rospy.get_param("~rtsp_stream_url")
        image_topic = rospy.get_param("~image_topic")
        image_scale = rospy.get_param("~image_scale")
        if image_scale > 1.0 or image_scale < 0.0:
            image_scale = 0.5
    except KeyError as e:
        # If error reading params, exit
        rospy.logerr(e)
        rospy.logerr("Error: launch parameters error. Exiting __ip_camera_publisher__ ...")
        exit()

    # Define publisher
    bridge = CvBridge()
    image_pub = rospy.Publisher(image_topic, Image, queue_size=1)

    # Default Frame Dimensions - 2304x1296 (lowest clear stream supported by the camera used for testing)
    width = 2304
    height = 1296

    # Get the frame dimensions from the RTSP stream
    stream_width, stream_height = get_dimensions(rtsp_stream_url)
    if stream_width != width or stream_height != height:
        rospy.loginfo(f"New Raw Frame dimensions: {stream_width}x{stream_height}")
        width = stream_width
        height = stream_height

    # Scale down the frame dimensions
    width = int(width * image_scale)
    height = int(height * image_scale)
    rospy.loginfo(f"Output Frame dimensions: {width}x{height}")

    # Convert RTSP stream to OpenCV image and publish
    convert_rtsp_to_opencv(rtsp_stream_url, width, height)
