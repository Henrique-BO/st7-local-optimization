import argparse

from algorithms import SimulatedAnnealing, TabuSA, TunnelingSA, Greedy, ParallelGreedy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='ISO3DFD Optimizer',
                    description='Optimizer for ISO3DFD parameters')
    parser.add_argument("-a", "--algorithm", help="Algorithm to be used", type=str, required=True)
    parser.add_argument("-n1", help="n1 dimension in problem size", type=int, required=True)
    parser.add_argument("-n2", help="n2 dimension in problem size", type=int, required=True)
    parser.add_argument("-n3", help="n3 dimension in problem size", type=int, required=True)
    parser.add_argument("-k", help="Maximum number of iterations", type=int, required=True)

    parser.add_argument("-T0", help="Initial temperature for Simulated Annealing", type=float)
    parser.add_argument("-decay", help="Decay function for Simulated Annealing", type=str)
    parser.add_argument("-tabu", help="Tabu list size", type=int)
    parser.add_argument("-cost", help="Cost function for Tunneling", type=str)
    parser.add_argument("-Etunnel", help="Tunneling energy", type=float)

    parser.add_argument("Olevel", help="Initial Olevel", type=str)
    parser.add_argument("simd", help="Initial simd", type=str)
    parser.add_argument("NbTh", help="Initial number of threads", type=int)
    parser.add_argument("n1_thrd_block", help="Initial n1_thrd_block", type=int)
    parser.add_argument("n2_thrd_block", help="Initial n2_thrd_block", type=int)
    parser.add_argument("n3_thrd_block", help="Initial n3_thrd_block", type=int)
    
    args = parser.parse_args()

    S0 = [args.Olevel, args.simd, args.NbTh, args.n1_thrd_block, args.n2_thrd_block, args.n3_thrd_block]
    if args.algorithm == "ghc":
        algo = Greedy(args.n1, args.n2, args.n3, S0, args.k)
    elif args.algorithm == "pghc":
        algo = ParallelGreedy(args.n1, args.n2, args.n3, S0, args.k)
    elif args.algorithm == "sa":
        assert args.T0 != None and args.decay != None
        print(args.decay)
        algo = SimulatedAnnealing(args.n1, args.n2, args.n3, S0, args.k, args.T0, args.decay)
    elif args.algorithm == "tabu_sa":
        assert args.T0 != None and args.decay != None
        algo = TabuSA(args.n1, args.n2, args.n3, S0, args.k, args.T0, args.temp_decay, args.tabu)
    elif args.algorithm == "tunnel_sa":
        assert args.T0 != None and args.decay != None and args.cost != None and args.Etunnel != None
        algo = TunnelingSA(args.n1, args.n2, args.n3, S0, args.k, args.T0, args.temp_decay, args.cost, args.Etunnel)
    else:
        raise ValueError("Invalid algorithm")

    algo.optimize()
    algo.save()
