library(dplyr)

# Compute complexities for a set of laws
files <- list.files(path="~/work/python/complexity/data/results", pattern="x.*.txt", full.names=T, recursive=FALSE)
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
  
# Normalize the interface complexities
  #  
  # Actually, no
  B <- tmb
  
# Extract the proper name for the file containing component complexities
  alpha <- sub("(.*)/x-(.*).txt","\\1/a-\\2.txt", x)  
  date_label <- sub("(.*)/x-(.*).txt","\\2", x)  
  
  tc <- read.csv(alpha, sep=" ", header = FALSE, col.names = c("act", "c")) 
  #colnames(tc) <- c("act", date_label)
# Normalize the component complexities
  # t$c <- t$c/max(t$c)
  # Actually, let's not do that
  #t$c <- t$c

  if(is.null(u)){
    print("u is null")
    u <<- tc
  }
  else{
    u <<- full_join(x = u, y = tc, by="act")  
  }
  
  
  C1 <- sum(tc$c)
  C2 <- sum(rowSums(B)) 
  C3 <- sum(abs(eigen(A)$values))/ncol(A)
  C <- C1 + C2*C3
  
# Extract the date label
  m <- strtoi(sub("(.*)/x-(.*)-(.*).txt","\\2", x))
  y <- strtoi(sub("(.*)/x-(.*)-(.*).txt","\\3", x))
  l <- sub("(.*)/x-(.*).txt","\\2", x)
  complexities <<- rbind(complexities, c(l, m, y, C1, C2, C3, C))
})

colnames(complexities) <- c("lbl","month", "year", "C1", "C2", "C3", "C")

cv <- as.data.frame(complexities)
cv <- cv[order(cv$year, cv$month),]

# Convert from factor
cv[,2] <- as.numeric(as.character(cv[,2]))
cv[,3] <- as.numeric(as.character(cv[,3]))
cv[,4] <- as.numeric(as.character(cv[,4]))
cv[,5] <- as.numeric(as.character(cv[,5]))
cv[,6] <- as.numeric(as.character(cv[,6]))
cv[,7] <- as.numeric(as.character(cv[,7]))

library(lubridate)
library(scales)
library(ggplot2)
cv$date <- as.Date(ymd(paste(cv$year, cv$month, 1)))

p <- ggplot(data = cv, aes(x=date, y=C, group = 1)) +
  geom_line() + 
  theme_minimal() +
  #scale_y_continuous("Keerukus", labels = seq(150, 800, 50), breaks = seq(150, 800, 50)) +
  scale_y_continuous("Keerukus") +
  scale_x_date(date_breaks = "6 months", labels = date_format("%m-%Y"), date_minor_breaks = "1 months", name = "Kvartal")+
  theme(axis.text.x = element_text(angle=90)) +
  geom_smooth()
  
p


# Routine end
t <- read.csv("/Users/andreskytt/work/python/complexity/data/results/x-10-2002.txt", sep="\t", row.names = 1)
cv
complexities[order((year-2002)*12+month)]
complexities[order(year),]

cv <- as.data.frame(complexities)
cv <- cv[order(cv$year),]
complexities
cv
complexities

cv[,2] <- as.numeric(as.character(cv[,2]))
cv[,3] <- as.numeric(as.character(cv[,3]))
cv[,4] <- as.numeric(as.character(cv[,4]))
cv[,5] <- as.numeric(as.character(cv[,5]))
cv[,6] <- as.numeric(as.character(cv[,6]))
cv[,7] <- as.numeric(as.character(cv[,7]))

library(dplyr)
cvo <- cv %>% mutate(o = (year-2002)*12 + month)
cv

library(ggplot2)
p <- ggplot(data = cvo, aes(x=o, y=C, group = 1)) +
  geom_line() + 
  theme_minimal() +
  #scale_y_discrete("Keerukus", labels = seq(150, 320, 20), breaks = seq(150, 320, 20)) +
  #scale_y_continuous(breaks = c(2,5,8), labels = c("two", "five", "eight"))
  #scale_x_discrete("Kuu ja aasta", labels = cvo$lbl, breaks=cvo$lbl) +
  theme(axis.text.x = element_text(angle=90))
p

class(cvo$o)
seq(150, 310, 10)

andmed <- data.frame(a=c(1,2,3), b=c(1,2,3), c=c("X", "Y", "Z"))

ggplot(andmed, aes(x=a, y=b))+
  geom_line()+
  scale_y_continuous(breaks=andmed$b, labels=andmed$c)

library(ggplot2)
library(lubridate)
library(scales)
cvo$date <- ymd(paste(cvo$year, cvo$month, 1))
cvo$date <- as.Date(cvo$date)

p <- ggplot(data = cvo, aes(x=date, y=C, group = 1)) +
  geom_line() + 
  theme_minimal() +
  scale_y_discrete("Keerukus", labels = seq(170, 800, 20), breaks = seq(170, 800, 20)) +
  scale_x_date(date_breaks = "3 months", labels = date_format("%m-%Y"), date_minor_breaks = "1 months")+
  theme(axis.text.x = element_text(angle=90))
p

cvo
p <- ggplot(data = cvo, aes(x=date, y=C, group = 1)) +
  geom_line() + 
  theme_minimal() +
  scale_y_discrete("Keerukus", labels = seq(170, 500, 20), breaks = seq(170, 500, 20)) +
  scale_x_date(date_breaks = "3 months", labels = date_format("%m-%Y"), date_minor_breaks = "1 months")+
  theme(axis.text.x = element_text(angle=90))
p

glimpse(cvo)
ggsave(p, filename='/Users/andreskytt/Desktop/complexity.png', height=6, width=8, scale=1)

write.csv(cv, file="~/complexity.csv")
?write.csv

cv
glimpse(cv)

p <- ggplot(data = cv, aes(x=date, y=C, group = 1)) +
  geom_line() + 
  theme_minimal() +
  scale_y_continuous("Keerukus") +
  scale_x_date(date_breaks = "6 months", labels = date_format("%m-%Y"), date_minor_breaks = "1 months")+
  theme(axis.text.x = element_text(angle=90))

p

glimpse(u)
