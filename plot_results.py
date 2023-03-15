import argparse
import matplotlib.pyplot as plt

from common import Result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Result plotter',
                    description='Plots results of ISO3DFD optimization')
    parser.add_argument("id", help="Trial ID", type=int)
    parser.add_argument("--plot", help="Set flag if you wish to plot the results", action="store_true")
    args = parser.parse_args()
    
    res = Result(args.id)
    res.print_summary()
    if args.plot:
        print("Plotting results")
        res.plot()
        plt.show()
