#! /usr/bin/env python
#coding=utf-8

from pyshed import roscore, rosrun, rqt


def main():
    print 'Starting ROS core...'
    core = roscore(delay=2, stdout='roscore.txt')

    print 'Starting USB camera node...'
    camera = rosrun('usb_cam', 'usb_cam_node', '__name:=camera', stdout='usb_cam.txt')

    print 'Image viewer...'
    rqt('-s', 'rqt_image_view/ImageView', '--args', 'image:=/camera/image_raw', stdout='image_view.txt').wait()

    print 'Shutdown...'
    camera.terminate()
    core.terminate()


if __name__ == '__main__':
    main()
