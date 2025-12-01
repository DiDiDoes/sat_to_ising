import argparse
import neal
from pysat.formula import CNF
import time
from tqdm import tqdm

from cnf_to_bqm import cnf_to_bqm

parser = argparse.ArgumentParser()
parser.add_argument("--num-instance", "-n", type=int, default=100)
parser.add_argument("--num-sweeps", "-s", type=int, default=100)
parser.add_argument("--num-reads", "-r", type=int, default=10)
args = parser.parse_args()

print(f"Running Neal on {args.num_instance} instances with {args.num_sweeps} sweeps and {args.num_reads} reads each.")
f_out = open(f"results/neal_{args.num_instance}_{args.num_sweeps}_{args.num_reads}.csv", "w")
f_out.write(
    "index,dataset,sat,"
    "cnf_variable,cnf_clause,"
    "ancillae,bqm_variable,bqm_interaction,"
    "neal_energy,neal_time,"
    "\n"
)
for dataset in ["sr", "3-sat", "ca", "k-clique", "k-domset", "k-vercov"]:
    solved = 0
    for i in tqdm(range(args.num_instance), desc=f"Dataset {dataset}"):
        cnf = CNF(from_file=f"/home/chengdicao/data/mas_sat/{dataset}/easy/train/sat/{i:05d}.cnf")
        bqm, ancillae = cnf_to_bqm(cnf)

        neal_sampler = neal.SimulatedAnnealingSampler()
        neal_start = time.time()
        neal_sampleset = neal_sampler.sample(
            bqm,
            num_sweeps=args.num_sweeps,
            num_reads=args.num_reads,
        )
        neal_end = time.time()

        f_out.write(
            f"{i},{dataset},1,"
            f"{cnf.nv},{len(cnf.clauses)},"
            f"{len(ancillae)},{bqm.num_variables},{bqm.num_interactions},"
            f"{neal_sampleset.first.energy},{neal_end - neal_start},"
            "\n"
        )
        if neal_sampleset.first.energy == 0:
            solved += 1
    print(f"Dataset {dataset}: Neal solved {solved}/{args.num_instance}")

f_out.close()