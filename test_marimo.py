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

    return io, np, plt, skimage


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


@app.cell
def _(plt, skimage, test_img):
    # crop to black section
    black_n_white = skimage.color.rgb2gray(test_img)
    # contours = measure.find_contours(black_n_white)

    fig, ax = plt.subplots()
    ax.imshow(black_n_white, cmap = "gray")

    # for contour in contours:
    #     ax.plot(contour[:,1], contour[:,0], linewidth = 2)


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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
