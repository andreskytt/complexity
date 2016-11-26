library(dplyr)

# Compute complexities for a given law
files <- list.files(path="~/work/python/complexity/data/test", pattern="l-.*.txt", full.names=T, recursive=FALSE)
complexities <- NULL
u <- NULL

lapply(files, function(x){
  # Read the file
  t <- read.csv(x, sep="\t", row.names = 1)  
  tm <- as.matrix(t)
  # Make sure we get both the links from A to B as well as B to A. Should yield a nice 
  # symmetrical matrix
  tmb <- tm + t(tm)
  
  # Set diagonal to zero
  diag(tmb) <- 0
  
  # Create a binary matrix
  A <- tmb
  A[A > 1] <-1
  
  B <- tmb
  
  # Extract the proper name for the file containing component complexities
  alpha <- sub("(.*)/l-(.*).txt","\\1/lc-\\2.txt", x)  
  date_label <- sub("(.*)/l-(.*)-(.*).txt","\\2", x)  
  act_id <- date_label <- sub("(.*)/l-(.*)-(.*).txt","\\3", x)
  
  tc <- read.csv(alpha, sep="\t", header = FALSE, col.names = c("section", "c")) 

  C1 <- sum(tc$c)
  C2 <- sum(rowSums(B)) 
  C3 <- sum(abs(eigen(A)$values))/ncol(A)
  C <- C1 + C2*C3
  
  # Extract the date label
  l <- sub("(.*)/l-(.*)-(.*).txt","\\2", x)
  m <- strtoi(sub("(.*)\\.(.*)\\.(.*)","\\2", l))
  y <- strtoi(sub("(.*)\\.(.*)\\.(.*)","\\3", l))
  
  complexities <<- rbind(complexities, c(l, m, y, act_id, C1, C2, C3, C))
})

colnames(complexities) <- c("lbl","month", "year", "act", "C1", "C2", "C3", "C")

cv <- as.data.frame(complexities)
cv <- cv[order(cv$year, cv$month),]

# Convert from factor
cv[,2] <- as.numeric(as.character(cv[,2]))
cv[,3] <- as.numeric(as.character(cv[,3]))
cv[,5] <- as.numeric(as.character(cv[,5]))
cv[,6] <- as.numeric(as.character(cv[,6]))
cv[,7] <- as.numeric(as.character(cv[,7]))
cv[,8] <- as.numeric(as.character(cv[,8]))


complexities
tm
x
ggplot(data = cv, aes(C)) + geom_histogram(bins= 90)
p

library(ggplot2)
library(dplyr)
?geom_histogram

mean(cv$C)

cv %>% 
  filter(C < 500 & year == 2002 & month == 10) %>%
  ggplot(aes(C3)) + 
  geom_histogram(bins = 590)

cv %>% filter(C3 == 0) %>% distinct(act)
glimpse(cv)

cv %>% group_by(lbl) %>% summarize(mC1 = mean(C1), mC2 = mean(C2), mC3 = mean(C3), mC = mean(C))
