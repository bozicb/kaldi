# use rfm-analysis functions
source("rfm-analysis.R")
source("customers.R")

# import transactions
dc <- read.csv("transactions.csv")

# create data frame with customer_id, date, and value
df <- as.data.frame(cbind(dc[,1],dc[,5],dc[,3]*dc[,4]))
names <- c("ID","Date","Value")
names(df) <- names
df[,2] <- as.Date(dc[,5])

period <- 12*7

cdf <- getDailyCustomerData(df)

# set start and end dates and generate RFM scores
startDate <- min(cdf$Date)
endDate <- max(cdf$Date)

n <- ceiling(as.numeric(endDate-startDate)/period)
results <- list()

# generate independent scores
for(i in 1:n) {
    endDate <- startDate+period
    pdf <- getDataFrame(cdf,startDate,endDate)
    startDate <- endDate
    results[[i]] <- getIndependentScore(pdf)
}

# plot graphs with RFM score changes of customers
rscore <- data.frame()
fscore <- data.frame()
mscore <- data.frame()
for(customer in unique(cdf$ID)) {
    rscore[customer,"ID"] <- customer
    fscore[customer,"ID"] <- customer
    mscore[customer,"ID"] <- customer
    for(i in 1:n) {
        r <- results[[i]][results[[i]]$ID==customer,]$R_Score
        f <- results[[i]][results[[i]]$ID==customer,]$F_Score
        m <- results[[i]][results[[i]]$ID==customer,]$M_Score
        if(length(r)==0) r <- 0
        if(length(f)==0) f <- 0
        if(length(m)==0) m <- 0
        rscore[customer,paste("score",toString(i),sep="")] <-r
        fscore[customer,paste("score",toString(i),sep="")] <-f
        mscore[customer,paste("score",toString(i),sep="")] <-m
    }
}

# show customer distribution
#drawHistograms(df1)

# find customers with scores larger than 500 and 400
#S500<-df1[df1$Total_Score>500,]
#print(paste("Number of scores over 500:",toString(dim(S500)[1])))
#S400<-df1[df1$Total_Score>400,]
#print(paste("Number of scores over 400:",toString(dim(S400)[1])))

# show distributions for recency, frequency, and monetary
#par(mfrow=c(1,3))
#hist(df$Recency)
#hist(df$Frequency)
#hist(df$Monetary)

# set the Recency ranges in days
#r <- c(60,120,180,240)

# set the Frequency ranges in absolute orders
#f <- c(2,5,8,10)

# set the Monetary ranges in euro
#m <- c(10,20,30,100)

# show scores with breaks
#df2 <- getScoreWithBreaks(df,r,f,m)
#drawHistograms(df2)

# show customers with scores over 500 and 400
#S500 <- df2[df2$Total_Score>500,]
#print(paste("Number of scores over 500:",toString(dim(S500)[1])))
#S400<-df2[df2$Total_Score>400,]
#print(paste("Number of scores over 400:",toString(dim(S500)[1])))

