# Tools for observing

## Predict times of quadratures

Supply a list of objects in a file with the format:

```sh
target_id  epoch  period  t14
```

see ```ephems.txt``` for an example. Then run the script as follows
to predict a list of quadratures over a range of nights for a given
observatory:

```sh
python calculate_quad_times.py ephems.txt 2019-04-10 2019-04-17 lasilla
```

This produces a list of quadrature times for each object separately,
then a combined chronologically ordered list for the entire run.
The quads are only listed if they occur with the Sun below an altitude 
of -14 degrees.

### Usage

```sh
▶ python calculate_quad_times.py -h                          
usage: calculate_quad_times.py [-h] infile n1 n2 observatory 
                                                              
positional arguments:                                         
  infile       path to file containing objects                
  n1           night 1                                        
  n2           night 2                                        
  observatory  Astropy name of observatory                    
                                                              
optional arguments:                                           
  -h, --help   show this help message and exit                
```

### To do:

   1. Add moon separation calculations
