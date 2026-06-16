import marimo

__generated_with = "0.23.9"
app = marimo.App()


@app.cell
def _():
    # import h5py
    from skimage import io
    from skimage import measure
    import matplotlib.pyplot as plt
    import os
    import numpy as np
    from skimage.filters import threshold_otsu
    from skimage.segmentation import clear_border
    from skimage.morphology import closing, footprint_rectangle
    from skimage.color import label2rgb
    import matplotlib.patches as mpatches
    from PIL import Image, ImageStat

    return (
        Image,
        ImageStat,
        clear_border,
        closing,
        footprint_rectangle,
        io,
        measure,
        mpatches,
        np,
        plt,
        threshold_otsu,
    )


@app.cell
def _(io):
    # reading in my own image file

    test_img = io.imread("test_img.JPG")
    raw_test = io.imread("EOS_R100\\IMG_0004.CR3")

    io.imshow(raw_test)
    io.show()
    return (test_img,)


@app.cell
def _(test_img):
    # still has original resolution
    print(len(test_img))
    print(len(test_img[0]))
    area = len(test_img)*len(test_img[0])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ***
    """)
    return


@app.cell
def _(plt, skimage, test_img):
    # crop to black section
    black_n_white = skimage.color.rgb2gray(test_img)
    # contours = measure.find_contours(black_n_white)

    fig, ax = plt.subplots()
    ax.imshow(black_n_white, cmap = "gray")


    plt.show()
    return (black_n_white,)


@app.cell
def _(black_n_white, np):
    # find percentage that is white/close to white
    def brightness_percent(img, threshhold):
        bright_pixels = np.where(img>threshhold, img, 0)
        bright_pixels = np.count_nonzero(bright_pixels)
        area = len(img) * len(img[0])
        return bright_pixels/area

    print(f"Percentage of whole image: {brightness_percent(black_n_white, 0.75)}%")

    cropped = black_n_white[600:3500, 1100:5000]

    print(f"Percentage when cropped: {brightness_percent(cropped, 0.75)}%")
    return


@app.cell
def _(black_n_white, np, plt):
    # histogram of brightnesses in image to see where to cut off white space
    plt.hist(np.ndarray.flatten(black_n_white), bins = 50)
    plt.vlines(0.75, 0,2e6, "red", linestyles = "dashed")
    plt.show()
    return


@app.cell
def _(plt):
    # compare to a couple blurrier versions, quantify the amount of distortion
    print(max(plt.hist([0,0,0,2,2,2,2,2,2,5,5])[0]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ***
    """)
    return


@app.cell
def _(
    clear_border,
    closing,
    footprint_rectangle,
    measure,
    mpatches,
    threshold_otsu,
):
    # Returns a copy of an image, cropped to a relevant region or list of points
    def crop_to_reg(region, img):
        if type(region) == list:
            minx, miny, maxx, maxy = region
        else:
            minx, miny, maxx, maxy = region.bbox
        return img[minx:maxx, miny:maxy]


    # ================== I skipped all of these ones, should figure out which will be needed =======================

    # returns label regions from a  black and white image
    def label_img(img, ftprnt):
        threshhold = threshold_otsu(img)
        bw = closing(img>threshhold, footprint_rectangle((ftprnt, ftprnt)))
        cleared = clear_border(bw)
        labels = measure.label(cleared)
        regions = measure.regionprops(labels)
        return regions

    # returns a list of significant regions
    def significant_reg(regions, size):
        regs = []
        for region in regions:
            if region.area>=size:
                regs.append(region)

        return regs

    # draws borders on significant regions
    def borders(sig_regions, ax):
        for region in sig_regions:
            minx, miny, maxx, maxy = region.bbox
            rect = mpatches.Rectangle(
                (miny, minx), 
                maxy-miny,
                maxx-minx,
                fill = False,
                edgecolor = "red",
                linewidth = 2,
            )
            ax.add_patch(rect)


    return borders, crop_to_reg, label_img, significant_reg


