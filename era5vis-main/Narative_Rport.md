# Jakob Werkgarner

**Assigned task**  
My task was to create the ERA5 cross-section plotting, including deviations (anomalies) from the climatological mean and plotting of the case file on pressure levels. I also added the call to my function in `cli.py` and made sure that `build_html.py` works correctly. In addition, I created the model climatology and the model topography from the ERA5 surface data. (The code is basically just resampling and computing the terrain height / g, so it is not included here.)

**Changes and outcome**  
During the implementation I added plotting routines for anomalies, climatological background fields, and terrain masking to improve readability. Wind arrows were implemented; although they are not used now, they can be used later on if the project is developed further. The rest basically went as planned, except that the output of the plotting function is not a Matplotlib figure anymore but now a path pointing to the created PNG for the HTML creation.

**Biggest challenge in implementation**  
The biggest challenge was finding a workflow that works with the files of the others. Different programming styles, mostly learned in a hands-on way, made the code inconsistent and harder to combine.

**Biggest challenge when merging**  
Since I followed Simon’s structure (especially for output handling), merging was not a major problem. However, after feedback, integrating `plot_crosssection` into `graphics.py` and separating helper functions caused some issues with shared variables and scripts called from the terminal, which required some debugging.
