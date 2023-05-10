# fabreeze
A cloth simulator that uses Verlet integration to simulate a piece of cloth as a lattice
of points connected by strings.

![image](https://github.com/daveseo901/fabreeze/assets/55063490/98fe595f-902e-4e3d-8fc9-4cd0c347ae1d)

To run, execute `python main.py` in the command line (this project uses Python 3).

To change the dimensions of the cloth, edit the `rows` and `cols` variables in `main.py`.

Hold left-click on points to drag them around. Right-click on points to toggle their fixedness.

Inspired by Josephbakulikira's work in this repository:

https://github.com/Josephbakulikira/Cloth-Simulation-With-python---Verlet-Integration

Some ideas also drawn from this YouTube video:

https://www.youtube.com/watch?v=zISvAW1QzJA&ab_channel=DaFluffyPotato

Definition of Verlet integration taken from this Wikipedia article:

https://en.wikipedia.org/wiki/Verlet_integration
