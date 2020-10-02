import numpy as np
import pandas as pd
# Import the linear regression class
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


# Sklearn also has a helper that makes it easy to do cross validation
from sklearn.cross_validation import KFold
from sklearn import cross_validation

#Print you can execute arbitrary python code
titanic = pd.read_csv("../input/train.csv", dtype={"Age": np.float64}, )
titanic_test = pd.read_csv("../input/test.csv", dtype={"Age": np.float64}, )

#Print to standard output, and see the results in the "log" section below after running your script
print("\n\nTop of the training data:")
print(titanic.head())

print("\n\nSummary statistics of training data")
print(titanic.describe())

#Any files you save will be available in the output tab below
#titanic.to_csv('copy_of_the_training_data.csv', index=False)

titanic["Age"] = titanic["Age"].fillna(titanic["Age"].median())

# Replace all the occurences of male with the number 0.
titanic.loc[titanic["Sex"] == "male", "Sex"] = 0
titanic.loc[titanic["Sex"] == "female", "Sex"] = 1

# Find all the unique values for "Embarked".
print(titanic["Embarked"].unique())

titanic["Embarked"] = titanic["Embarked"].fillna('S')

titanic.loc[titanic["Embarked"] == 'S', "Embarked"] = 0
titanic.loc[titanic["Embarked"] == 'C', "Embarked"] = 1
titanic.loc[titanic["Embarked"] == 'Q', "Embarked"] = 2



# The columns we'll use to predict the target
predictors = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]

# Initialize our algorithm class
alg = LinearRegression()
# Generate cross validation folds for the titanic dataset.  It return the row indices corresponding to train and test.
# We set random_state to ensure we get the same splits every time we run this.
kf = KFold(titanic.shape[0], n_folds=3, random_state=1)

predictions = []
for train, test in kf:
    # The predictors we're using the train the algorithm.  Note how we only take the rows in the train folds.
    train_predictors = (titanic[predictors].iloc[train,:])
    # The target we're using to train the algorithm.
    train_target = titanic["Survived"].iloc[train]
    # Training the algorithm using the predictors and target.
    alg.fit(train_predictors, train_target)
    # We can now make predictions on the test fold
    test_predictions = alg.predict(titanic[predictors].iloc[test,:])
    predictions.append(test_predictions)
    
    
# Initialize our algorithm
alg = LogisticRegression(random_state=1)
# Compute the accuracy score for all the cross validation folds.  (much simpler than what we did before!)
scores = cross_validation.cross_val_score(alg, titanic[predictors], titanic["Survived"], cv=3)
# Take the mean of the scores (because we have one for each fold)
print(scores.mean())

titanic_test["Age"] = titanic_test["Age"].fillna(titanic["Age"].median())

titanic_test.loc[titanic_test["Sex"] == 'male', "Sex"] = 0
titanic_test.loc[titanic_test["Sex"] == 'female', "Sex"] = 1

titanic_test["Embarked"] = titanic_test["Embarked"].fillna('S')

titanic_test.loc[titanic_test["Embarked"] == 'S', "Embarked"] = 0
titanic_test.loc[titanic_test["Embarked"] == 'C', "Embarked"] = 1
titanic_test.loc[titanic_test["Embarked"] == 'Q', "Embarked"] = 2

titanic_test["Fare"] = titanic_test["Fare"].fillna(titanic["Fare"].median())

# Initialize the algorithm class
#alg = LogisticRegression(random_state=1)

# Train the algorithm using all the training data
#alg.fit(titanic[predictors], titanic["Survived"])
predictors = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
alg = RandomForestClassifier(random_state=1, n_estimators=150, min_samples_split=4, min_samples_leaf=2)
scores = cross_validation.cross_val_score(alg, titanic[predictors], titanic["Survived"], cv=3)
print(scores.mean())

# Make predictions using the test set.
#predictions = alg.predict(titanic_test[predictors])

#full_predictions = []
#for alg, predictors in algorithms:
# Fit the algorithm using the full training data.
alg.fit(titanic[predictors], titanic["Survived"])
# Predict using the test dataset.  We have to convert all the columns to floats to avoid an error.
predictions = alg.predict_proba(titanic_test[predictors].astype(float))[:,1]
#full_predictions.append(predictions)

# The gradient boosting classifier generates better predictions, so we weight it higher.
#predictions = (full_predictions[0] * 3 + full_predictions[1]) / 4

predictions[predictions <= .5] = 0
predictions[predictions > .5] = 1
predictions = predictions.astype(int)

# Create a new dataframe with only the columns Kaggle wants from the dataset.
submission = pd.DataFrame({
        "PassengerId": titanic_test["PassengerId"],
        "Survived": predictions
    })
    
submission.to_csv("kaggle.csv", index=False)