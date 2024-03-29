"""Solves a lab  4 exersice.

The perceptron is the first method of the LabSolver classself.

At the end of the script is the entry point.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


class LabSolver(object):
    """Able to solve a machine learning lab."""

    def __init__(self):
        """Initialize the object."""
        self.folds = 9
        self.model = None

        self.map_dict = {
          "Iris-setosa": 0,
          "Iris-versicolor": 1,
          "Iris-virginica": 0
        }

        self.criteria = [
            'accuracy',
            'precision',
            'recall',
            'fmeasure',
            'sensitivity',
            'specificity'
        ]

        self.results = []  # placeholder for the results.

        self.data = None
        self.data = self.get_data()
        self.prepare_data()

    def read_data(self):
        """Read data using the local  configuration module."""
        try:
            # if runs on student's local machine, try get the local file.
            from local_configuration import LocalConfiguration
            print ("Student's machine")

            configuration = LocalConfiguration()
            data = configuration.read_data()
        except:
            print ("Data not found locally, fetching...")
            # Else get file from an online resource.
            url_data = 'http://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data'
            # 2
            data = pd.read_csv(url_data, header=None).values

        return data

    def get_data(self):
        """Return the data. Fetch the data if needed."""
        if self.data is None:
            self.data = self.read_data()

        return self.data

    def prepare_data(self):
        """Format the data."""
        data = self.get_data()
        NumberOfPatterns, NumberOfAttributes = data.shape

        patterns = data[:, :4]
        # Make patterns float type.
        patterns = list(map(lambda x: np.float64(x), patterns))

        targets = np.zeros(NumberOfPatterns)

        for pattern in range(NumberOfPatterns):
            targets[pattern] = self.map_dict[data[pattern][4]]

        # Add 1 at the patterns.
        aces = np.ones([NumberOfPatterns, 1])
        self.patterns = patterns

        self.x = patterns  # p.hstack((patterns, aces))
        self.t = targets

    def get_fold(self, folds, x, t):
        """Slit the data and return a fold."""
        for k in range(folds):
            xtrain, xtest, ttrain, ttest = train_test_split(x, t,
                                                            test_size=0.1)
            fold = {
                'xtrain': xtrain,
                'xtest': xtest,
                'ttrain': ttrain,
                'ttest': ttest
            }

            yield fold

    def accuracy(self, metrics):
        """Calculate the accuracy.

        metrics (dict) has all needed metrics (tn, tp, fn, tp)
        """
        sum = metrics['tp'] + metrics['tn'] + metrics['fp'] + metrics['fn']
        if (sum == 0):
            return 0

        value = (metrics['tp'] + metrics['tn']) / sum
        return value

    def precision(self, metrics):
        """Calculate the precision.

        metrics (dict) has all needed metrics (tn, tp, fn, tp)
        """
        sum = metrics['tp'] + metrics['fp']
        if (sum == 0):
            return 0

        value = metrics['tp'] / sum
        return value

    def recall(self, metrics):
        """Calculate the recall.

        metrics (dict) has all needed metrics (tn, tp, fn, tp)
        """
        sum = metrics['tp'] + metrics['fn']

        if (sum == 0):
            return 0

        value = metrics['tp'] / sum
        return value

    def fmeasure(self, metrics):
        """Calculate the fmeasure.

        metrics (dict) has all needed metrics (tn, tp, fn, tp)
        """
        sum = self.precision(metrics) + self.recall(metrics)

        if (sum == 0):
            return 0

        value = (self.precision(metrics) * self.recall(metrics)) / (sum * 2)
        return value

    def sensitivity(self, metrics):
        """Calculate the specificity.

        metrics (dict) has all needed metrics (tn, tp, fn, tp)
        """
        sum = metrics['tp'] + metrics['fn']

        if (sum == 0):
            return 0

        value = metrics['tp'] / sum
        return value

    def specificity(self, metrics):
        """Calculate the specificity.

        metrics (dict) has all needed metrics (tn, tp, fn, tp)
        """
        sum = metrics['tn'] + metrics['fp']

        if (sum == 0):
            return 0

        value = metrics['tn'] / sum
        return value

    def cross_validation(self, NumberOfNeurons, solver):
        """Perform a cross validation test."""
        cross_validation = self.get_fold(self.folds, self.x, self.t)
        fold = next(cross_validation)
        fold_index = 0

        model = MLPClassifier(hidden_layer_sizes=[int(NumberOfNeurons)],
                              activation="logistic", solver=solver,
                              learning_rate="constant", max_iter=10000,
                              learning_rate_init=0.1, momentum=0.95)

        while (fold):
            try:
                model.fit(fold['xtrain'], fold['ttrain'])

                # test the model using the weights.
                patternScores = model.predict(fold['xtest'])

                # call the predict function
                determened_output = []
                for i in range(len(patternScores)):
                    current_score = self.predict(patternScores[i], 0.5)
                    determened_output.append(current_score)

                fold_results = {}
                # evaluate
                for criterion in self.criteria:
                    fold_results[criterion] = self.evaluate(fold['ttest'],
                                                            determened_output,
                                                            criterion)

                # save the results fot later calculations
                self.results.append(fold_results)

                # Add to plot
                global show_plot
                if show_plot:
                    fold_index += 1
                    self.add_to_plot(fold['ttest'], determened_output,
                                     fold_index)

                # Call next fold
                fold = next(cross_validation)
            except StopIteration:
                break

    def predict(self, value, threshold):
        """Decide at what class a pattern belong to."""
        if value < threshold:
            return 0

        return 1

    def evaluate(self, targets, predictions, criterion):
        """Evaluate the means of the basic metrics.

        targets (array): the real targets.
        predictions (array): the array with the claifier output.
        criterion (string): The criterion to be used.
        """
        if not any(list(map(lambda x: criterion == x, self.criteria))):
            raise Exception()

        tn = tp = fn = fp = 0

        for i in range(len(targets)):
            tn += (targets[i] == predictions[i]) and targets[i] == 0
            tp += (targets[i] == predictions[i]) and targets[i] == 1
            fn += (targets[i] != predictions[i]) and targets[i] == 1
            fp += (targets[i] != predictions[i]) and targets[i] == 0

        metrics = {
            'tn': tn,
            'tp': tp,
            'fn': fn,
            'fp': fp
        }

        calculated_values = {
            'accuracy': self.accuracy(metrics),
            'precision': self.precision(metrics),
            'recall': self.recall(metrics),
            'fmeasure': self.fmeasure(metrics),
            'sensitivity': self.sensitivity(metrics),
            'specificity': self.specificity(metrics)
        }

        return calculated_values[criterion]

    def calculate_means(self):
        """Calculate means for all criteria."""
        sums = {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'fmeasure': 0.0,
            'sensitivity': 0.0,
            'specificity': 0.0
        }

        for criterion in self.criteria:
            for fold in self.results:
                sums[criterion] += fold[criterion]

        means = {}
        for criterion in self.criteria:
            means[criterion] = sums[criterion] / 9

        self.means = means

    def show_means(self):
        """Show means."""
        if not self.means:
            print ("Means are not calculated yet.")
            return

        for criterion in self.criteria:
            print ("{}: {}".format(criterion, self.means[criterion]))

    def add_to_plot(self, targets, predictions, position):
        """Add a subplot of the fold to the plot.

        targets: The real targets
        predictions: The calculated outputs
        position: The position of the plot inside the grid.
        """
        plt.subplot(3, 3, position)
        plt.plot(targets, 'bo')
        plt.plot(predictions, 'r.')
        plt.title('fold ' + str(position + 1))

    def show_plot(self):
        """Show the plot."""
        plt.tight_layout()
        plt.show()

    def reset(self):
        """Reset the model results."""
        self.results = []


if __name__ == "__main__":

    global show_plot
    msg = "Show plots (for every solver/neurons combination) y/n[n]: "
    user_choice = input(msg)

    if user_choice == "y":
        show_plot = True
    else:
        show_plot = False

    # "sgd",
    solvers = ["sgd", "adam"]
    N1 = 5, 10, 20, 50, 100

    a = LabSolver()



    for solver in solvers:
        for n in N1:
            print ("\n\nSolver: {} - Neurons: {}".format(solver, n))
            print ("Training...")
            a.cross_validation(n, solver)
            print ("Calculate results...")
            a.calculate_means()
            a.show_means()

            if show_plot:
                a.show_plot()

            a.reset()
