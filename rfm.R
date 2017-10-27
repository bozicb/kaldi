# import transactions
dc <- read.csv("transactions.csv")

# create data frame with customer_id, date, and value
df <- as.data.frame(cbind(df[,1],as.Date(df[,5]),df[,3]*df[,4]))
names <- c("ID","Date","Value")
names(df) <- names
df[,2] <- as.Date(df[,5])

# set start and end dates and generate RFM scores
startDate <- as.Date("20160911","%Y%m%d")
endDate <- as.Date("20170620","%Y%m%d")
df <- getDataFrame(df,startDate,endDate)

# generate independent scores
df1 <- getIndependentScore(df)

# show customer distribution
drawHistograms(df1)

# find customers with scores larger than 500 and 400
S500<-df1[df1$Total_Score>500,]
dim(S500)
S400<-df1[df1$Total_Score>400,]
dim(S400)

# show distributions for recency, frequency, and monetary
par(mfrow=c(1,3))
hist(df$Recency)
hist(df$Frequency)
hist(df$Monetary)

# set the Recency ranges in days
r <- c(60,120,180,240)

# set the Frequency ranges in absolute orders
f <- c(2,5,8,10)

# set the Monetary ranges in euro
m <- c(10,20,30,100)

# show scores with breaks
df2 <- getScoresWithBreaks(df,r,f,m)
drawHistograms(df2)

# show customers with scores over 500 and 400
S500 <- df2[df2$Total_Score>500,]
dim(S500)
S400<-df2[df2$Total_Score>400,]
dim(S400)

