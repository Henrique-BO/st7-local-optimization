import argparse
import matplotlib.pyplot as plt

from common import Result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Result plotter',
                    description='Plots results of ISO3DFD optimization')
    parser.add_argument("id", help="Trial IDs", type=int, nargs="+")
    parser.add_argument("-plot", help="Plot on interactive screen", action="store_true")
    parser.add_argument("-fig", help="Save plot to file", type=str, nargs="?", const="img.png")
    parser.add_argument("-title", help="Plot title")
    parser.add_argument("-legend", help="Legend labels separated by spaces", nargs="+")
    args = parser.parse_args()
    
    for i in args.id:
        res = Result(i)
        res.print_summary()
        if args.plot or args.fig:
            title = args.title
            if args.legend != None and i < len(args.legend):
                label = args.legend[i]
            else:
                label = None
            res.plot(title, label)
    if args.fig != None:
        print("Saving to", args.fig)
        plt.savefig(args.fig)
    if args.plot:
        print("Plotting")
        plt.show()
