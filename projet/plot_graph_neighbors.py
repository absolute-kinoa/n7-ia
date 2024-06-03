import numpy as np
import pandas as pd
from tqdm import tqdm
from dataclasses import dataclass
from swarm_sim import *
import networkx as nx
import random
from matplotlib.animation import FFMpegWriter

# Chemin vers le fichier source des donnes
PATH = './Traces.csv'
# Nombre de temps a analyser
MAXTEMPS = 100
# Constantes de distance
MAX_RANGE = 60000
MID_RANGE = 40000
MIN_RANGE = 20000

###
### Manipulation du fichier source.
###

print("### Importation des données ### ")
df = pd.read_csv(PATH, header=0)

print("### Reformatage des données : ajout d'un index sur le temps ### ")
#On genere un tableau qui servira d'index de temps pour chaque echantillon
names = ['1']
i=2
while len(names)<10000 :
  names.append(''+ str(i))
  i=i+1

#On modifie le df pour ajouter en tete de colone notre index de temps
save = df.columns
df.columns = names
df.loc[-1] = save
df.index = df.index + 1 
df = df.sort_index()
print("### Reformatage des données : ajout d'un index sur les satelites ### ")
# On genere les noms des satelite 
satnames = ['satx1']
i=1
while len(satnames)<300 :
  if (i !=1):
    satnames.append('satx'+ str(i))
  satnames.append('saty'+ str(i))
  satnames.append('satz'+ str(i))
  i=i+1
# On applique notre index
df['coords'] = satnames
df = df.set_index('coords', drop=True)

# On transpose notre df pour avoir le temps en ligne et les coordonees de satelites en colonnes
dft = df.transpose()


###
### Mise en forme de la donnee en memoire (Creation des structures de donnees necessaires)
###

# On itère sur les elements de notre df pour en extraire des Node comme implantes dans swarm_sim
def GetNodes(time):
  nodes = {}
  id = 1
  while id < 101:
    node = Node(id - 1, dft.loc[str(time)]['satx'+str(id)], dft.loc[str(time)]['saty'+str(id)], dft.loc[str(time)]['satz'+str(id)])
    nodes[id - 1] = node
    id = id +1
  return nodes  

# Cette fonction permet, a partir du swarm, d'extraire une matrice d'adjaceance qui prend en compte le cout des differents liens.
def GetWeightedMatrix(Swarm):
  # On prend comme base le reseau avec une portee minimale puis on vient ajouter les chemins necessitant plus de portee en multipliant par un coefficient.
  matrix20 = Swarm.neighbor_matrix(MIN_RANGE)
  matrix40 = Swarm.neighbor_matrix(MID_RANGE)
  matrix60 = Swarm.neighbor_matrix(MAX_RANGE)
  x=0
  y=0 
  while x < len(matrix20) :
    y=0
    while y < len(matrix20):
      if (matrix20[x][y] == 0 and matrix40[x][y] == 1) :
        matrix20[x][y]=2
      if (matrix20[x][y] == 0 and matrix40[x][y] == 0 and matrix60[x][y] == 1):
        matrix20[x][y]=3 
      y=y+1
    x=x+1
  return matrix20

def CreateNeighbors(Swarm, Range=MAX_RANGE):
  for t in range(len(Swarm)):
    matrix = Swarm[t].neighbor_matrix(Range)
    # print(len(matrix))
    for i in range(int(np.floor(len(matrix)/2))):
      for j in range(int(np.floor(len(matrix)/2))):
        if (matrix[i][j]>0):
          node_i = Swarm[t].get_node_by_id(i)
          node_j = Swarm[t].get_node_by_id(j)

          node_i.add_neighbor(node_j)
          node_j.add_neighbor(node_i)


print("### Génération des tableaux de nodes en fonction du temps ### ")
def GetPositions(): 
  Positions = {}
  temps = 0
  while temps < MAXTEMPS:
    Positions[temps] = GetNodes(temps+1)
    temps = temps+1
  return Positions
Positions = GetPositions()

print("### Génération des swarms correspondants a chaque instants ###")
def InitSwarms(Positions):
  Swarms = {}
  temps = 0
  while temps < MAXTEMPS:
    Swarms[temps] = Swarm(MAX_RANGE, list(Positions[temps].values()))
    temps = temps+1
  return Swarms

chosen_range=MAX_RANGE
Swarms = InitSwarms(Positions)
CreateNeighbors(Swarms, chosen_range)


print("=============================")
print("Showcasing Neighbor Graph")
print("=============================")

# Animation setup
# metadata = dict(title='Swarm Evolution', artist='Eric YU')
# writer = FFMpegWriter(fps=10, metadata=metadata)

# Initialize lists to store maximum coordinates

# x_list = []
# y_list = []
# z_list = []

# for i in range(len(Swarms)):
#   for n in Swarms[i].nodes:
#     x_list.append(n.x)
#     y_list.append(n.y)
#     z_list.append(n.z)

# x_max = np.max(x_list)
# y_max = np.max(y_list)
# z_max = np.max(z_list)
# x_min = np.min(x_list)
# y_min = np.min(y_list)
# z_min = np.min(z_list)


# Placeholder for generating swarm data over time (this should be replaced with your actual data)

fig = plt.figure(figsize=(20,20))
ax0=Swarms[0].plot_edges(fig,221,time=0, range=chosen_range)
ax1=Swarms[int(MAXTEMPS/2)].plot_edges(fig, 222,time=50, range=chosen_range)
ax3=Swarms[MAXTEMPS-1].plot_edges(fig, 212,time=99, range=chosen_range)
plt.show()

# Generating random positions for the sake of demonstration
# with writer.saving(fig, "swarm_connectivity_evolution.mp4", MAXTEMPS):
#     for i in range(len(Swarms)):
#         nodes = []
#         print(i)
#         nodes = Swarms[i].nodes
#         x_data = [node.x for node in nodes]
#         y_data = [node.y for node in nodes]
#         z_data = [node.z for node in nodes]
        
#         # Settings limits to the graph
#         # ax.set_xlim(x_min,x_max)
#         # ax.set_ylim(y_min,y_max)
#         # ax.set_zlim(z_min,z_max)

#         # Plot the grapb
#         ax.scatter(x_data, y_data, z_data, c="blue", s=50)
#         ax.plot([0,0],[0, 0],[0, 0], color='red', markersize=50000) # Origin
#         for node in nodes:
#             for n in node.neighbors:
#                 if n in nodes:
#                     ax.plot([node.x, n.x], [node.y, n.y], [node.z, n.z], c="grey")
#         plt.show()
#         writer.grab_frame()
#         ax.clear()
#         plt.cla()

# print("Animation created and saved as 'swarm_evolution.mp4'")
# print("=============================")

