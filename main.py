import argparse

from algorithms import Greedy, ParallelGreedy, SimulatedAnnealing, TabuSA, TunnelingSA, LAHC

if __name__ == "__main__":
    # CLI arguments
    parser = argparse.ArgumentParser(
                    prog='ISO3DFD Optimizer',
                    description='Optimize the ISO3DFD parameters (Olevel, SIMD, NbTh, n2_thrd_block, n2_thrd_block, n3_thrd_block)\
                                 using the chosen algorithm',
                    )

    # Positional arguments
    algo_list = ["ghc", "pghc", "sa", "tabu_sa", "tunnel_sa", "lahc"]
    parser.add_argument("algo", choices=algo_list, help="Algorithm to use in optimization", type=str)
    
    # Optional arguments
    parser.add_argument("-n", help="Problem size separated by spaces", type=int, default=[256, 256, 256], 
                        nargs=3, metavar=("n1","n2","n3"))
    parser.add_argument("-k", help="Maximum number of iterations", type=int, default=200)
    parser.add_argument("-S0", help="Initial solution", nargs=6, 
                        metavar=("Olevel","simd","NbTh","n1_thrd_block","n2_thrd_block","n3_thrd_block"))
    parser.add_argument("-T0", help="Initial temperature for Simulated Annealing", type=float, default=100)
    parser.add_argument("-decay", help="Decay function for Simulated Annealing", type=str, default="geometric")
    parser.add_argument("-tabu", help="Tabu list size", type=int, default=5)
    parser.add_argument("-cost", help="Cost function for Tunneling", type=str, default="stochastic")
    parser.add_argument("-Etunnel", help="Tunneling energy", type=float, default=0.0)
    parser.add_argument("-Lh", help="List size for LAHC", type=int, default=10)
    
    # Parse arguments
    args = parser.parse_args()
    n1, n2, n3 = args.n
    if args.S0 == None:
        S0 = ["Ofast", "avx512", 32, n1, 4, 4]
    else:
        S0 = args.S0
        for i in range(3,7):
            S0[i] = int(S0[i])

    # Identify and initialize chosen algorithm
    if args.algo == "ghc":
        algo = Greedy(n1, n2, n3, S0, args.k)

    elif args.algo == "pghc":
        algo = ParallelGreedy(n1, n2, n3, S0, args.k)
    
    elif args.algo == "sa":
        algo = SimulatedAnnealing(n1, n2, n3, S0, args.k, args.T0, args.decay)
    
    elif args.algo == "tabu_sa":
        algo = TabuSA(n1, n2, n3, S0, args.k, args.T0, args.temp_decay, args.tabu)
    
    elif args.algo == "tunnel_sa":
        algo = TunnelingSA(n1, n2, n3, S0, args.k, args.T0, args.temp_decay, args.cost, args.Etunnel)
    
    elif args.algo == "lahc":
        algo = LAHC(n1, n2, n3, S0, args.k, args.Lh)
    
    else:
        raise ValueError("Invalid algorithm")

    # Run and save optimization trial
    algo.optimize()
    algo.save()
