import dimod
from pysat.formula import CNF


def cnf_to_bqm(
        cnf: CNF,
        clause_panelty: float = 1.0,
        auxilary_penalty: float = 10.0,
    ) -> dimod.BinaryQuadraticModel:

    bqm = dimod.BinaryQuadraticModel(dimod.BINARY)
    ancillae = []

    for clause in cnf.clauses:
        # Each term is represented as (order, weight, [list of variables])
        terms = [[0, clause_panelty, []]]
        for literal in clause:
            variable = abs(literal)
            if literal < 0:
                # Negated variable, multiply existing terms by x
                for term in terms:
                    term[0] += 1
                    term[2].append(variable)
            else:
                # Positive variable, multiply existing terms by (1 - x)
                new_terms = [
                    [term[0] + 1, -term[1], term[2] + [variable]] for term in terms
                ]
                terms.extend(new_terms)
        while len(terms) > 0:
            order, weight, variables = terms.pop(0)
            if order == 0:
                bqm.offset += weight
            elif order == 1:
                bqm.add_linear(variables[0], weight)
            elif order == 2:
                bqm.add_quadratic(variables[0], variables[1], weight)
            else:
                # For higher-order terms, introduce auxiliary variables z = xy
                # And add penalty terms xy - 2(xz + yz) + 3z
                ancilla = (variables[0], variables[1])
                if ancilla not in ancillae:
                    ancillae.append(ancilla)
                    bqm.add_quadratic(variables[0], variables[1], auxilary_penalty)
                    bqm.add_quadratic(variables[0], ancilla, -2 * auxilary_penalty)
                    bqm.add_quadratic(variables[1], ancilla, -2 * auxilary_penalty)
                    bqm.add_linear(ancilla, 3 * auxilary_penalty)
                terms.append([order - 1, weight, variables[2:] + [ancilla]])

    return bqm, ancillae

if __name__ == "__main__":
    cnf = CNF(from_file="example_sat.cnf")
    print(f"CNF has {cnf.nv} variables and {len(cnf.clauses)} clauses.")

    # Convert the CNF to a BQM
    bqm, ancillae = cnf_to_bqm(cnf)
    print(f"Introduced {len(ancillae)} auxiliary variables.")
    print(f"BQM has {bqm.num_variables} variables and {bqm.num_interactions} interactions.")

    # Sample from the BQM using different samplers

    import neal
    sampler = neal.SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm)
    print(sampleset.first.energy)

    import tabu
    sampler = tabu.TabuSampler()
    sampleset = sampler.sample(bqm)
    print(sampleset.first.energy)
