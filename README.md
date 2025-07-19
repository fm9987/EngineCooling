This github repository is in attempt to make an electron  
app to run rocket simulations using a .csv file to  
define the shape of the engine with the first column as the   
location across the engine, and the second as r which is   
the distance from the center.
The updates that have been done from version 1 of the app are:
 - Help Button
 - Color change of simulation
 - Input of .csv file
 - Getting python to run
 - Data input
 - UI cleanup
 - Live data review
 - Python "simulation" that generates data from x and r in input file
 - Save output.csv file in same directory as input file

TO DO:
- Implement Regen cooling simulation 
- Implement film cooling simulation
- Make error messages display into the error section on the app (especially python outputs)


Publish changes:
git add .  
git commit -m "Comment"  
git push -u origin main  