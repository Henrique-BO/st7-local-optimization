import argparse
import matplotlib.pyplot as plt

from common import Result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Result plotter',
                    description='Plots results of ISO3DFD optimization')
    parser.add_argument("id", help="Trial IDs", type=int, nargs="+")
    parser.add_argument("--plot", help="Set flag if you wish to plot the results", action="store_true")
    args = parser.parse_args()
    
    print(args.id)
    for i in args.id:
        res = Result(i)
        res.print_summary()
        if args.plot:
            res.plot()
    if args.plot:
        plt.savefig("img.png")
