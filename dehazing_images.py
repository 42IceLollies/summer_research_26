# Script may take up to 9 minutes per image

import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import json
# May be interesting to look into using ransac rather than np.polyfit

# number of pixels in the width/height of a patch, how much the patches are overlapped
# And how far out patches may affect each other during interpolation
patch_size = 50
overlap = 25
interpol_range = 5


# Read in image, reverse red and blue channels- backwards in CV library
image = cv.imread("EOS_R100_JPG/jpg0006.jpg")
image = image[:,:,::-1]



#=====================  Airlight Magnitude and Direction Calculation Functions ==========================

# x dimension = red
# y dimesnion = green
# z dimension = blue

def find_dir_and_mag(image) -> (np.ndarray):
    """Calculates the magnitude and color direction of the haze added to an image

    Args: 
    image: original image to process read into CV, in RBG format

    Returns: 
    mags (np.ndarray): two dimensional array containing magnitude information for each patch in the image
    airlight_dir (np.ndarray): two dimensional array containing direction information for eatch patch in image
    uncertainties (np.ndarray): two dimensional array containing uncertainty in line of best fit for each patch
    """
    mags = np.zeros((len(image)//(patch_size-overlap), len(image[0])//(patch_size-overlap)), dtype = type([0.0]))
    airlight_dir = mags.copy()
    uncs = mags.copy()
    
    # Iterate through all patches within image
    for i in range(0, (len(image)//(patch_size-overlap))-1):
        for j in range(0, (len(image[0])//(patch_size-overlap))-2, 2):
            row = i*(patch_size-overlap)
            col = j*(patch_size-overlap)
        
            patch_one = image[row:row+patch_size, col:col+patch_size]
            patch_two = image[row:row+patch_size, col+overlap: col+patch_size+overlap]

            # Ignore patches which may have hard data to accurately fit
            if not too_white(patch_one) and not too_white(patch_two) and highly_variable(patch_one) and highly_variable(patch_two):
                # create lines of best fit for each patch, along with uncertainty in fit
                l1 = polyfit(patch_one)
                l2= polyfit(patch_two)

                # Calculate airlight direction for both patches
                A_hat = airlight_direction(l1, l2)
                #calculate magnitude of airlight individually
                a_1 = airlight_mag(l1, A_hat)
                a_2 = airlight_mag(l2, A_hat)
            
                # save all values for both patches in previously declared arrays
                mags[i][j] = a_1
                mags[i][j+1] = a_2
                airlight_dir[i][j] = A_hat
                airlight_dir[i][j+1] = A_hat
                uncs[i][j] = l1[2]
                uncs[i][j+1] = l2[2]
    
    return mags, airlight_dir, uncs
    


def polyfit(pixels: np.ndarray):
    """
    Uses Numpy polyfit to calculate a three dimensional line of best fit in rgb space for a patch of pixels
    Line is parameterized by z dimension (blue dimension)

    Args:
    pixels (np.ndarray): a singular patch of pixels sliced from initial image

    Returns: 
    List containing the following: 
        polyfit_x [slope (float), y-intercept (float)]: one dimensional line of best fit with z as dependent, x as independent variable
        polyfit_y [slope (float), y-intercept (float)]: one dimensional line of best fit with z as dependent, y as independent variable
        uncertainty (float): sum of uncertainty present in both fits 

    """
 
    pixels = pixels.reshape(patch_size**2, 3)
    polyfit_x, unc_x = np.polyfit(pixels[:][:,2], pixels[:][:,0], 1, cov = True)
    polyfit_y, unc_y = np.polyfit(pixels[:][:,2], pixels[:][:,1], 1, cov = True)
    unc = unc_x[0][0] + unc_y[0][0]
    return[polyfit_x, polyfit_y, unc]


def normalize(vec: list) -> list:
    """Given a list of three float numbers, normalizes the vector to a length of one
    
    Args: 
    vector (list[float]): a vector of three float numbers

    Returns: 
    norm_vector (list[float]): a vector of three float numbers, now normalized
    """
    l = np.sqrt(vec[0]**2 + vec[1]**2+vec[2]**2)
    return [vec[0]/l, vec[1]/l, vec[2]/l]




def airlight_direction(lobf_one, lobf_two):
    """
    Calculates direction of airlight between two patches as the vector in the direction that could most efficiently shift their
    lines of best fit to the origin

    Args: 
    lobf_one: (output from polyfit func) line of best fit for patch one
    lobf_two: (output from polyfit func) line of best fit for patch two

    Returns: 
    airlight_direction: (list[float]) Normalized vector describing direciton of airlight in image
    """

    #    choose two points along line of best fit
    z1 = 50
    z2 = 100

    # points on plane 1
    # calculate points on a plane that passes through the origin and patch one's line of best fit
    # these will be the points at z1 and z2
    pt1 = [z1*lobf_one[0][0] + lobf_one[0][1], z1*lobf_one[1][0] + lobf_one[1][1], z1]
    pt2 = [z2*lobf_one[0][0] + lobf_one[0][1], z2*lobf_one[1][0] + lobf_one[1][1], z1]
    # get normal vector to plane
    norm_one = np.cross(pt1, pt2)


    # points on plane 2
    # find the points on patch two's plane, and find its normal
    pt3 = [z1*lobf_two[0][0] + lobf_two[0][1], z1*lobf_two[1][0] + lobf_two[1][1], z2]
    pt4 = [z2*lobf_two[0][0] + lobf_two[0][1], z2*lobf_two[1][0] + lobf_two[1][1], z2]
    norm_two = np.cross(pt3, pt4)

    # By definition, planes must cross at origin, so we can find the vector perpendicular to both via cross product of their normals
    # this is the direction of airlight
    intersect = np.cross(norm_one, norm_two)
    return normalize(intersect)



def airlight_mag(lobf, A_dir):
    """Calculates the magnitude of airlight at a particular patch
    
    Args:
    lobf: (output of polyfit func) line of best fit for patch in question
    A_dir: (list[float]) airlight direction, output from airlight_direction function

    Returns: 
    mag: (float): scalar multiplier for A_dir vector describing how far line of best fit must be shifted to origin
    """

    # Test for what multiplier s will make line of best fit pass through origin when shifted by s*A_dir
    test_zs = range(-100,100,10)
    s = -255
    def avg_dist(s):
        xs = np.mean([np.abs((lobf[0][0]*z + lobf[0][1]) - s*A_dir[0]) for z in test_zs])
        ys = np.mean([np.abs((lobf[1][0]*z + lobf[1][1]) - s*A_dir[1]) for z in test_zs])
        zs = np.mean([np.abs(z - s*A_dir[2]) for z in test_zs])
        return (xs+ys+zs)/3
    curr_dist = avg_dist(s)
    new_dist = avg_dist(s+1)
    while new_dist<curr_dist:
        s+=3
        curr_dist = new_dist
        new_dist = avg_dist(s)

    return s


def get_brightness(pixel):
    """Returns average brightness across all three channels of one pixel
    
    Args: 
    pixel: (list[int_8]) vector describing brightnesses in three pixel channels

    Returns: 
    brightness: (float) value of all three channels averaged
    """
    return (int(pixel[0]) + int(pixel[1]) + int(pixel[2]))/3

def avg_brightness(patch):
    """Returns average brightness of a whole patch of pixels
    
    Args: 
    patch (np.ndarray): 2D array of pixels sliced from original image

    Returns:
    brightness (float): brightness of each pixel divided by number of pixels
    """
    patch = patch.reshape(patch_size**2, 3)
    patch = [get_brightness(pix) for pix in patch]
    return sum(patch) / len(patch)



def highly_variable(patch):
    """Function to evaluate viability of a patch - returns false if there isn't enough pixel variation to build an accurate line of best fit. 

    Args: 
    patch (np.ndarray): 2D array of pixels sliced from original image

    Returns:
    variable (boolean): True if patch has enough contrast variation, False otherwise

    """
    patch = patch.reshape(patch_size**2, 3)
    patch = [get_brightness(pix) for pix in patch]
    # The value of 20 is a fairly arbitrary threshhold for contrast, but seemed to work for my images - may be changed for better performance
    return np.max(patch)-np.min(patch)>20


def too_white(patch):
    """ Function to evaluate viability of a patch: returns False if the overall color is too close to the color of the airlight itself
    In this case, line of best fit correction may return wild values
        
    Args:
    patch (np.ndarray): 2D array of pixels sliced from original image

    Returns: 
    too_white (boolean): False if patch is too white, True otherwise
    """
    patch = patch.reshape(patch_size**2, 3)
    thresh = 135
    return np.max([np.abs(int(pix[0])-int(pix[1])) for pix in patch]) <thresh and np.max([np.abs(int(pix[0])-int(pix[2])) for pix in patch]) <thresh and avg_brightness(patch)>125 






# ============================================ Interpolation Functions ============================================


def interpolate(mags, airlight_dir, uncs):
    """
    Averages out airlight direction and magnitude to smooth outliers in image, make more realistically dehazed

    Args: 
    mags: (np.ndarray) 2D array of airlight magnitudes for all patches from find_dir_and_mags function
    airlight_dir: (np.ndarray) airlight directions array from find_dir_and_mags function
    uncs: (np.ndarray) line of best fit uncertainties from find_dir_and_mags function

    Returns: 
    mags: (np.ndarray) 2D array of airlight magnitudes for all patches
    airlight_dir: (np.ndarray) 2D array of airlight directions for all patches in image
    """
    # influences is a matrix where each entry describes the weight of influence that a pixel in the horizontal index has on a pixel in the vertical index
    # if there are memory issues, this may need to be declared separately and rewritten over - it is a very large matrix
    num_patches = (len(image)//(patch_size-overlap))* (len(image[0])//(patch_size-overlap))
    influences = np.zeros((num_patches, num_patches))

    # Assign all undefined patches average airlight direction and mag values - big uncertainty so they don't affect the otehr values
    avg_dir, avg_mag = find_airlight_avgs(airlight_dir, mags)
    for i in range(len(mags)):
        for j in range(len(mags[0])):
            if mags[i][j] == 0:
                mags[i][j] = avg_mag
                airlight_dir[i][j] = avg_dir
                uncs[i][j] = 1


    # Loop through all patches and calculate their influence on other patches in their radius
    row_len = len(mags[0])
    for i in range(len(mags)):
        for j in range(len(mags[0])):
            if uncs[i][j] != 1:
                min_i, max_i, min_j, max_j = find_range(i, j, len(mags), len(mags[0]))
            

                for k in range(min_i, max_i):
                    for l in range(min_j, max_j):
                        # calculate influence for each of these patches
                        dist = np.sqrt(np.abs(i-k)**2 + np.abs(j-l)**2)
                        influences[k*row_len+l][i*row_len+j] = influence(dist, uncs[i][j], uncs[k][l])
                        

            

    # Apply influences to the airlight dir, and airlight mag matrices
    mags_copy = mags.copy()
    airlight_dir_copy = airlight_dir.copy()
    for i in range(len(mags)):
        for j in range(len(mags[0])):
            min_i, max_i, min_j, max_j = find_range(i, j, len(mags), len(mags[0]))

            relevant_influences = []
            # because of the layout of the matrix, have to reconstruct which influences in a 1D format belong to which in a 2D format

            for num in np.where(influences[i*row_len+j] != 0):
                relevant_influences.append(influences[i*row_len+j][num])
            relevant_influences = relevant_influences[0]
           
            mag, dir = apply_influence(relevant_influences, airlight_dir_copy[min_i:max_i, min_j:max_j], mags_copy[min_i:max_i, min_j:max_j])
            if mag!= None:
                mags[i][j] = mag

            if dir!= None:
                airlight_dir[i][j] = dir

    return mags, airlight_dir



def influence(distance, self_unc, other_unc):
    """Based on distance between patches, and the uncertainty of each patch, calculate how much influence surrounding patch corrections should have in its final value. 
    
    Args: 
    distance (float): distance from the index of pixel one to pixel 2
    self_unc: (float) uncertainty of the pixel whose effect is being calculated
    other_unc: (float) uncertainty of the pixel who is having the effect on them calculated
    
    Returns:
    influence: (float) multiplier for how much of a given pixel's value will factor into the value of those surrounding it
    """
    weight = 10
    influence = (-weight/interpol_range**2)*distance + weight
    influence = influence + (1-self_unc) - (1-other_unc)
    return  influence

def find_airlight_avgs(airlight_dir, mags):
    """Finds the average airlight direction of an image
    
    Args: 
    airlight_dir: (np.ndarray) 2D array of all airlight directions in an image
    mags: (np.ndarray) 2D array of all airlight magnitudes for each patch in an image

    Returns:
    average_airlight_dir: (list[float]) vector of average value for each direction of the airlight direction
    average_airlight_mag: (float) average value across all magnitudes in the image
    """
    red_total = 0
    green_total = 0
    blue_total = 0
    mag_sum = 0
    size = 0
    for i in range(len(airlight_dir)):
        for j in range(len(airlight_dir[i])):
            if mags[i][j]!= 0:
                a = airlight_dir[i][j]
                red_total += (a[0])
                green_total += (a[1])
                blue_total += (a[2])
                mag_sum += mags[i][j]
                size+=1
    avg_airlight_dir = [red_total/size, green_total/size, blue_total/size]
    avg_airlight_mag = mag_sum/size
    return avg_airlight_dir, avg_airlight_mag


def add_vecs(vecs):
    """ Adds up a list of three dimensional vectors componen-wise
    
    Args: 
    vecs: (list[list[float]]) list of 3D vectors 

    Returns: 
    sum: (list[float]) vector consisting of the sum of each set of components 
    """
    sum = [0,0,0]
    for vec in vecs:
        sum[0] += vec[0]
        sum[1] += vec[1]
        sum[2] += vec[2]
    return sum

def scalar_divide_vec(vec, scal):
    """
    Performs scalar division on a three dimensional vector

    Args: 
    vec: (list[float]) 3D vector to be divided
    scal: scalar value to divide each component by

    Returns:
    quotient: (list[float]) vector with each component divided by scalar
    """
    return [vec[0]/scal, vec[1]/scal, vec[2]/scal]



def scalar_mult_vec(vec, scal):
    """
    Performs scalar multiplication on a 3D vector

    Args: 
    vec (list[float]): 3D vector to be multiplied
    scal: (float) scalar value to multiply each component by

    Returns:
    product: (list[float]) vector with each component multiplied by scalar
    """
    return [vec[0]*scal, vec[1]*scal, vec[2]*scal]




def apply_influence(influences, dirs, mags):
    """
    Given a set of magnitudes, directions and influences, iterates through patches in image, and applies a weighted average to direction and magnitude values (weighted by influence values)

    Args: 
    influences: (np.ndarray) 2D array of all pixel influences on each other
    dirs: (np.ndarray) 2D array of all airlight direction values in image
    mags: (np.ndarray) 2D array of all airlight magnitude values in image

    Returns: 
    mags: (np.ndarray) 2D array of all airlight magnitude values in image - now averaged
    dirs: (np.ndarray) 2D array of all airlight direction values in image - now averaged
    """
    dirs = dirs.reshape(len(dirs)*len(dirs[0]))
    mags = mags.reshape(len(mags)*len(mags[0]))
   
    if sum(influences) != 0:
        magnitude = np.sum([mags[i]*influences[i] for i in range(len(mags))])/((sum(influences))) 
    else:
        magnitude = None
    if sum(influences)!=0:
        direction = scalar_divide_vec(add_vecs([scalar_mult_vec(dirs[i],influences[i]) for i in range(len(dirs))]), (sum([np.abs(inf) for inf in influences])*len(dirs))) 
    else:
        direction = None
    return magnitude, direction


def find_range(i, j, l, h):
    """Returns the indeces that describe the bounds of interpolation values, accounting for image edges
    
    Args:
    i: (int) row index of current patch
    j: (int) column index of current patch
    l: (int) width of the image in patches
    h: (int) height of the image in patches

    Returns: 
    min_i: (int) index of patches in top row of influence
    max_i: (int) index of patches in bottowm row of influence
    min_j: (int) index of patches in left col of influence
    max_j: (int) index of patches in right col of influence
    """
    min_i = i-interpol_range if i-interpol_range>0 else 0
    max_i = i+interpol_range if i+interpol_range<l-1 else l-1
    min_j = j-interpol_range if j-interpol_range>0 else 0
    max_j = j+interpol_range if j+interpol_range<h-1 else h-1
    return min_i, max_i, min_j, max_j



# ======================================== Executing code and saving outputs to JSON =====================================

data = {}

a, A_hat, uncs = find_dir_and_mag(image)
# a, A_hat = interpolate(a, A_hat, uncs)

data["EOS_R100_JPG/jpg0006.jpg"] = [a, A_hat, uncs]


with open("haze_data.json", "w") as f:
    json.dump(data,f)


