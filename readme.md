# 2Classify

The system only classify 2 category

# Usage

* cm = CategoryManager()
* cm.trainSystem("train_data.csv")
* cm.loadModel("train.csv")
* cm.classifyText('He lived and worked primarily in Washington D.C. and the Washington Post described her as a force in the Washington Color School')
* cm.classifyMany('test_dp3.csv', 2, 0, 'test_dp3_r.csv')
* cm.classifyMany('test_dp6.csv', 2, 0, 'test_dp6_r.csv')

Here train_data.csv is the training data as DBPedia format. After completing the training it will store model data into train.csv
So We need to laod this model by loadModel("train.csv").

For Single text classification we can use classifyText() and for multipe data at a same time we can use: classifyMany('test_dp3.csv', 2, 0, 'test_dp3_r.csv')
Here test_dp3.csv is also provided for testing as DBPedia data. The test_dp3_r.csv is the output file after getting the result.
Here for testing cm.classifyMany('test_dp3.csv', 2, 0, 'test_dp3_r.csv') The value 2 means which column value will be used for checking and 0 means which column value will be displayed in result file.

For Example:
"3",52,48,"Artist","Transport"
Means Artist -> 52, Transport-> 48 and category is given to display is 3


*classes.csv

Artist
Transport
X

*ignore_category_words.csv

Which keywords will be ignored during training and predictions.

Like 0,for in file meand 'for' will be ignored for both category. But if we write this..<1,for> then it will be ignored only for category 1.
Also if we write <2,for> then it will be ignored only for category 2.

# Accuracy

* Between 94% ~98%

# Get help

Email: saiful_vonair@yahoo.com
