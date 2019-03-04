# toy data
nrow = 10
ncol = 1000
# data as dataframe
d = matrix(rnorm(nrow*ncol), nrow, ncol)
d = as.data.frame(d)

set.seed(10) # fix letters names
d[,'geocode'] = sample(LETTERS, nrow)

# SUM ALL VALUES that are higher than a threshold.
threshold = 0.5

# OPTION 1: use apply
# x > threshold returns a logical vector, which is then sum up
vals.opt1 = apply(d[,1:360], 1, function(x) sum( x > threshold ) )

# OPTION 2: 
# select all columns expect 'geocode'
logical.matrix = d[,1:360] > threshold
vals.opt2 = rowSums(logical.matrix)

# COMMENT: option 2 is faster when the dimensions of data is too big