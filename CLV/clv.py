from lifelines import WeibullAFTFitter, LogNormalAFTFitter, LogLogisticAFTFitter, CoxPHFitter


def prep_data(filename):

	"""This function takes path to excel file and filename as a string and converts the 
	categorical columns to integer values, and returns the modified dataframe."""

	from pandas import read_excel
	
	df = read_excel(filename, index_col=0)

	df["marital"].replace({"Married": 1, "Unmarried": 0}, inplace=True)
	df["retire"].replace({"Yes": 1, "No": 0}, inplace=True)
	df["gender"].replace({"Male": 0, "Female": 1}, inplace=True)
	df["voice"].replace({"Yes": 1, "No": 0}, inplace=True)
	df["internet"].replace({"Yes": 1, "No": 0}, inplace=True)
	df["forward"].replace({"Yes": 1, "No": 0}, inplace=True)
	df["churn"].replace({"Yes": 1, "No": 0}, inplace=True)
	df["ed"].replace({"Post-undergraduate degree": 4, "College degree": 3,
					  "Some college": 2, "High school degree": 1,
					  "Did not complete high school": 0}, inplace=True)
	df["region"].replace({"Zone 3": 2, "Zone 2": 1, "Zone 1": 0}, inplace=True)
	df["custcat"].replace({"Total service": 3, "Plus service": 2, "E-service": 1,
						  "Basic service": 0}, inplace=True)
						  
	return df
	
def best_model(df, duration="tenure", event="churn"):

	"""This function takes, following arguments: 
	
	1. df: DataFrame
	2. duration: Name of column to be set as duration as string (optional)
	3. event: Name of column to be set as event as string (optional)
	
	Then it compares the AIC values of 4 models/fitters:
	
	1. WeibullAFTFitter()
	2. LogNormalAFTFitter()
	3. LogLogisticAFTFitter()
	4. CoxPHFitter()
	5. ExponentialFitter()
	
	And returns the model with the least AIC score."""

	fitters = [WeibullAFTFitter(), LogNormalAFTFitter(), LogLogisticAFTFitter(), CoxPHFitter()]
	
	leastAIC = float('inf')
	for fitter in fitters:
		fitter.fit(df, duration_col=duration, event_col=event)
		try:
			aic = fitter.AIC_
		except:
			aic = fitter.AIC_partial_
		
		if  aic < leastAIC:
			leastAIC = aic
			leastfitter = fitter
	return leastfitter

def calc_CLV(df, duration="tenure", event="churn"):

	"""This function takes, following arguments: 
	
	1. df: DataFrame
	2. duration: Name of column to be set as duration as string (optional)
	3. event: Name of column to be set as event as string (optional)
	
	Then returns the predicted survival function."""

	fitter = best_model(df, duration, event)
	fitter.fit(df, duration_col=duration, event_col=event)
	pred = fitter.predict_survival_function(df)
	pred = pred.iloc[0:24,0:5]
	
	MM = 1300
	r = 0.1

	for i in range(1, 6):
		for index, row in pred.iterrows():
		    row[i] = row[i] / pow((1 + r/12),i-1)
	
	pred['CLV'] = MM * pred.sum(axis = 1)
	return pred['CLV'].describe()
	
def vis_CLV(df, compare, duration="tenure", event="churn"):

	"""This function takes, following arguments: 
	
	1. df: DataFrame
	2. comare: Name of the column to view the partial effects on outcome
	3. duration: Name of column to be set as duration as string (optional)
	4. event: Name of column to be set as event as string (optional)
	
	Then plot tow graphs:
	
	1. Plot the cooeffitients and ranges
	2. Plot the effects on outcome graph"""

	from matplotlib.pyplot import figure, show, close
	
	if compare == "age":
		value = range(20, 80, 5)
	elif compare == "address":
		value = range(0, 55, 5)
	elif compare == "income":
		value = range(0, 1670, 50)
	else:
		value = range(min(df[compare]), max(df[compare])+1)
	
	fitter = best_model(df, duration, event)
	fitter.fit(df, duration_col=duration, event_col=event)
	figure(figsize=(10,5))
	fitter.plot()
	show()
	close()
	figure(figsize=(20,10))
	fitter.plot_partial_effects_on_outcome(compare, value)
	show()
	close()
	
def hyp_test(df, compare, alpha=None, duration="tenure", event="churn"):

	"""This function takes, following arguments: 
	
	1. df: DataFrame
	2. comare: Name of the column to view the partial effects on outcome
	3. alpha: The value of alpha (optional)
	4. duration: Name of column to be set as duration as string (optional)
	5. event: Name of column to be set as event as string (optional)
	
	Then prints weather the hypothesis based on a column can be rejected or not
	after comparing it with the p-value of that column obtained from the best model."""

	fitter = best_model(df, duration, event)
	fitter.fit(df, duration_col=duration, event_col=event)
	
	if alpha == None:
		alpha = fitter.alpha
	
	p = fitter.summary["p"]["mu_"][compare]
	
	if p < alpha:
		print("Reject Null Hypothesis")
	else:
		print("Null Hypothesis can't be rejected")
	
def hyp_test_segment(df, compare, alpha=None, duration="tenure", event="churn"):
	
	"""This function takes, following arguments: 
	
	1. df: DataFrame
	2. comare: Name of the column to view the partial effects on outcome
	3. alpha: The value of alpha (optional)
	4. duration: Name of column to be set as duration as string (optional)
	5. event: Name of column to be set as event as string (optional)
	
	Then check all the unique values of columns having categorical data and prints
	the name of columns and the values whose hypothesis can be rejected, if none
	can be rejected	then the function says so."""
	
	import warnings
	warnings.filterwarnings("ignore")
	
	fitter = best_model(df, duration, event)
	
	n = False
	for i in df.columns:
		if len(df[i].unique())<= 10 and i != "retire":
			for j in df[i].unique():
				try:
					temp = df[df[i] == j] 
					fitter.fit(temp, duration_col=duration, event_col=event)

					if alpha == None:
						alpha = fitter.alpha
					p = fitter.summary["p"]["mu_"][compare]

					if type(p) == 'numpy.float64':
						if p < alpha:
							n = True
							print("Reject Null Hypothesis for", i, j)
				except:
					pass
	if n == False:
		print("Null Hypothesis not rejected for any segment")
	
	
	
	
	
	
