DOIcreator
==========

Create a DOI suffix for IANUS
 
It uses the module checkdigit.py to create the check digit. It uses the file datengeber.txt to look up the first three numbers or expand the list. It uses the file vergeben.txt to avoid duplicates

Form of Suffix:  
       xxx.xxxxxx-y <br \>
       \_/ \____/  \  
       /    |       \  
datengeber  random   check digit  

x is alphanumeric; y is numeric

prefix is 10.13149

See https://www.ianus-fdz.de/attachments/download/942/PID-TestbedErgebnisse.pdf for more information about PIDs and why and how IANUS uses DOIs.
