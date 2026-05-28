import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import matplotlib.pyplot as plt
    import numpy as np

    return np, plt


@app.cell
def _(np, plt):
    func = lambda x: x**3/5
    plt.plot(np.linspace(-5,5), [func(x) for x in np.linspace(-5,5)])
    return


if __name__ == "__main__":
    app.run()
