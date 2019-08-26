import pandas as pd
import numpy as np
import pickle
import graphviz
from graphviz import Source
from sklearn import tree
from sklearn.metrics import precision_score, recall_score, f1_score,
                            confusion_matrix

# One hot encoding function for categorical data
def encode(df):
	feat_objs = [col for col in df if df[col].dtype == 'object']
	feat_encs = [pd.get_dummies(df[i], prefix=i) for i in feat_objs]

	for i in feat_encs:
		df_enc = df.join(i)
	
	for i in feat_objs:
		df_enc = df_enc.drop([i], axis=1)

	return df_enc

# Scorer for statistics about tree performance
def get_scores(tree_obj, X, y):
	fits = tree_obj.predict(X)
	prec = precision_score(y, fits)
	rec = recall_score(y, fits)
	f1 = f1_score(y, fits)
	res = confusion_matrix(y, fits)

	print("""\n\n\t\t\tModel Performance: \n
	         \t\t{}\n
		     \t\tPrecision: {}\n
		     \t\tRecall: {}\n
		     \t\tF1: {}\n""".format(res, prec, rec, f1))

	return res

# Create PDF
def graph_tree(tree_obj, feats, classes=['N', 'Y'], filename='tree.dot'):
	dot = Source(tree.export_graphviz(tree_obj, out_file=filename,
	             feature_names=feats, class_names=classes
				 filled = True))


# Extract text rules
def get_rules(tree_obj, feats):
	left      = tree_obj.tree_.children_left
	right     = tree_obj.tree_.children_right
	threshold = tree_obj.tree_.threshold
	features  = [feats[i] for i in tree.tree_.feature]

	# Child node ids
	idx = np.argwhere(left == -1)[:,0]

	def recurse(left, right, child, lineage=None):
		if lineage is None:
			lineage = [child]
		if child in left:
			parent = np.where(left == child)[0].item()
			split = '<='
		else:
			parent = np.where(right == child)[0].item()
			split = '>'

		lineage.append((parent, split, threshold[parent], features[parent]))
		# Alt version for if statements:
		# lineage.append(("IF", features[parent], split, threshold[parent]))

		if parent == 0:
			lineage.reverse()
			return lineage
		else:
			return recurse(left, right, parent, lineage)

	for child in idx:
		for node in recurse(left, right, child):
			print(node)
		print("Class values: ", tree.tree_.value[child])

		bal = tree.tree_.value[child][0][1] / np.sum(tree.tree_.value[child])
		print("Y balance: ", bal, "\n")


# Save model object
def save_tree_obj(tree_obj, name='tree.sav'):
	pickle.dump(tree_obj, open(name, 'wb')
	print('tree object saved as {}!'.format(name))
	
	# To reopen the object, use:
	# tree = pickle.load(open(fname, 'rb'))