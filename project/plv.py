import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns

from kuramoto import Kuramoto

sns.set_style("whitegrid")

# Instantiate a random graph and transform into an adjacency matrix
graph_nx = nx.erdos_renyi_graph(n=10, p=1) # p=1 -> all-to-all connectivity
graph = nx.to_numpy_array(graph_nx)

for i in {0.01,0.1,1,5,10,50}:
    # Instantiate model with parameters
    model = Kuramoto(coupling=i, dt=0.01, T=10, n_nodes=len(graph))
    # Run simulation
    act_mat = model.run(adj_mat=graph)
    plt.plot([Kuramoto.phase_coherence(vec) for vec in act_mat.T], label=i)
plt.xlabel("Time")
plt.ylabel("PLV/S")
plt.title("10 oscillators phase coherence for different coupling strengths")
plt.legend()
plt.show()






