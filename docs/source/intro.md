# Intro

Illustris is a **huge** suite of simulations with the moving mesh code, [`AREPO`](https://arepo-code.org/). Illustris applies the FoF and `Subfind` algorithms to identify halos/subhalos and store particles accordingly. Therefore, we can easily load a subset of particles belonging to the same halo/subhalo. This method works for most cases but still fails when 
1. two halos largely overlap, 
2. there are too many "fuzz" particles which don't belong to any halo, 
3. we want to trace the evolution of a particle, but it "jumps" to another halo at some time, etc.

Therefore, we develope the `mesh_illustris` toolkit to enable loading Illustris like mesh-based simulations. `mesh_illustris` splits the entire volume into a 3D mesh and index each particle/cell according to its location in the mesh. This method allows us to **quickly** load a subset (e.g., a box or sphere) of particles/cells with **minimal** amount of memory.