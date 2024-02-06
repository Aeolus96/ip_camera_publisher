# ROS IP Camera Publisher Package

This ROS package streams video from an IP camera using the RTSP protocol, scales down the images, converts it to ROS Image format, and publishes them to a ROS topic.

> !! Higher resolutions will slow down the streaming significantly. !!

Reference example using the default streaming resolution:

- Camera -> RTSP stream out
- 2304x1296x3 = 8,957,952 Bytes/frame x 10 fps ~ 90 MB/s x 8bits ~ 720 Mb/s
- RTSP stream in -> FFmpeg -> Scaled DOWN into half resolution (default) -> ROS Image out
- 1152x648x3 = 2,239,488 Bytes/frame x 10 fps ~ 22 MB/s x 8bits ~ 179 Mb/s
- Total bandwidth used by this stream = 720 Mb/s + 179 Mb/s ~ 900 Mb/s

> Most inexpensive/common network setups unless specified are limited to 1000/100/10 Mbit/s per ethernet interface.

Performance can be improved by using hardware acceleration and stream compression using codecs like H264, H265 and HEVC. This package was tested with an IP camera that supports H264 and H265. Change the `ffmpeg_cmd` if you want to use other codecs. You can try to get a test feed running by using [FFmpeg](https://www.ffmpeg.org/) directly and then adding that command to the `ffmpeg_cmd` variable.

## Prerequisites

- ROS Noetic (Robot Operating System): Make sure you have ROS installed (Noetic tested). You can follow the [official ROS installation instructions](http://wiki.ros.org/ROS/Installation).
- OpenCV: The package relies on OpenCV for image processing. You can install it using:

  ```bash
  sudo apt-get install ros-${ROS_DISTRO}-cv-bridge
  ```

- FFmpeg: Ensure that FFmpeg is installed on your system. You can install it using:

  ```bash
  sudo apt-get install ffmpeg
  ```

## Package Installation

1. Clone this repository into your ROS workspace:

   ```bash
   cd ~/<your_ros_workspace>/src
   git clone https://github.com/Aeolus96/ip_camera_publisher.git
   ```

2. Build the ROS package:

   ```bash
   catkin build ip_camera_publisher
   ```

3. Source your ROS workspace:

   ```bash
   source ~/<your_ros_workspace>/devel/setup.bash
   ```

## Launching the IP Camera Publisher Node

Use the provided launch file to start the IP camera publisher node. Adjust the launch file parameters according to your IP camera settings.

```bash
roslaunch ip_camera_publisher camera.launch
```

## Launch File Parameters

- **`username`**: Username for RTSP stream authentication (default: "admin").
- **`password`**: Password for RTSP stream authentication (default: "I%3C3Robots").
- **`stream_path`**: Path to the RTSP stream on the IP camera (default: "192.168.0.41/h264Preview_01_main").
- **`image_topic`**: ROS topic to publish the images (default: "/camera/image_raw").
- **`image_scale`**: Scaling factor for resizing frames (default: 0.5). Keep this between 0.0 and 1.0.

## Node Details

- **Node Name**: `ip_camera_publisher`
- **Published Topic**: `/camera/image_raw` (adjust based on the `image_topic` parameter)

## Example Launch with Custom Parameters

```bash
roslaunch ip_camera_publisher camera.launch username:=<your_username> password:=<your_password> stream_path:=<your_stream_path> image_topic:=<your_image_topic> image_scale:=<0.5>
```

## License

This project is licensed under the [MIT License](LICENSE).

Feel free to report issues, or make suggestions!
