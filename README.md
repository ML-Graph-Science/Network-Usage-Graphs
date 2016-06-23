# Network-Usage-Graphs
Code plots network bandwidth for the nersc endpoint for 1 day. 

Code does the following:
-	Identity the N busiest days for which the nersc endpoint had the highest number of transfers occur in the globus log
-	Then for each of these N busiest days:
  -	Plot the network traffic over the course of the day for all of the transfers that occurred on that day (X Axis = Time of Day, Y Axis = MiB/s) to establish a baseline. 
  -	Randomly divide the transfers into 2 groups (X and Y) and make another plot using these 2 groups
  -	X Group – transfers with hard constraints, and so these transfers start at the time requested in the original logs. 
  -	Y Group – best-effort transfers (ASAP). Each transfer was randomly assigned a ‘price’ or max network bandwidth that the transfer could start at. To simulate these transfers, the transfer duration and transfer rate remained the same, but if the network bandwidth exceeded the transfer ‘price’ at the requested start time, then the transfer start time and end time were delayed until the next time the network bandwidth dropped below the transfer ‘price’
  -	Then the code outputs a plot that has the original network bandwidth over the course of the day and the modified network bandwidth generated using the X and Y groups. 

The hope is to reduce network bandwidth peaks by delaying some of the non-critical transfers during the busiest times until the network bandwidth goes down. 

I’ve uploaded generated graphs of the 10 busiest days for the nersc endpoint to google drive so you can see.
https://drive.google.com/folderview?id=0B4wQroU0fOkpaEtVWWhZOFZsOVk&usp=sharing 

The blue line plots the original network bandwidth, and the red line plots the modified network bandwidth. 
I expected the original data to be more consistent, with higher network demand during the middle of the day and less at night. However, the data appears to vary quite a bit by the day and so that causes the results to also vary. Furthermore, these results are dependent on a number of different variables in my code that could be tweaked to modify the results.

These variables include: 
-	Percentage of transfers in X vs Y groups (currently 50% and 50%)
-	The min price range for the prices assigned to the Y transfers (currently min price value is (Max Network Bandwidth in original data – Min Network bandwidth) * 0.05 + Min Network Bandwidth )
-	The max price range for the prices assigned to the Y transfers (currently max price value is (Max Network Bandwidth in original data – Min Network bandwidth) * 0.6 + Min Network Bandwidth )
-	How the prices are randomly generated for the Y transfers (currently prices are generated using a normal distribution with a mean and standard deviation equal to the mean and standard deviation of the original network traffic for the day, and prices outside of the min and max price ranges are removed).
