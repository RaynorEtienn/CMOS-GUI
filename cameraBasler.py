# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------------------------------
from pypylon import pylon

class Basler_ERROR(Exception):
    def __init__(self, ERROR_mode = "Basler_ERROR"):
        self.ERROR_mode = ERROR_mode
        super().__init__(self.ERROR_mode)

def get_nb_of_cam():
    """
    Return the number of camera connected

    :return: Number of uEye camera connected
    """
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()

    if devices != () :
        return len(devices)
    else:
        return 0

def get_cam_list():
    """
    Return the list containing the ID, serial number and name of all cameras connected

    :return: list build like that [[cam1_id, cam1_ser_no, cam1_name], ... ]
    """
    nb_cam = get_nb_of_cam()
    if nb_cam > 0:
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()
        cameraList = []
        for id, device in enumerate(devices):
            FriendlyName = device.GetFriendlyName().split(' ')
            FullModelName, SerNo = FriendlyName[1], int(FriendlyName[2].strip("()"))
            cameraList.append([id, SerNo, FullModelName])
        return cameraList
    else:
        return []

#-------------------------------------------------------------------------------------------------------

class BaslerCamera():
    def __init__(self, cam_id = 0):
        self.cam_id = cam_id
        tl_factory = pylon.TlFactory.GetInstance()
        self.h_cam = pylon.InstantCamera()
        self.h_cam.Attach(tl_factory.CreateFirstDevice())
        self.converter = pylon.ImageFormatConverter()
        self.nBitsPerPixel = int
        self.colormode = None
        self.MemID = int
        self.pcImageMemory = int
        self.width = int
        self.height = int
        self.pitch = int

        self.init()
        self.ser_no, self.id = self.get_cam_info()
        self.width_max, self.height_max, self.cam_name, self.cam_pixel = self.get_sensor_info()

    def init(self):
        self.h_cam.Open()
        if self.h_cam.IsOpen():
            #self.h_cam.Gain.SetValue(2.5)
            self.h_cam.Close()
            return True
        else:
            self.h_cam.Close()
            raise Basler_ERROR("init BlasterCamera")

    def get_cam_info(self):
        ser_no, id = None, None
        try :
            ser_no, id = get_cam_list()[self.cam_id][1], self.cam_id
        except : 
            raise Basler_ERROR("get_cam_info")
        
        return ser_no, id
    
    def get_sensor_info(self):
        try :
            if self.h_cam.IsOpen():
                max_height = self.h_cam.Height.GetMax()
                max_width = self.h_cam.Width.GetMax()
                name = get_cam_list()[self.cam_id][2]
                pixel = max_height * max_width

            elif not self.h_cam.IsOpen():
                self.h_cam.Open()
                max_height = self.h_cam.Height.GetMax()
                max_width = self.h_cam.Width.GetMax()
                name = get_cam_list()[self.cam_id][2]
                pixel = max_height * max_width
                self.h_cam.Close()
    
        except :
            raise Basler_ERROR("get_sensor_info")
        
        return max_width, max_height, name, pixel
    
    def get_sensor_max_width(self):
        try :
            if self.h_cam.IsOpen():
                nMaxWidth = self.h_cam.Width.GetMax()

            elif not self.h_cam.IsOpen():
                self.h_cam.Open()
                nMaxWidth = self.h_cam.Width.GetMax()
                self.h_cam.Close()

        except :
            raise Basler_ERROR("get_sensor_max_width")
        
        return nMaxWidth

    def get_sensor_max_height(self):
        try :
            if self.h_cam.IsOpen():
                nMaxHeight = self.h_cam.Height.GetMax()

            elif not self.h_cam.IsOpen():
                self.h_cam.Open()
                nMaxHeight = self.h_cam.Height.GetMax()
                self.h_cam.Close()
        except :
            raise Basler_ERROR("get_sensor_max_height")
        
        return nMaxHeight

    def set_display_mode(self, mode = pylon.PixelType_BGR8packed):
        try :
            self.converter.OutputPixelFormat = mode
    
        except :
            raise Basler_ERROR("set_display_mode")
        
    def capture_video(self):
        try : 
            if not self.h_cam.IsOpen():
                self.h_cam.Open()
            
            if not self.h_cam.IsGrabbing():
                self.h_cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            
        except :
            raise Basler_ERROR("capture_video")
        
    def stop_video(self):
        try : 
            if self.h_cam.IsGrabbing():
                self.h_cam.StopGrabbing()

            if self.h_cam.IsOpen():
                self.h_cam.Close()
        except :
            raise Basler_ERROR("stop_video")

    def alloc(self):
        pass

    def un_alloc(self):
        pass

    def stop_camera(self):
        try : 
            if self.h_cam.IsOpen():
                self.stop_video()
                self.un_alloc()
        except :
            raise Basler_ERROR("stop_camera")
        
    def get_mem_info(self):
        pass

    def get_image(self):
        try :
            if self.h_cam.IsOpen() and self.h_cam.IsGrabbing():
                grab_result = self.h_cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                if grab_result.GrabSucceeded():
                    # Get the image data as a numpy array
                    self.array = grab_result.Array

                    grab_result.Release()
                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                grab_result = self.h_cam.GrabOne(5000)

                if grab_result.GrabSucceeded():
                    # Get the image data as a numpy array
                    self.array = grab_result.Array

                    grab_result.Release()
                    
                self.h_cam.Close()

            return self.array
        
        except :
            raise Basler_ERROR("get_image")

    def get_aoi(self):
        try :
            if self.h_cam.IsOpen():
                
                width = self.h_cam.Width.GetValue()
                height = self.h_cam.Height.GetValue()
                offset_x = self.h_cam.OffsetX.GetValue()
                offset_y = self.h_cam.OffsetY.GetValue()

                return offset_x, offset_y, width, height
                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                width = self.h_cam.Width.GetValue()
                height = self.h_cam.Height.GetValue()
                offset_x = self.h_cam.OffsetX.GetValue()
                offset_y = self.h_cam.OffsetY.GetValue()

                self.h_cam.Close()
                
                return offset_x, offset_y, width, height

        except :
            raise Basler_ERROR("get_aoi")
        
    def set_aoi(self, x, y, w, h):

        x0, y0, w0, h0 = ajust_aoi(x, y, w, h)

        try :
            if self.h_cam.IsOpen():
                
                self.h_cam.Width.SetValue(w0)
                self.h_cam.Height.SetValue(h0)
                self.h_cam.OffsetX.SetValue(x0)
                self.h_cam.OffsetY.SetValue(y0)

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                self.h_cam.Width.SetValue(w0)
                self.h_cam.Height.SetValue(h0)
                self.h_cam.OffsetX.SetValue(x0)
                self.h_cam.OffsetY.SetValue(y0)

                self.h_cam.Close()

        except :
            raise Basler_ERROR("set_aoi")

    def get_colormode(self):
        try :
            if self.h_cam.IsOpen():
                pixelFormat =  self.h_cam.PixelFormat.GetValue()

            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                pixelFormat =  self.h_cam.PixelFormat.GetValue()

                self.h_cam.Close()
                
            return pixelFormat

        except :
            raise Basler_ERROR("get_colormode")

    def set_colormode(self, mode):
        try :
            if self.h_cam.IsOpen():
                self.h_cam.PixelFormat = mode
                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                self.h_cam.PixelFormat = mode

                self.h_cam.Close()

            self.nBitsPerPixel = get_bits_per_pixel(mode)

        except :
            raise Basler_ERROR("set_colormode")

    def get_exposure(self):
        """
        Method used to get the exposure time in seconds.

        Raises:
            Basler_ERROR: Error

        Returns:
            int: exposure time in seconds.
        """
        try :
            if self.h_cam.IsOpen():
                exposure = self.h_cam.ExposureTime.GetValue()

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                exposure = self.h_cam.ExposureTime.GetValue()

                self.h_cam.Close()
            return exposure

        except :
            raise Basler_ERROR("get_exposure")

    def get_exposure_range(self):
        """
        Method used to get the min and max value of the exposure time.

        Raises:
            Basler_ERROR: Error.

        Returns:
            ints: minimum and maximum values of exposure in seconds.
        """
        try :
            if self.h_cam.IsOpen():
                exposureMin = self.h_cam.ExposureTime.GetMin()
                exposureMax = self.h_cam.ExposureTime.GetMax()

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                exposureMin = self.h_cam.ExposureTime.GetMin()
                exposureMax = self.h_cam.ExposureTime.GetMax()

                self.h_cam.Close()
            return exposureMin, exposureMax

        except :
            raise Basler_ERROR("get_exposure_range")

    def set_exposure(self, exposure):
        """
        Method used to set the exposure time in seconds.

        Args:
            exposure (int): exposure time wanted in seconds.

        Raises:
            Basler_ERROR: Error.
        """
        try :
            if self.h_cam.IsOpen():
                self.h_cam.ExposureTime.SetValue(exposure)
                self.h_cam.Gain.SetValue(2.5)
                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                self.h_cam.ExposureTime.SetValue(exposure)
                self.h_cam.Gain.SetValue(2.5)

                self.h_cam.Close()

        except :
            raise Basler_ERROR("set_exposure")

    def get_frame_rate(self):
        """
        Method used to get the frame rate.

        Raises:
            Basler_ERROR: Error

        Returns:
            int: frame rate in seconds.
        """
        try :
            if self.h_cam.IsOpen():
                frameRate = self.h_cam.AcquisitionFrameRate.GetValue()

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                frameRate = self.h_cam.AcquisitionFrameRate.GetValue()

                self.h_cam.Close()
            return frameRate

        except :
            raise Basler_ERROR("get_frame_rate")

    def get_frame_time_range(self):
        """
        Method used to get the min and max value of the frame rate.

        Raises:
            Basler_ERROR: Error.

        Returns:
            ints: minimum and maximum values of the frame rate.
        """
        try :
            if self.h_cam.IsOpen():
                frameRateMin = self.h_cam.AcquisitionFrameRate.GetMin()
                frameRateMax = self.h_cam.AcquisitionFrameRate.GetMax()

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                frameRateMin = self.h_cam.AcquisitionFrameRate.GetMin()
                frameRateMax = self.h_cam.AcquisitionFrameRate.GetMax()

                self.h_cam.Close()
            return [frameRateMin, frameRateMax, None]

        except :
            raise Basler_ERROR("get_frame_time_range")

    def set_frame_rate(self, fps):
        """
        Method used to set the frame rate.

        Args:
            fps (int): frame rate wanted.

        Raises:
            Basler_ERROR: Error.
        """
        try :
            if self.h_cam.IsOpen():
                self.h_cam.AcquisitionFrameRate.SetValue(fps)

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                self.h_cam.AcquisitionFrameRate.SetValue(fps)

                self.h_cam.Close()

        except :
            raise Basler_ERROR("set_frame_rate")

    def get_pixel_clock(self):
        pass

    def get_black_level(self):
        """
        Method used to get the blacklevel.

        Raises:
            Basler_ERROR: Error

        Returns:
            int: blacklevel.
        """
        try :
            if self.h_cam.IsOpen():
                BlackLevel = self.h_cam.BlackLevel.GetValue()

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                BlackLevel = self.h_cam.BlackLevel.GetValue()

                self.h_cam.Close()
            return BlackLevel

        except :
            raise Basler_ERROR("get_black_level")
        
    def get_black_level_range(self):
        """
        Method used to get the min and max value of the blackLevel.

        Raises:
            Basler_ERROR: Error.

        Returns:
            ints: minimum and maximum values of the blackLevel.
        """
        try :
            if self.h_cam.IsOpen():
                BlackLevelMin = self.h_cam.BlackLevel.GetMin()
                BlackLevelMax = self.h_cam.BlackLevel.GetMax()

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                BlackLevelMin = self.h_cam.BlackLevel.GetMin()
                BlackLevelMax = self.h_cam.BlackLevel.GetMax()

                self.h_cam.Close()
            return BlackLevelMin, BlackLevelMax

        except :
            raise Basler_ERROR("get_black_level_range")

    def set_black_level(self, value):
        """
        Method used to set the blackLevel.

        Args:
            value (int): blackLevel wanted.

        Raises:
            Basler_ERROR: Error.
        """
        try :
            if self.h_cam.IsOpen():
                self.h_cam.BlackLevel.SetValue(value)

                
            elif not self.h_cam.IsOpen():
                self.h_cam.Open()

                self.h_cam.BlackLevel.SetValue(value)

                self.h_cam.Close()

        except :
            raise Basler_ERROR("set_black_level")

