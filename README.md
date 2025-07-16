This github repository is in attempt to make an electron  
app to run rocket simulations using a .csv file to  
define the shape of the engine with the first column as the   
location across the engine, and the second as r which is   
the distance from the center.

To add changes use this sequence:  

git add .  
git commit -m "Comment"  
git push -u origin main  

TO DO:

- Choose what data to display for the Regen Sim
- Make error messages display into the error section on the app
- Make the slider change the color of the corresponding point in the engine 
- Implement Regen cooling simulation 
- Make data be written into a json file
- Use data from json to assign variables to sim
- Implement film cooling simulation