library(xts)

dc <- read.csv("transactions.csv")
df <- as.data.frame(cbind(dc[,2],as.Date(dc[,5]),dc[,3]*dc[,4]))
names <- c("ID","Date","Value")
names(df) <- names
df[,2] <- as.Date(dc[,5])

for(p in sort(unique(df[,1]))) {
    na.omit(df[df$ID==1,])
}
