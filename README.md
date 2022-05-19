# CLV-package
In ourder to make this package work, it is enough to have everything in one folder, but sometimes the file called "clv.py" 
needs to be uploaded into jupyter notebook to make it work. The package does several functions connected to CLV(Customer lifetime value). The first 
function after importing clv, is best_model(), which finds the best model by calaculating AIC and finding the one which has smallest AIC score.
The second function is calc_CLV which calculates clv based on the best model found. Third function vis_CLV, which visualizes CLV. And the last function
hyp_test(data, "gender"), which in this conducts hypothesis testing based on gender.
File testtt.ipynb can be opened to see the example.
