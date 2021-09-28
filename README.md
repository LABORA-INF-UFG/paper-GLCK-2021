# Optimal joint functional split and network functionplacement in virtualized RAN with splittable flows

## Description
This repository aims to demonstrate the Multi-path functional Split and network function placement in virtualized RAN (*MuSt-RAN*) model implementation. We tested in Ubuntu Server 18.04 and Ubuntu 20.04, with Python 3.6.9, docplex 2.20.204 for implement the optimization model and IBM CPLEX version 12.8.0.

- [Topologies](#topologies)
- [Paths](#paths)
- [Splittable Flows](#splittable-flows)
- [Final Results](#final-results)

## Topologies

In this work, we used two different types of topologies named as T1 and T2. The T1 topology is a ring based topology with two CRs positioned close to the Core in a centralized way, and the others 23 CRs are distributed as a ring based cluster where each one has an Radio Unit (RU). 

The T2 topology is a hierarchical topology with two CRs positioned close to the Core. The others 23 CRs are distributed in layers that respect an hierarchy. Each one of those 23 CRs has an RU.

In both topologies the CRs are free to allocate different amounts of Virtualized Network Functions (VNF).  In other words, they are free to act as a Core Unite (CU) or/and a Distributed Unit (DU). Also, the numbers of CUs or DUs are dynamic, i. e., there is no fixed number of CUs or DUs in our model. 

![topo_fig](https://github.com/LABORA-INF-UFG/paper-GLCK-2021/blob/main/figure_topology.png)

## Paths

To calculate the routing paths of the topologies we used the k-shortest path algorithm. This algorithm are used to calculate a set of paths that will be used by the optimization model to solve the problem. Each path can be used with different configurations of allocation points, given that the paths reaches a set of CRs. In this case, we consider all the configurations available. 

## Splittable Flows

In this work, we consider the flow split between the VNFs to reach better results to the Radio Access Network (RAN). With flow split we are capable to optimize the network data flow and the network resources usage. Also, the flow split strategy can improve the centralization level and the positioning of VNFs, i. e., improve the RAN quality and CRs usage. The improvements of using splittable flows are discussed with more details in the article.

![flow_split_fig](https://github.com/LABORA-INF-UFG/paper-GLCK-2021/blob/main/git%20flow%20split.png)

## Final Results

To see the final results, i. e., the optimal solution of each topology and/or the improvements of each scenario, we provide a set of charts that can be used to compare the optimal solutions of three different approaches. The scripts and solutions used to plot those charts are available in this repository.
