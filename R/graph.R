library(dplyr)
library(lubridate)
library(scales)
library(ggplot2)

set.seed(45)
df <- data.frame(x=rep(1:5, 9), val=sample(1:100, 45), 
                 variable=rep(paste0("category", 1:9), each=5))

library(readr)
complexities <- read_delim("~/work/complexity/data/complexities.txt", 
                           "\t", escape_double = FALSE, col_names = FALSE, 
                           col_types = cols(X1 = col_character()), 
                           trim_ws = TRUE)
colnames(complexities) <- c("lbl","month", "year", "name", "C1", "C2", "C3","C")

complexities$date <- as.Date(ymd(paste(complexities$year, complexities$month, 1)))

qc <- read_delim("~/work/complexity/data/q_complexities.txt", 
                           "\t", escape_double = FALSE, col_names = FALSE, 
                           col_types = cols(X1 = col_character()), 
                           trim_ws = TRUE)
colnames(qc) <- c("month", "year", "C1", "C2", "C3","C")

qc$date <- as.Date(ymd(paste(qc$year, qc$month, 1)))

p <- ggplot(data = qc, aes(x=date, y=C, group = 1)) +
  geom_line() + 
  geom_smooth() + 
  theme_minimal() +
  scale_y_continuous("Keerukus") +
  scale_x_date(date_breaks = "6 months", labels = date_format("%m-%Y"), date_minor_breaks = "1 months", name ="Kuu")+
  theme(axis.text.x = element_text(angle=90))
p
ggplot(data=complexities, aes(x=complexities$date, y=complexities$C)) + 
  geom_line(aes(colour=complexities$name)) + theme(legend.position="none") + scale_y_log10()

library(dplyr)
group_by(qc)

minmaks <- complexities %>% group_by(name) %>% summarise(i = min(C), x = max(C))
p <- ggplot(data = minmaks, aes(x=i, y=x)) + geom_point() + scale_y_log10()+ scale_x_log10()
p
minmaks$g <- minmaks$i/minmaks$x

ggplot(data = minmaks) + 
  aes(g) + 
  geom_histogram(aes(y=100*..count../sum(..count..))) + 
  theme_minimal()

mitu <- complexities %>% group_by(date) %>% summarise(mitu = n())
mitu %>% ggplot(aes(x = date, y=mitu)) + 
  geom_line() +
  scale_x_date(date_breaks = "6 months", labels = date_format("%m-%Y"), date_minor_breaks = "1 months", name ="Kuu") + 
  theme_minimal() +
  theme(axis.text.x = element_text(angle=90))
  
qc$nc1 <- (qc$C1-min(qc$C1))/max(qc$C1)
qc$nc2 <- (qc$C2-min(qc$C2))/max(qc$C2)
qc$nc3 <- (qc$C3-min(qc$C3))/max(qc$C3)
qc$nc <- (qc$C-min(qc$C))/max(qc$C)

qc %>% gather(type, value=)

qc %>% ggplot(aes(x=qc$date)) +
  geom_line(aes(y=qc$nc1)) + 
  geom_line(aes(y=qc$nc2)) + 
  geom_line(aes(y=qc$nc3)) + 
  geom_line(aes(y=qc$nc))
??gather()
summary(qc)


library(tidyr)


qc %>% 
  select(nc1, nc2, nc3, nc, date) %>% 
  gather(type,  value=cmpl, nc1, nc2, nc3, nc, -date) -> nqc
nqc %>%  ggplot(aes(x=date,y=nqc$cmpl, colour = nqc$type)) +
  geom_line()
nqc

qc %>% ggplot(aes(x=qc$date, y=qc$C2)) + geom_line()


mitu <- complexities %>% group_by(date) %>% summarise(mitu = sum(C))
mitu %>% ggplot(aes(x = date, y=mitu)) + 
  geom_line() +
  scale_x_date(date_breaks = "6 months", labels = date_format("%m-%Y"), date_minor_breaks = "1 months", name ="Kuu") + 
  theme_minimal() +
  theme(axis.text.x = element_text(angle=90))
glimpse(mitu)