@app.cell
def _(black_n_white, borders, crop_to_reg, label_img, plt, significant_reg):
    # An attempt at labelling parts of the image
    # If only I had the data to attempt to classify it as well

    regions = label_img(black_n_white, 5)
    fig_1, ax_1 = plt.subplots(1,2, figsize = (10, 6))
    ax_1[0].imshow(black_n_white, cmap = "gray")
    sig_regions = significant_reg(regions, 10000)
    borders(sig_regions, ax_1[0])
    ax_1[1].imshow(crop_to_reg(sig_regions[0], black_n_white), cmap = "gray")


    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    From here, should be able to run the cropped areas of interest through an ML classification algorithm. Can save the classifications with the image, to have data on shunt numbers, other defect numbers and such. This is mainly for identifying defect type with ML, which I'm not sure if its worth it, given I'm still not sure what I'm doing exactly, but... It's cool at least!

    ***
    """)
    return


@app.cell
def _(Image, ImageStat, black_n_white):
    # Function to calculate average brightness of an image 
    # For use in comparing optical patterns, 

    # this one uses PIL Images
    def avg_brightness_PIL(img_path):
        img = Image.open(img_path)
        img = img.convert("L")
        return ImageStat.Stat(img).mean[0]/256

    # This one is just the skimage np array image
    def avg_brightness(img):
        return sum([sum(i) for i in img])/ (len(img)*len(img[0]))


    print(avg_brightness_PIL("test_img.JPG"))
    print(avg_brightness(black_n_white))
    return (avg_brightness,)


@app.cell
def _(avg_brightness, black_n_white, crop_to_reg, np, plt):
    # Taking two points on the image and calculating their average brightness


    # takes in the coordinates of the top left corner and width of box one and box two -> returns two cropped images of 
    def select_regions(point1, width1, img1, point2, width2, img2):
        return (crop_to_reg([point1[0], point1[1], point1[0]+width1, point1[1]+width1], img1), crop_to_reg([point2[0], point2[1], point2[0]+width2, point2[1]+width2], img2))

    # calculates the difference in brightness between two given regions (cropped np array images) - 0 is no contrast, 1 is max contrast
    def calc_contrast(regs):
        return np.abs(avg_brightness(regs[0]) - avg_brightness(regs[1]))


    # adds correct scaling to heatmap of image so that it will display in the correct
    def scale_heatmap(reg):
        reg[0][0] = 1
        reg[0][1] = 0
        return reg

    # displays two regions side by side, third argument controls whether the displayed images are scaled to actual darkness or not
    def display_regs(regs, corrected):
        fig_2, ax_2 = plt.subplots(1,2)
        # This I think needs to be a dereferenced pointer but I don't have the energy rn
        reg1, reg2 = regs
        if corrected:
            reg1 = scale_heatmap(regs[0])
            reg2 = scale_heatmap(regs[1])
        ax_2[0].imshow(reg1, cmap = "gray")
        ax_2[1].imshow(reg2, cmap = "gray")
        plt.show()


    regs = select_regions((0,0), 1000, black_n_white, (2000,2000), 1000, black_n_white)
    display_regs(regs, True)
    print(calc_contrast(regs))


    # transmittance can build off of this, but it's just the image with the mask divided by the image with the light
    # can just use an all white square to test it with the image here
    return display_regs, select_regions


@app.cell
def _(avg_brightness, black_n_white, display_regs, np, select_regions):
    # calculates the amount of light transmitted through a device based on the brightness of the light source and the brightness shining through the 
    # sample (crop to relevant areas)
    # REGIONS [0] SHOULD BE THE LIGHT SOURCE, AND [1] SHOULD BE THE MASKED IMAGE
    import select
    def calc_transmittance(regs):
        return avg_brightness(regs[1]) / avg_brightness(regs[0])


    light_source = np.ones((4000,6000))

    regs_t = select_regions((0,0), 100, light_source, (2500,100), 100, black_n_white )
    display_regs(regs_t, True)

    print(calc_transmittance((regs_t[0], regs_t[1])))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell
def _(io):
    tif = io.imread("EOS_R100/IMG_0004.tif")
    io.imshow(tif)
    return


if __name__ == "__main__":
    app.run()
