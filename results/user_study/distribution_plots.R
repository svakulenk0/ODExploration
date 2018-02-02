# http://www.r-tutor.com/r-introduction/data-frame
# http://www.cookbook-r.com/Graphs/Plotting_distributions_(ggplot2)/

# todo boxplots
n_turns_simulation1 = c(5, 5, 5, 5, 5, 5, 5, 5, 6, 7, 7, 7, 7, 7, 7) 
n_turns_users1 = c(4, 5, 5, 6, 6, 7, 8, 9, 10, 11, 20) 
n_turns_simulation2 = c(5, 8, 8, 9, 9, 9, 9) 
n_turns_users2 = c(5, 7, 14, 19, 21, 21, 24, 56) 

z <- c('n_turns_simulation1', 'n_turns_users1', 'n_turns_simulation2', 'n_turns_users2')
dataList <- lapply(z, get, envir=environment())
names(dataList) <- c("Simulation", "User study", "Simulation", "User study")
boxplot(dataList, ylab="Number of turns", xlab="Search task 1                                                       Search task 2")

# todo histograms
n_correct_search1 = c(0, 0, 0, 0, 0, 0, 0, 0, 0.067, 0.2, 0.4, 0.4) 
n_correct_browse1 = c(0.067, 0.067, 0.067, 0.067, 0.067, 0.0672, 0.13, 0.2, 0.2, 0.2, 0.4, 1)
n_correct_search2 = c(0,0,0,0,0,0,0,0,0,0,0,0.14) 
n_correct_browse2 = c(0,0,0,0,0,0,0,0,0.14, 0.14, 0.14, 0.71)

n_correct_search1 = c(0, 0, 0, 0, 0, 0, 0, 0, 6.7, 20, 40, 40) 
n_correct_browse1 = c(6.7, 6.7, 6.7, 6.7, 6.7, 6.7, 13, 20, 20, 20, 40, 100)
n_correct_search2 = c(0,0,0,0,0,0,0,0,0,0,0,14) 
n_correct_browse2 = c(0,0,0,0,0,0,0,0,14, 14, 14, 71)

df <- data.frame(n_correct_search1, n_correct_browse1, n_correct_search2, n_correct_browse2)
colnames(df) <- c("Search", "Browse", "Search", "Browse")
boxplot(df, ylab="Recall", xlab="Search task 1                                                       Search task 2")

# build data frame for the histograms
require(reshape2)
df <- melt(data.frame(n_correct_search1, n_correct_browse1, n_correct_search2, n_correct_browse2))
x_name <- "cond"
y_name <- "rating"
colnames(df) <- c(x_name, y_name)

#x <- table(df)
#barplot(x, col=c("darkblue","red"), beside=TRUE)

library(ggplot2)


# Interleaved histograms
ggplot(df, aes(x=rating, fill=cond)) +
  geom_histogram(binwidth=.5, position="dodge")

# Density plots
ggplot(df, aes(x=rating, colour=cond, group =cond)) + geom_line(aes(linetype=cond,colour=cond),stat="density") + xlim(0, 1)

# + geom_density() 


