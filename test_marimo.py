import marimo

__generated_with = "0.23.6"
app = marimo.App()


@app.cell
def _():
    import h5py
    import skimage
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

    return (
        clear_border,
        closing,
        footprint_rectangle,
        io,
        measure,
        mpatches,
        np,
        plt,
        skimage,
        threshold_otsu,
    )


@app.cell
def _(io):
    # reading in my own image file

    test_img = io.imread("test_img.JPG")

    io.imshow(test_img)
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
def _():
    # compare to a couple blurrier versions, quantify the amount of distortion
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
    # Returns a copy of an image, cropped to a relevant region
    def crop_to_reg(region, img):
        minx, miny, maxx, maxy = region.bbox
        return img[minx:maxx, miny:maxy]

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
    """)
    return


if __name__ == "__main__":
    app.run()
