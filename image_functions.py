from skimage import io
from skimage import measure
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.morphology import closing, footprint_rectangle
from skimage.color import rgb2gray
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


# Class for io images, just to eliminate some of the repetetive syntax
class Image():
    def __init__(self, path: str) -> None:
        """Reads in an image to create an object from given path.

        Args:
        path (str): path to image file compatible with skimage io

        Returns: 
        None"""
        if type(path) == np.ndarray:
            self.array = path
        else:
            self.array = io.imread(path)
        self.bwarray = rgb2gray(self.array)

    
    def show(self) -> None:
        """
        Show image using plt imshow.
        
        Args:
        None
        
        Returns:
        None 
        """
        plt.imshow(self.array)
        plt.show()
    
    def scale_heatmap(self)-> None:
        """Adds contrasting pixels to the image to correctly scale the heatmap representation of an image after cropping
        
        Args: 
        None
        
        Returns:
        None
        """
        self.array[0][0] = 1
        self.array[0][1] = 0


    def bright_fraction(self, threshold:float) -> float:
        """Returns the fraction of an image that has pixels which are brighter than a certain threshold. 

        Args: 
        threshold (float): Number between 0 and 1. Brightness values greater than this are considered "bright".

        Returns: 
        (float): Decimal fraction describing number of bright pixels
        """

        bright_pixels = np.where(self.bwarray>(threshold/255), self.array, 0)
        bright_pixels = np.count_nonzero(bright_pixels)
        area = len(self.array) * len(self.bwarray[0])
        percent = bright_pixels/area
        print(f"Bright Fraction: {percent}")

        return percent
    

    def brightness_hist(self, threshold:float = -1) -> None:
        """Makes a histogram of brighnesses in the image. Useful for deciding a brighness threshold, mayhaps. 
        
        Args: 
        threshold (optional) (float): A vertical line will be drawn here to test out a certain threshold value.
        
        Returns: 
        None
        """

        brightnesses = plt.hist(np.ndarray.flatten(self.bwarray), bins = 50, color = "darkblue")
        if threshold != -1:
            plt.vlines(threshold, 0, max(brightnesses[0]), "red", linestyles = "dashed")
        plt.show()


    def avg_brightness(self):
        """Calculates the average brightness of all pixels in an image.
        
        Args: 
        None

        Returns: 
        (float): Average value of all pixel brightnesses 
        """

        return sum([sum(i) for i in self.bwarray])/(len(self.bwarray)*len(self.bwarray[0]))
    

    def contrast_difference(self, other:Image)-> float:
        """Calculates the difference in brightness between two images.
        
        Args: 
        other (Image): the image with which to compare self image to
        
        Returns: 
        (float): the decimal value of difference in average brightness between the two images
        """
        return np.abs(self.array.avg_brightness() - other.avg_brightness())
    
    def calc_transmittance(self, light_src:Image)-> float:
        """Based on an image of a light source, and an image of object on top of a light source, returns how much light is transmitted through the object.
         
        Args: 
        light_src (Image): Image object of the light source without the hazy object on top
          
        Returns: 
         (float): fraction of light which is transmitted
        
         """
        trans = self.avg_brightness()/light_src.avg_brightness()
        print(f"Fraction of light transmitted: {trans}")
        return trans

    
    def crop(self, region) -> Image:
        """Crops the image to a region defined by either a list of points or a bbox object from skimage.measure
        
        Args: 
        Region (list[int] or region.bbox): list of integer points that define the corners of a crop region. Ordered min x, min y, max x, max y

        Returns: 
        (Image): new image object that is cropped to specified region

        """
        if type(region) == list:
            minx, miny, maxx, maxy = region
        else:
            minx, miny, maxx, maxy = region.bbox

        if maxx<minx or maxy<miny:
            raise(ValueError("Max value larger than min value. Review order of points in array."))
        
        return Image(self.array[minx:maxx, miny:maxy])
    


    def crop_wh(self, point:tuple[int], width:int, height:int = -1)-> Image:
        """Crops an image from inputs of a locating point, width and height rather than four points
        
        Args: 
            point (tuple(int)): coordinates of the top left corner of the cropped region.
            width (int): horizontal length of the cropped region
            height (int) (optional): vertical length of cropped region, equal to width by default

        Returns: 
            (image): Cropped region image object
        """
        if height == -1:
            height = width
        return self.crop([point[0], point[1], point[0]+width, point[1]+height])


    def label_img(self, ftprnt: int, size: int = -1)-> None:
        """Uses skimage label function to label the significant parts of the image.
        
        Args: 
            ftprnt (int): size of footprint square
            size (int) (optional): if specified, only regions with area larger than specified will be labeled. 
        
        Returns:
            None
            """
        
        threshold = threshold_otsu(self.bwarray)
        bw = closing(self.bwarray>threshold, footprint_rectangle((ftprnt, ftprnt)))
        cleared = clear_border(bw)
        labels = measure.label(cleared)
        regions = measure.regionprops(labels)

        if size>=0:
            sig_regions = []
            for region in regions:
                if region.area>=size:
                    sig_regions.append(region)
            regions = sig_regions

        fig, ax = plt.subplots()
        ax.imshow(self.array)
        
        for region in regions:
            minx, miny, maxx, maxy = region.bbox
            rect = mpatches.Rectangle(
                (miny, minx),
                maxy-miny,
                maxx-minx,
                fill = False,
                edgecolor = "red", 
                linewidth =2,
            )
            ax.add_patch(rect)
        plt.show()



    

    
