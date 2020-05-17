import init
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.risk_models import fix_nonpositive_semidefinite

dataTable = None # The raw input from file, contains the whole data table.
exp_return = None
cov_matrix = None # The covariance matrix
corr_matrix = None # The correlation coefficient matrix
assetsList = None # in the Same order in summary file
asset_to_num = None # a dictionary for the reverse index of assetsList


if __name__ == "__main__":

    # Step1: get expected return and cov matrix from data
    # This step will takes about 10-20s
    dataTable, summaryTable = init.read_CSV()
    assetsList, asset_to_num = init.getAssetsList()
    init.preprocess()
    exp_return = init.calcExpectedReturn_1()
    cov_matrix, corr_matrix = init.calcCovMatrix()

    # Step2: ...

    # Step3:
    cov_matrix = fix_nonpositive_semidefinite(cov_matrix)

    ef = EfficientFrontier(exp_return, cov_matrix)
    raw_weights = ef.max_sharpe(risk_free_rate=0.008674) #shibor O/N 2020-05-15
    cleaned_weights = ef.clean_weights()
    ef.save_weights_to_file("weights.csv")
    print(cleaned_weights)
    ef.portfolio_performance(verbose=True)