#-------------------------------------------------------------------------------------------------------

def ajust_aoi(x, y, width, height):
    """
    Ajust the AOI parameters to the closest (smaller) possible size.
    The possibles sizes are defined by:
        - 0 <= x <= 2456 pixels with 4 pixels step
        - 0 <= y <= 2054 pixels with 2 pixels step
        - 256 <= width <= 2456 pixels with 8 pixels step
        - 256 <= height <= 2056 pixels with 2 pixels step

    :param x: x coordinate (width) of the top left corner of the AOI
    :param y: y coordinate (height) of the top left corner of the AOI
    :param width: width of the AOI
    :param height: height of the AOI
    :return: same AOI parameter adjusted to the closest (smaller) possible size
    """
    if x < 0:
        x0 = 0
    elif x > 2456:
        x0 = 2456
    else:
        x0 = x - x % 4

    if y < 0:
        y0 = 0
    elif x > 2054:
        y0 = 2054
    else:
        y0 = y - y % 2

    if width < 256:
        width0 = 256
    elif width > 2456:
        width0 = 2456
    else:
        width0 = width - width % 8

    if height < 256:
        height0 = 256
    elif height > 2054:
        height0 = 2054
    else:
        height0 = height - height % 2

    return x0, y0, width0, height0

def get_bits_per_pixel(color_mode):
    """
    Returns the number of bits per pixel for the given color mode raises exception if color mode is not is
    not in dict

    :param color_mode: color mode for which we want the number of bits per pixel
    :return : number of bits per pixel of the given color mode
    """

    return {
        'Mono8': 8,
        'Mono12': 12,
    }[color_mode]

#-------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Test - get_nb_of_cam : {get_nb_of_cam()}")
    print(f"Test - get_cam_list : {get_cam_list()}")

    BaslerTest = BaslerCamera()
    print(f"Test - Blaster Class : {BaslerTest}")
    print(f"Test - get_sensor_max_width : {BaslerTest.get_sensor_max_width()}")
    print(f"Test - get_sensor_max_height : {BaslerTest.get_sensor_max_height()}")
    print(f"Test - set_display_mode : {BaslerTest.set_display_mode()}")
    print(f"Test - capture_video : {BaslerTest.capture_video()}")
    print(f"Test - stop_video : {BaslerTest.stop_video()}")
    print(f"Test - get_image : {BaslerTest.get_image()}")
    print(f"Test - get_aoi : {BaslerTest.get_aoi()}")
    print(f"Test - set_aoi : {BaslerTest.set_aoi(0, 100, 600, 800)}")
    print(f"Test - get_colormode : {BaslerTest.get_colormode()}")
    print(f"Test - set_colormode : {BaslerTest.set_colormode('Mono8')}")
    print(f"Test - get_exposure : {BaslerTest.get_exposure()}")
    print(f"Test - get_exposure_range : {BaslerTest.get_exposure_range()}")
    print(f"Test - set_exposure : {BaslerTest.set_exposure(BaslerTest.get_exposure_range()[1])}")
    print(f"Test - get_frame_rate : {BaslerTest.get_frame_rate()}")
    print(f"Test - get_frame_time_range : {BaslerTest.get_frame_time_range()}")
    print(f"Test - set_frame_rate : {BaslerTest.set_frame_rate(1)}")
    print(f"Test - get_black_level : {BaslerTest.get_black_level()}")
    print(f"Test - get_black_level_range : {BaslerTest.get_black_level_range()}")
    print(f"Test - set_black_level : {BaslerTest.set_black_level(0)}")
